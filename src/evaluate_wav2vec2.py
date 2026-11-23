"""Part 2 / Part 3: wav2vec 2.0 + CTC head, greedy CTC decoding.

Used for the published Turkish checkpoint (baseline) and for our fine-tuned checkpoint
(contribution, --role contribution --model <local folder>).
"""
import argparse

import torch
from transformers import AutoModelForCTC, AutoProcessor

from common import Timer, batches, load_audio, load_manifest, local_model_path, save_system_run


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="m3hrdadfi/wav2vec2-large-xlsr-turkish")
    ap.add_argument("--tag", default="wav2vec2_xlsr_tr")
    ap.add_argument("--split", default="test")
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--role", choices=["baseline", "contribution"], default="baseline")
    ap.add_argument("--base-model", default="", help="For a fine-tuned model: the checkpoint it started from")
    args = ap.parse_args()

    df = load_manifest(args.split)
    path, revision = local_model_path(args.model)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = AutoProcessor.from_pretrained(path)
    model = AutoModelForCTC.from_pretrained(path).to(device).eval()

    hyps = []
    with Timer() as t:
        for i, chunk in enumerate(batches(list(df["audio_path"]), args.batch_size)):
            audio = [load_audio(p) for p in chunk]
            inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)
            inputs = {k: v.to(device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = model(**inputs).logits
            ids = torch.argmax(logits, dim=-1)
            hyps.extend(processor.batch_decode(ids))
            if (i + 1) % 10 == 0:
                print(f"{len(hyps)}/{len(df)}")

    info = {"model": args.model, "revision": revision, "family": "wav2vec 2.0 + CTC head",
            "role": args.role,
            "training_by_group": "none (zero-shot)" if args.role == "baseline"
            else "fine-tuned by our group on our training split (see results/training/)",
            "settings": {"decoding": "greedy CTC (argmax, collapse repeats, remove blanks)",
                         "batch_size": args.batch_size, "dtype": "float32"},
            "inference_seconds": t.seconds}
    if args.base_model:
        info["base_model"] = args.base_model
    save_system_run(args.tag, df, hyps, info)


if __name__ == "__main__":
    main()
