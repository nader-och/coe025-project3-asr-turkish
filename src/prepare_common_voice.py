"""Part 1 - Data: build speaker-separated train / validation / test manifests for Common Voice Turkish.

Default (--split-mode official): use the documented Common Voice train.tsv / dev.tsv / test.tsv.
We check ourselves that no speaker (client_id) appears in two splits.
Alternative (--split-mode grouped): group validated.tsv by speaker and assign whole speakers
to train / validation / test with a fixed seed.

To fit a free Colab GPU, each split can be reduced. The reduction always keeps or drops
WHOLE speakers, so speakers stay separated. A cap on clips per speaker stops a few
very active speakers from dominating a split.

Outputs
  data/manifest.csv                     one row per clip (split, speaker, wav path, reference, duration)
  data/dataset_info.json                dataset version, split mode, seed, caps
  data/wav16k/<split>/<clip>.wav        16 kHz mono PCM audio (not committed)
  results/data/split_statistics.csv     speakers, utterances, hours per split
  results/data/overlap_report.json      speaker overlap (must be 0) and exact sentence overlap
"""
import argparse
import csv
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from common import DATA, DATASET_INFO, MANIFEST, NORMALIZATION_VERSION, RESULTS, ROOT, SAMPLE_RATE, normalize_tr

SPLITS = ["train", "validation", "test"]
OFFICIAL_FILES = {"train": "train.tsv", "validation": "dev.tsv", "test": "test.tsv"}


def read_tsv(path):
    return pd.read_csv(path, sep="\t", quoting=csv.QUOTE_NONE, dtype=str, on_bad_lines="skip")


def clean(df, clips_dir):
    df = df.dropna(subset=["client_id", "path", "sentence"]).copy()
    df["reference_norm"] = df["sentence"].map(normalize_tr)
    df = df[df["reference_norm"].str.len() > 0]
    df = df[df["path"].map(lambda p: (clips_dir / p).exists())]
    return df.drop_duplicates(subset="path")


def official_splits(cv_dir, clips_dir):
    parts = {}
    for split, name in OFFICIAL_FILES.items():
        f = cv_dir / name
        if not f.exists():
            raise SystemExit(f"{f} not found. Use --split-mode grouped if this release has no official splits.")
        parts[split] = clean(read_tsv(f), clips_dir)
    return parts


def grouped_splits(cv_dir, clips_dir, seed):
    from sklearn.model_selection import GroupShuffleSplit
    df = clean(read_tsv(cv_dir / "validated.tsv"), clips_dir).reset_index(drop=True)
    gss = GroupShuffleSplit(n_splits=1, test_size=0.10, random_state=seed)
    rest_idx, test_idx = next(gss.split(df, groups=df["client_id"]))
    rest = df.iloc[rest_idx].reset_index(drop=True)
    gss = GroupShuffleSplit(n_splits=1, test_size=1 / 9, random_state=seed)
    train_idx, val_idx = next(gss.split(rest, groups=rest["client_id"]))
    return {"train": rest.iloc[train_idx], "validation": rest.iloc[val_idx], "test": df.iloc[test_idx]}


def reduce_split(df, max_utts, max_per_speaker, seed):
    """Cap clips per speaker, then keep whole speakers (in seeded random order) up to max_utts."""
    rng = np.random.default_rng(seed)
    if max_per_speaker > 0:
        df = df.sample(frac=1.0, random_state=seed).groupby("client_id").head(max_per_speaker)
    if max_utts <= 0 or len(df) <= max_utts:
        return df
    speakers = np.array(sorted(df["client_id"].unique()), dtype=object)
    rng.shuffle(speakers)
    sizes = df.groupby("client_id").size()
    keep, total = [], 0
    for s in speakers:
        if total + sizes[s] <= max_utts or total == 0:
            keep.append(s)
            total += sizes[s]
        if total >= max_utts:
            break
    return df[df["client_id"].isin(keep)]


