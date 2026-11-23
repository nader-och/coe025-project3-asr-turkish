"""Shared utilities used by every part of the project.

- One Turkish text normalization policy for references and hypotheses.
- One scoring function (corpus WER/CER with S/D/I counts) for every system.
- Speaker-level bootstrap for confidence intervals (clips of one speaker are not independent).
- Pinned model download (exact Hugging Face commit) and a run record for every system.
"""
import json
import platform
import re
import time
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
SYSTEMS = RESULTS / "systems"
MANIFEST = DATA / "manifest.csv"
DATASET_INFO = DATA / "dataset_info.json"
REVISIONS_FILE = RESULTS / "model_revisions.json"
SAMPLE_RATE = 16000
NORMALIZATION_VERSION = "tr-norm-v1"

_APOSTROPHES = "'’‘ʼ`´"


# ---------------------------------------------------------------------------
# Text normalization
# ---------------------------------------------------------------------------
def normalize_tr(text) -> str:
    """Turkish-aware normalization, applied to references AND hypotheses of every system.

    1. Unicode NFKC.
    2. Turkish lowercasing: I -> ı and İ -> i before lower() (Python's lower() is not Turkish-aware).
    3. Remove stray combining dot above (U+0307).
    4. Delete apostrophes, so "İstanbul'da" and "istanbulda" are the same word.
    5. Every other punctuation mark or symbol becomes a space.
    6. Collapse whitespace.
    Turkish letters (ç ğ ı ö ş ü) and digits are kept. Nothing is transliterated.
    """
    if text is None or (isinstance(text, float) and np.isnan(text)):
        return ""
    t = unicodedata.normalize("NFKC", str(text))
    t = t.replace("I", "ı").replace("İ", "i").lower()
    t = t.replace("̇", "")
    for a in _APOSTROPHES:
        t = t.replace(a, "")
    t = "".join(ch if (ch.isalnum() or ch.isspace()) else " " for ch in t)
    return re.sub(r"\s+", " ", t).strip()


# ---------------------------------------------------------------------------
# Data access
# ---------------------------------------------------------------------------
def load_manifest(split=None) -> pd.DataFrame:
    if not MANIFEST.exists():
        raise SystemExit("data/manifest.csv not found. Run src/prepare_common_voice.py first.")
    df = pd.read_csv(MANIFEST, dtype={"clip_id": str, "speaker_id": str})
    if split:
        df = df[df["split"] == split].reset_index(drop=True)
    return df


def load_audio(rel_path) -> np.ndarray:
    """Load a manifest audio file as 16 kHz mono float32 and check the sample rate."""
    import soundfile as sf
    path = ROOT / rel_path
    audio, sr = sf.read(str(path), dtype="float32", always_2d=False)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    if sr != SAMPLE_RATE:
        import librosa
        audio = librosa.resample(audio, orig_sr=sr, target_sr=SAMPLE_RATE)
    return audio.astype(np.float32)


def batches(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
def per_utterance_counts(refs_n, hyps_n):
    """Word-level S, D, I and reference length for every utterance (minimum-edit alignment)."""
    import jiwer
    out = jiwer.process_words(refs_n, hyps_n)
    rows = []
    for ref, chunks in zip(out.references, out.alignments):
        s = d = i = 0
        for c in chunks:
            if c.type == "substitute":
                s += c.ref_end_idx - c.ref_start_idx
            elif c.type == "delete":
                d += c.ref_end_idx - c.ref_start_idx
            elif c.type == "insert":
                i += c.hyp_end_idx - c.hyp_start_idx
        rows.append({"sub": s, "del": d, "ins": i, "ref_words": len(ref)})
    return pd.DataFrame(rows), out


def corpus_scores(refs_n, hyps_n) -> dict:
    """Corpus-level scores: total edits / total reference units (not a mean of clip scores)."""
    import jiwer
    w = jiwer.process_words(refs_n, hyps_n)
    c = jiwer.process_characters(refs_n, hyps_n)
    n_words = w.hits + w.substitutions + w.deletions
    n_chars = c.hits + c.substitutions + c.deletions
    return {
        "wer": float(w.wer),
        "cer": float(c.cer),
        "mer": float(w.mer),
        "wil": float(w.wil),
        "substitutions": int(w.substitutions),
        "deletions": int(w.deletions),
        "insertions": int(w.insertions),
        "hits": int(w.hits),
        "reference_words": int(n_words),
        "char_substitutions": int(c.substitutions),
        "char_deletions": int(c.deletions),
        "char_insertions": int(c.insertions),
        "reference_characters": int(n_chars),
    }


def speaker_bootstrap_wer(errors, ref_words, speakers, n_boot=1000, seed=0):
    """95% interval for corpus WER, resampling whole speakers (slides: respect clusters)."""
    df = pd.DataFrame({"e": errors, "n": ref_words, "s": speakers}).groupby("s")[["e", "n"]].sum()
    e, n = df["e"].to_numpy(), df["n"].to_numpy()
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(df), size=(n_boot, len(df)))
    w = e[idx].sum(axis=1) / np.maximum(n[idx].sum(axis=1), 1)
    return float(np.percentile(w, 2.5)), float(np.percentile(w, 97.5))


