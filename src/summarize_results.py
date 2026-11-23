"""Part 3 - Collect every system's test results into one comparison.

Baselines and our own trained model are reported in SEPARATE tables (course rule).
All systems must have been scored on the identical test clips; this script checks that.

Outputs: results/summary.csv, results/comparison.json, results/RESULTS.md
"""
import json

import pandas as pd

from common import DATASET_INFO, RESULTS, SYSTEMS, paired_speaker_bootstrap


def pct(x):
    return "-" if x is None or pd.isna(x) else f"{100 * x:.2f}%"


def load_systems(split="test"):
    rows, preds = [], {}
    for d in sorted(SYSTEMS.glob("*")):
        if not (d / "metrics.json").exists():
            continue
        m = json.loads((d / "metrics.json").read_text(encoding="utf-8"))
        r = json.loads((d / "run_manifest.json").read_text(encoding="utf-8"))
        if r.get("split") != split:
            continue
        rows.append({
            "tag": d.name, "role": r.get("role"), "model": r.get("model"),
            "revision": str(r.get("revision", ""))[:12], "family": r.get("family"),
            "base_model": r.get("base_model", ""),
            "wer": m["wer"], "cer": m["cer"], "wer_ci_low": m["wer_ci95"][0], "wer_ci_high": m["wer_ci95"][1],
            "substitutions": m["substitutions"], "deletions": m["deletions"], "insertions": m["insertions"],
            "reference_words": m["reference_words"], "utterances": m["utterances"], "speakers": m["speakers"],
            "empty_hypotheses": m["empty_hypotheses"], "rtf": m["rtf"],
            "gpu": r.get("environment", {}).get("gpu", ""),
        })
        preds[d.name] = pd.read_csv(d / "predictions.csv", dtype={"clip_id": str, "speaker_id": str})
    return pd.DataFrame(rows), preds


def table(df):
    lines = ["| System | Checkpoint @ revision | Family | WER | 95% CI (speakers) | CER | S / D / I | Clips | RTF |",
             "|---|---|---|---:|---|---:|---|---:|---:|"]
    for r in df.sort_values("wer").itertuples():
        lines.append(f"| {r.tag} | `{r.model}` @ {r.revision} | {r.family} | {pct(r.wer)} | "
                     f"{pct(r.wer_ci_low)} - {pct(r.wer_ci_high)} | {pct(r.cer)} | "
                     f"{r.substitutions} / {r.deletions} / {r.insertions} | {r.utterances} | {r.rtf} |")
    return "\n".join(lines)


def main():
    df, preds = load_systems()
    if df.empty:
        raise SystemExit("No test results found in results/systems/. Run the evaluation scripts first.")

    clip_sets = {t: frozenset(p["clip_id"]) for t, p in preds.items()}
    identical = len(set(clip_sets.values())) == 1
    if not identical:
        print("WARNING: systems were not scored on the same test clips:",
              {t: len(s) for t, s in clip_sets.items()})

    comparisons = []
    for r in df[df["role"] == "contribution"].itertuples():
        base = df[(df["role"] == "baseline") & (df["model"] == r.base_model)]
        if len(base):
            b = base.iloc[0]["tag"]
            c = paired_speaker_bootstrap(preds[b], preds[r.tag])
            comparisons.append({"contribution": r.tag, "baseline": b, **c})
    df.to_csv(RESULTS / "summary.csv", index=False)
    (RESULTS / "comparison.json").write_text(json.dumps(
        {"identical_test_clips": identical, "paired_comparisons": comparisons}, indent=2), encoding="utf-8")

    md = ["# Results", ""]
    info = json.loads(DATASET_INFO.read_text(encoding="utf-8")) if DATASET_INFO.exists() else {}
    md += [f"Dataset: {info.get('name', '?')}, release {info.get('version', '?')}, "
           f"split mode: {info.get('split_mode', '?')}, seed {info.get('seed', '?')}.", ""]
    stats_f = RESULTS / "data" / "split_statistics.csv"
    if stats_f.exists():
        md += ["## Data splits", "", pd.read_csv(stats_f).to_markdown(index=False), ""]
    ov_f = RESULTS / "data" / "overlap_report.json"
    if ov_f.exists():
        ov = json.loads(ov_f.read_text(encoding="utf-8"))
        md += [f"Speaker overlap between splits: {ov['speaker_overlap']}. "
               f"Test sentences that appear word for word in our training split: "
               f"{ov['test_sentences_in_train_used']} / {ov['test_utterances']} "
               f"(in the full official train split: {ov['test_sentences_in_full_official_train']}).", ""]
    md += ["## Baselines (no training by our group)", "", table(df[df["role"] == "baseline"]), ""]
    if (df["role"] == "contribution").any():
        md += ["## Our contribution (trained by our group)", "", table(df[df["role"] == "contribution"]), ""]
    for c in comparisons:
        md += [f"Paired comparison on {c['matched_clips']} identical test clips: WER({c['contribution']}) - "
               f"WER({c['baseline']}) = {100 * c['delta_wer']:+.2f} points "
               f"(95% speaker-bootstrap interval {100 * c['ci_low']:+.2f} to {100 * c['ci_high']:+.2f}).", ""]
    tr_f = RESULTS / "training" / "training_summary.json"
    if tr_f.exists():
        tr = json.loads(tr_f.read_text(encoding="utf-8"))
        ep = pd.DataFrame(tr["validation_by_epoch"])
        ep["validation_wer"] = ep["validation_wer"].map(pct)
        ep["validation_cer"] = ep["validation_cer"].map(pct)
        md += ["## Fine-tuning: validation WER by epoch (test not used)", "",
               ep.to_markdown(index=False), "",
               f"Selected epoch: {tr['best_epoch']} (lowest validation WER).", ""]
    matrix = RESULTS / "baseline_matrix.csv"
    if matrix.exists():
        m = pd.read_csv(matrix)
        m = m[m["status"] != "run"]
        if len(m):
            md += ["## Baselines not run, and why", "", m.to_markdown(index=False), ""]
    md += ["Scoring: corpus-level WER and CER (total edits / total reference words or characters) "
           "after one shared Turkish normalization (src/common.py). RTF = compute seconds / audio seconds."]
    (RESULTS / "RESULTS.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(df[["tag", "role", "wer", "cer", "utterances", "rtf"]].to_string(index=False))
    print("Identical test clips for all systems:", identical)
    for c in comparisons:
        print(c)
    print("Saved results/summary.csv and results/RESULTS.md")


if __name__ == "__main__":
    main()
