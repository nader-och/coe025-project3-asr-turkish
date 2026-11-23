"""Part 3 - Write the measured numbers into the report and the slides.

Reads only files produced by the other scripts (results/...). A value that was not measured
is written as "not run" - never estimated.

  report/report_source.md          -> report/Turkish_ASR_Project_Report.md
  presentation/slides_source.pptx  -> presentation/Turkish_ASR_Presentation.pptx
"""
import json
import re

import pandas as pd

from common import RESULTS, ROOT, SYSTEMS

SYSTEM_KEYS = {
    "WHISPER": "whisper_small",
    "W2V": "wav2vec2_xlsr_tr",
    "QWEN": "qwen3_asr_0.6b",
    "RNNT": "seda_rnnt",
    "FT": "wav2vec2_xlsr_tr_finetuned",
}
DISPLAY = {
    "whisper_small": "Whisper small",
    "wav2vec2_xlsr_tr": "wav2vec2 XLSR Turkish (CTC)",
    "qwen3_asr_0.6b": "Qwen3-ASR 0.6B",
    "qwen3_asr_1.7b": "Qwen3-ASR 1.7B",
    "seda_rnnt": "seda v0.1 (RNN-T)",
    "wav2vec2_xlsr_tr_finetuned": "our fine-tuned wav2vec2",
}
MISSING = "not run"


def pct(x):
    return f"{100 * x:.1f}%"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def build_values():
    v = {}
    info = read_json(ROOT / "data" / "dataset_info.json") or {}
    v["DATASET_VERSION"] = str(info.get("version", MISSING))
    v["SPLIT_MODE"] = {"official": "official Common Voice splits", "grouped": "our speaker-grouped split"}.get(
        info.get("split_mode"), MISSING)

    stats_f = RESULTS / "data" / "split_statistics.csv"
    if stats_f.exists():
        st = pd.read_csv(stats_f).set_index("split")
        for split, key in [("train", "TRAIN"), ("validation", "VAL"), ("test", "TEST")]:
            if split in st.index:
                v[f"{key}_SPK"] = f"{int(st.loc[split, 'speakers']):,}"
                v[f"{key}_UTT"] = f"{int(st.loc[split, 'utterances']):,}"
                v[f"{key}_HRS"] = f"{st.loc[split, 'hours']:.2f}"
    ov = read_json(RESULTS / "data" / "overlap_report.json")
    if ov:
        v["SPK_OVERLAP"] = " / ".join(str(x) for x in ov["speaker_overlap"].values())
        v["SENT_OVERLAP"] = f"{ov['test_sentences_in_train_used']} / {ov['test_utterances']}"
        v["SENT_OVERLAP_FULL"] = f"{ov['test_sentences_in_full_official_train']} / {ov['test_utterances']}"

    metrics = {}
    for key, tag in SYSTEM_KEYS.items():
        m = read_json(SYSTEMS / tag / "metrics.json")
        r = read_json(SYSTEMS / tag / "run_manifest.json")
        if not m:
            continue
        metrics[tag] = m
        v[f"{key}_WER"] = pct(m["wer"])
        v[f"{key}_CER"] = pct(m["cer"])
        v[f"{key}_CI"] = f"{100 * m['wer_ci95'][0]:.1f}-{100 * m['wer_ci95'][1]:.1f}%"
        v[f"{key}_SDI"] = f"{m['substitutions']} / {m['deletions']} / {m['insertions']}"
        v[f"{key}_N"] = f"{m['utterances']:,}"
        v[f"{key}_RTF"] = f"{m['rtf']:.3f}" if m.get("rtf") is not None else MISSING
        v[f"{key}_REV"] = str(r.get("revision", ""))[:7] if r else MISSING
        if r and "GPU" not in v:
            v["GPU"] = r.get("environment", {}).get("gpu", MISSING)

    baselines = {t: m for t, m in metrics.items() if t != SYSTEM_KEYS["FT"]}
    if baselines:
        best = min(baselines, key=lambda t: baselines[t]["wer"])
        v["BEST_BASELINE"] = DISPLAY.get(best, best)
        v["BEST_BASELINE_WER"] = pct(baselines[best]["wer"])
        v["BASELINES_RUN"] = str(len(baselines))

    comp = read_json(RESULTS / "comparison.json")
    pairs = (comp or {}).get("paired_comparisons", [])
    if pairs:
        c = pairs[0]
        d, lo, hi = 100 * c["delta_wer"], 100 * c["ci_low"], 100 * c["ci_high"]
        v["FT_DELTA"] = f"{d:+.1f} points"
        v["FT_DELTA_CI"] = f"{lo:+.1f} to {hi:+.1f}"
        if hi < 0:
            v["FT_VERDICT"] = f"Fine-tuning lowered test WER by {abs(d):.1f} points; the 95% interval does not include zero."
        elif lo > 0:
            v["FT_VERDICT"] = f"Fine-tuning raised test WER by {d:.1f} points; the 95% interval does not include zero."
        else:
            v["FT_VERDICT"] = "No clear difference: the 95% interval of the WER change includes zero."
        v["IDENTICAL_CLIPS"] = "yes" if comp.get("identical_test_clips") else "NO - check"

    tr = read_json(RESULTS / "training" / "training_summary.json")
    if tr:
        for row in tr["validation_by_epoch"]:
            v[f"EP{row['epoch']}_WER"] = pct(row["validation_wer"])
        v["BEST_EPOCH"] = str(tr["best_epoch"])
        v["BEST_VAL_WER"] = pct(tr["best_validation_wer"])
        v["TRAIN_MIN"] = f"{tr['training_minutes']:.0f}"
        v["EPOCHS"] = str(tr["settings"]["epochs"])
        v["LR"] = f"{tr['settings']['learning_rate']:g}"
        v["EFF_BATCH"] = str(tr["settings"]["effective_batch"])
        v["OOV_RATE"] = f"{100 * tr['oov_character_rate']:.2f}%"
        v["FT_GPU"] = tr.get("environment", {}).get("gpu", MISSING)

    err_f = RESULTS / "error_analysis" / "error_summary.csv"
    ex = read_json(RESULTS / "error_analysis" / "examples.json") or {}
    if err_f.exists():
        err = pd.read_csv(err_f).set_index("system")
        sys_tag = SYSTEM_KEYS["FT"] if SYSTEM_KEYS["FT"] in err.index else err.index[0]
        e = err.loc[sys_tag]
        v["ERR_SYS"] = DISPLAY.get(sys_tag, sys_tag)
        for col, key in [("turkish_letter", "ERR_LETTER"), ("suffix", "ERR_SUFFIX"), ("other", "ERR_OTHER"),
                         ("deletion", "ERR_DEL"), ("insertion", "ERR_INS"),
                         ("word_boundary_only_clips", "ERR_SPACE")]:
            v[key] = f"{int(e[col]):,}"
        v["ERR_SUFFIX_SHARE"] = pct(e["suffix_share_of_substitutions"])
        v["ERR_LETTER_SHARE"] = pct(e["turkish_letter_share_of_substitutions"])
        cats = ex.get(sys_tag, {})
        for i, cat in enumerate(["suffix", "turkish_letter", "other"], start=1):
            items = cats.get(cat) or []
            if items:
                v[f"EX{i}_REF"] = items[0]["reference"]
                v[f"EX{i}_HYP"] = items[0]["hypothesis"]
                v[f"EX{i}_ERR"] = items[0]["error"]
    return v