def convert_one(job):
    """Decode, resample to 16 kHz mono, write 16-bit PCM WAV. Returns duration in seconds."""
    src, dst = job
    import librosa
    import soundfile as sf
    dst = Path(dst)
    if dst.exists():
        info = sf.info(str(dst))
        return info.frames / info.samplerate
    y, _ = librosa.load(src, sr=SAMPLE_RATE, mono=True)
    dst.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(dst), y, SAMPLE_RATE, subtype="PCM_16")
    return len(y) / SAMPLE_RATE


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cv-dir", default=str(DATA / "common_voice_tr"),
                    help="Folder with train.tsv, dev.tsv, test.tsv, validated.tsv and clips/")
    ap.add_argument("--dataset-version", default="27.0", help="Exact Common Voice release you downloaded")
    ap.add_argument("--split-mode", choices=["official", "grouped"], default="official")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--max-train", type=int, default=6000, help="0 = keep all")
    ap.add_argument("--max-validation", type=int, default=600, help="0 = keep all")
    ap.add_argument("--max-test", type=int, default=2000, help="0 = keep all")
    ap.add_argument("--max-clips-per-speaker", type=int, default=20, help="0 = no cap")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--train-max-clips-per-speaker", type=int, default=0, help="0 = same as --max-clips-per-speaker")
    args = ap.parse_args()

    cv_dir = Path(args.cv_dir)
    clips_dir = cv_dir / "clips"
    if not clips_dir.exists():
        raise SystemExit(f"{clips_dir} not found. Extract the Common Voice Turkish archive into {cv_dir}.")

    parts = (official_splits(cv_dir, clips_dir) if args.split_mode == "official"
             else grouped_splits(cv_dir, clips_dir, args.seed))
    full_counts = {s: {"utterances": int(len(d)), "speakers": int(d["client_id"].nunique())} for s, d in parts.items()}
    full_train_sentences = set(parts["train"]["reference_norm"])

    caps = {"train": args.max_train, "validation": args.max_validation, "test": args.max_test}
    for s in SPLITS:
        per_spk = args.train_max_clips_per_speaker if (s == "train" and args.train_max_clips_per_speaker) else args.max_clips_per_speaker
        parts[s] = reduce_split(parts[s], caps[s], per_spk, args.seed)

    # Speaker separation check - this is the leakage rule from the Week 9 slides.
    spk = {s: set(parts[s]["client_id"]) for s in SPLITS}
    overlaps = {f"{a}-{b}": len(spk[a] & spk[b]) for a, b in
                [("train", "validation"), ("train", "test"), ("validation", "test")]}
    if any(overlaps.values()):
        raise SystemExit(f"Speaker overlap between splits: {overlaps}. Use --split-mode grouped.")

    # Durations (optional file in Common Voice releases) and conversion to 16 kHz WAV.
    dur_file = cv_dir / "clip_durations.tsv"
    declared = {}
    if dur_file.exists():
        d = read_tsv(dur_file)
        declared = dict(zip(d.iloc[:, 0], pd.to_numeric(d.iloc[:, 1], errors="coerce") / 1000.0))

    rows, jobs = [], []
    for s in SPLITS:
        for r in parts[s].itertuples():
            clip_id = Path(r.path).stem
            wav_rel = Path("data") / "wav16k" / s / f"{clip_id}.wav"
            jobs.append((str(clips_dir / r.path), str(ROOT / wav_rel)))
            rows.append({"clip_id": clip_id, "split": s, "speaker_id": r.client_id,
                         "audio_path": wav_rel.as_posix(), "source_file": r.path,
                         "reference": r.sentence, "reference_norm": r.reference_norm,
                         "declared_duration": declared.get(r.path, np.nan)})
    print(f"Converting {len(jobs)} clips to 16 kHz mono WAV ...")
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        durations = list(ex.map(convert_one, jobs, chunksize=32))
    man = pd.DataFrame(rows)
    # Replace Common Voice client IDs with short pseudonyms before anything is saved.
    pseudo = {c: f"spk{i:05d}" for i, c in enumerate(sorted(man["speaker_id"].unique()))}
    man["speaker_id"] = man["speaker_id"].map(pseudo)
    man["duration_seconds"] = np.round(durations, 3)
    man["sample_rate"] = SAMPLE_RATE
    mismatch = int(((man["declared_duration"] - man["duration_seconds"]).abs() > 0.5).sum())
    man = man.drop(columns=["declared_duration"])
    man.to_csv(MANIFEST, index=False, encoding="utf-8")

    out_dir = RESULTS / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    stats = []
    for s in SPLITS:
        p = man[man["split"] == s]
        stats.append({"split": s, "speakers": p["speaker_id"].nunique(), "utterances": len(p),
                      "hours": round(p["duration_seconds"].sum() / 3600, 3),
                      "mean_clip_seconds": round(p["duration_seconds"].mean(), 2)})
    stats = pd.DataFrame(stats)
    stats.to_csv(out_dir / "split_statistics.csv", index=False)

    train_sent = set(man[man["split"] == "train"]["reference_norm"])
    test_sent = man[man["split"] == "test"]["reference_norm"]
    val_sent = man[man["split"] == "validation"]["reference_norm"]
    overlap = {
        "speaker_overlap": overlaps,
        "test_sentences_in_train_used": int(test_sent.isin(train_sent).sum()),
        "test_sentences_in_full_official_train": int(test_sent.isin(full_train_sentences).sum()),
        "validation_sentences_in_train_used": int(val_sent.isin(train_sent).sum()),
        "test_utterances": int(len(test_sent)),
        "note": "Exact match after the shared normalization (word for word).",
    }
    (out_dir / "overlap_report.json").write_text(json.dumps(overlap, indent=2), encoding="utf-8")

    info = {"name": "Mozilla Common Voice - Turkish (Scripted Speech)", "version": args.dataset_version,
            "split_mode": args.split_mode, "seed": args.seed,
            "caps": {**caps, "max_clips_per_speaker": args.max_clips_per_speaker, "train_max_clips_per_speaker": args.train_max_clips_per_speaker or args.max_clips_per_speaker},
            "full_split_sizes_before_reduction": full_counts,
            "duration_mismatch_over_0.5s": mismatch,
            "audio": "decoded with librosa, resampled to 16 kHz mono, saved as 16-bit PCM WAV",
            "normalization": NORMALIZATION_VERSION}
    DATASET_INFO.write_text(json.dumps(info, indent=2), encoding="utf-8")

    print(stats.to_string(index=False))
    print(json.dumps(overlap, indent=2))
    print("Speaker-disjoint check: PASS")


if __name__ == "__main__":
    main()