def paired_speaker_bootstrap(pred_a: pd.DataFrame, pred_b: pd.DataFrame, n_boot=1000, seed=0):
    """WER(b) - WER(a) on identical clips, with a speaker-level bootstrap interval."""
    m = pred_a[["clip_id", "speaker_id", "errors", "ref_words"]].merge(
        pred_b[["clip_id", "errors"]], on="clip_id", suffixes=("_a", "_b"))
    g = m.groupby("speaker_id")[["errors_a", "errors_b", "ref_words"]].sum()
    ea, eb, n = g["errors_a"].to_numpy(), g["errors_b"].to_numpy(), g["ref_words"].to_numpy()
    delta = (eb.sum() - ea.sum()) / n.sum()
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(g), size=(n_boot, len(g)))
    d = (eb[idx].sum(axis=1) - ea[idx].sum(axis=1)) / np.maximum(n[idx].sum(axis=1), 1)
    return {"delta_wer": float(delta), "ci_low": float(np.percentile(d, 2.5)),
            "ci_high": float(np.percentile(d, 97.5)), "matched_clips": int(len(m))}


# ---------------------------------------------------------------------------
# Models and run records
# ---------------------------------------------------------------------------
def pinned_revision(model_id):
    if REVISIONS_FILE.exists():
        info = json.loads(REVISIONS_FILE.read_text(encoding="utf-8")).get(model_id, {})
        rev = info.get("revision")
        if rev and rev != "LOOKUP_FAILED":
            return rev
    return None


def local_model_path(model_id, allow_patterns=None):
    """Download a model at its pinned commit and return (local_path, revision).

    A local directory (for example our fine-tuned checkpoint) is used as it is.
    """
    if Path(model_id).exists():
        return str(model_id), "local"
    from huggingface_hub import snapshot_download
    rev = pinned_revision(model_id)
    path = snapshot_download(model_id, revision=rev, allow_patterns=allow_patterns)
    return path, (rev or Path(path).name)


def environment_info() -> dict:
    info = {"python": platform.python_version(), "platform": platform.platform()}
    for pkg in ["torch", "transformers", "jiwer", "librosa", "qwen_asr", "sherpa_onnx"]:
        try:
            mod = __import__(pkg)
            info[pkg] = getattr(mod, "__version__", "installed")
        except Exception:
            pass
    try:
        import torch
        info["gpu"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none (CPU)"
    except Exception:
        info["gpu"] = "unknown"
    return info


class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *exc):
        self.seconds = time.perf_counter() - self.start


def save_system_run(tag, df, hypotheses, run_info):
    """Save predictions, metrics and a run manifest for one system on one split.

    df: manifest rows (same order as hypotheses). run_info: model, revision, family,
    role ("baseline" or "contribution"), settings and inference_seconds.
    """
    out_dir = SYSTEMS / tag
    out_dir.mkdir(parents=True, exist_ok=True)
    refs_n = [normalize_tr(x) for x in df["reference"]]
    hyps_n = [normalize_tr(x) for x in hypotheses]
    counts, _ = per_utterance_counts(refs_n, hyps_n)

    pred = pd.DataFrame({
        "clip_id": df["clip_id"].values,
        "speaker_id": df["speaker_id"].values,
        "duration_seconds": df["duration_seconds"].values,
        "reference": df["reference"].values,
        "hypothesis": list(hypotheses),
        "reference_norm": refs_n,
        "hypothesis_norm": hyps_n,
    })
    pred = pd.concat([pred, counts], axis=1)
    pred["errors"] = pred["sub"] + pred["del"] + pred["ins"]
    pred.to_csv(out_dir / "predictions.csv", index=False, encoding="utf-8")

    metrics = corpus_scores(refs_n, hyps_n)
    lo, hi = speaker_bootstrap_wer(pred["errors"], pred["ref_words"], pred["speaker_id"])
    audio_seconds = float(df["duration_seconds"].sum())
    inf_sec = float(run_info.get("inference_seconds", float("nan")))
    metrics.update({
        "wer_ci95": [lo, hi],
        "utterances": int(len(pred)),
        "speakers": int(pred["speaker_id"].nunique()),
        "empty_hypotheses": int(sum(1 for h in hyps_n if not h)),
        "audio_hours": round(audio_seconds / 3600, 4),
        "inference_seconds": round(inf_sec, 2),
        "rtf": round(inf_sec / audio_seconds, 4) if audio_seconds else None,
    })
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    dataset = json.loads(DATASET_INFO.read_text(encoding="utf-8")) if DATASET_INFO.exists() else {}
    manifest = {
        "tag": tag,
        **run_info,
        "split": str(df["split"].iloc[0]) if len(df) else None,
        "dataset": {k: dataset.get(k) for k in ["name", "version", "split_mode", "seed"]},
        "normalization": NORMALIZATION_VERSION,
        "scoring": "jiwer corpus-level WER/CER on normalized text",
        "environment": environment_info(),
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                                               encoding="utf-8")
    print(json.dumps({k: metrics[k] for k in ["wer", "cer", "wer_ci95", "utterances", "rtf"]}, indent=2))
    print(f"Saved results/systems/{tag}/")
    return metrics