def replace_tokens(text, values, missing):
    def sub(m):
        key = m.group(1)
        if key not in values:
            missing.add(key)
        return values.get(key, MISSING)
    return re.sub(r"\{\{([A-Z0-9_]+)\}\}", sub, text)


def fill_pptx(src, dst, values, missing):
    from pptx import Presentation
    prs = Presentation(src)

    def frames(shapes):
        for sh in shapes:
            if sh.shape_type == 6:  # group
                yield from frames(sh.shapes)
            if sh.has_text_frame:
                yield sh.text_frame
            if getattr(sh, "has_table", False) and sh.has_table:
                for row in sh.table.rows:
                    for cell in row.cells:
                        yield cell.text_frame

    for slide in prs.slides:
        for tf in frames(slide.shapes):
            for p in tf.paragraphs:
                for r in p.runs:
                    if "{{" in r.text:
                        r.text = replace_tokens(r.text, values, missing)
    prs.save(dst)


def main():
    values = build_values()
    missing = set()
    src_md, dst_md = ROOT / "report" / "report_source.md", ROOT / "report" / "Turkish_ASR_Project_Report.md"
    dst_md.write_text(replace_tokens(src_md.read_text(encoding="utf-8"), values, missing), encoding="utf-8")
    src_p = ROOT / "presentation" / "slides_source.pptx"
    dst_p = ROOT / "presentation" / "Turkish_ASR_Presentation.pptx"
    fill_pptx(src_p, dst_p, values, missing)
    print(f"Filled {len(values)} values into {dst_md.name} and {dst_p.name}")
    if missing:
        print("Not measured yet (written as 'not run'):", ", ".join(sorted(missing)))


if __name__ == "__main__":
    main()
