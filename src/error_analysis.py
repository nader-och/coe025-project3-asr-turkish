"""Part 3 - Error analysis: what kind of errors each system makes, with real examples.

Word substitutions are put into categories that matter for Turkish:
  turkish_letter  same word except Turkish letters (c/ç, g/ğ, i/ı, o/ö, s/ş, u/ü)
  suffix          same stem, different ending (shared start of at least 3 letters and half the
                  shorter word) - typical for an agglutinative language
  other           any other substituted word
Deletions and insertions are counted separately. "word_boundary" counts clips where the
only problem is spacing (removing spaces makes reference and hypothesis equal).

Outputs: results/error_analysis/error_summary.csv, results/error_analysis/examples.md,
         results/error_analysis/examples.json
"""
import json

import pandas as pd

from common import RESULTS, SYSTEMS

ASCII = str.maketrans("çğıöşü", "cgiosu")


def category(ref_word, hyp_word):
    if ref_word.translate(ASCII) == hyp_word.translate(ASCII):
        return "turkish_letter"
    n = 0
    for a, b in zip(ref_word, hyp_word):
        if a != b:
            break
        n += 1
    if n >= 3 and n >= 0.5 * min(len(ref_word), len(hyp_word)):
        return "suffix"
    return "other"


def analyse(pred):
    import jiwer
    pred = pred.fillna({"reference_norm": "", "hypothesis_norm": ""})
    out = jiwer.process_words(list(pred["reference_norm"]), list(pred["hypothesis_norm"]))
    counts = {"turkish_letter": 0, "suffix": 0, "other": 0, "deletion": 0, "insertion": 0}
    examples = {k: [] for k in counts}
    for row, ref, hyp, chunks in zip(pred.itertuples(), out.references, out.hypotheses, out.alignments):
        for c in chunks:
            if c.type == "substitute":
                for r, h in zip(ref[c.ref_start_idx:c.ref_end_idx], hyp[c.hyp_start_idx:c.hyp_end_idx]):
                    cat = category(r, h)
                    counts[cat] += 1
                    examples[cat].append((row.clip_id, row.reference, row.hypothesis, f"{r} -> {h}"))
            elif c.type == "delete":
                counts["deletion"] += c.ref_end_idx - c.ref_start_idx
                examples["deletion"].append((row.clip_id, row.reference, row.hypothesis,
                                             "missing: " + " ".join(ref[c.ref_start_idx:c.ref_end_idx])))
            elif c.type == "insert":
                counts["insertion"] += c.hyp_end_idx - c.hyp_start_idx
                examples["insertion"].append((row.clip_id, row.reference, row.hypothesis,
                                              "extra: " + " ".join(hyp[c.hyp_start_idx:c.hyp_end_idx])))
    boundary = int(((pred["reference_norm"] != pred["hypothesis_norm"]) &
                    (pred["reference_norm"].str.replace(" ", "") ==
                     pred["hypothesis_norm"].str.replace(" ", ""))).sum())
    return counts, examples, boundary


def main():
    out_dir = RESULTS / "error_analysis"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows, md, ex_json = [], ["# Error analysis (test split)", ""], {}
    for d in sorted(SYSTEMS.glob("*")):
        f = d / "predictions.csv"
        if not f.exists():
            continue
        run = json.loads((d / "run_manifest.json").read_text(encoding="utf-8"))
        if run.get("split") != "test":
            continue
        pred = pd.read_csv(f, dtype={"clip_id": str})
        counts, examples, boundary = analyse(pred)
        subs = counts["turkish_letter"] + counts["suffix"] + counts["other"]
        total = subs + counts["deletion"] + counts["insertion"]
        rows.append({"system": d.name, "role": run.get("role"), **counts,
                     "word_boundary_only_clips": boundary, "total_word_errors": total,
                     "suffix_share_of_substitutions": round(counts["suffix"] / subs, 3) if subs else 0.0,
                     "turkish_letter_share_of_substitutions": round(counts["turkish_letter"] / subs, 3) if subs else 0.0})
        md += [f"## {d.name}", "",
               f"Substitutions: {subs} (Turkish letter {counts['turkish_letter']}, suffix {counts['suffix']}, "
               f"other {counts['other']}); deletions {counts['deletion']}; insertions {counts['insertion']}; "
               f"clips wrong only because of spacing: {boundary}.", ""]
        ex_json[d.name] = {}
        for cat, items in examples.items():
            if not items:
                continue
            md += [f"**{cat}**", "", "| Clip | Reference | Hypothesis | Error |", "|---|---|---|---|"]
            for clip, ref, hyp, err in items[:5]:
                md.append(f"| {clip} | {ref} | {hyp} | {err} |")
            md.append("")
            ex_json[d.name][cat] = [dict(zip(["clip_id", "reference", "hypothesis", "error"], x)) for x in items[:5]]

    if not rows:
        raise SystemExit("No test predictions found in results/systems/.")
    pd.DataFrame(rows).to_csv(out_dir / "error_summary.csv", index=False)
    (out_dir / "examples.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (out_dir / "examples.json").write_text(json.dumps(ex_json, indent=2, ensure_ascii=False), encoding="utf-8")
    print(pd.DataFrame(rows).to_string(index=False))
    print("Saved results/error_analysis/")


if __name__ == "__main__":
    main()
