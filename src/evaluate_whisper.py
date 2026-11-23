"""Part 2 - Baselines: Whisper (attention encoder-decoder), zero-shot, language forced to Turkish."""
import argparse

import torch
from transformers import pipeline

from common import Timer, batches, load_audio, load_manifest, local_model_path, save_system_run


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="openai/whisper-small")
    ap.add_argument("--tag", default="whisper_small")
    ap.add_argument("--split", default="test")
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--num-beams", type=int, default=1, help="1 = greedy decoding")
    args = ap.parse_args()
    if args.model.endswith(".en"):
        raise SystemExit("'.en' Whisper checkpoints are English-only and cannot transcribe Turkish.")

    df = load_manifest(args.split)
    path, revision = local_model_path(args.model)
    cuda = torch.cuda.is_available()
    dtype = torch.float16 if cuda else torch.float32
    pipe = pipeline("automatic-speech-recognition", model=path, dtype=dtype,
                    device=0 if cuda else -1)
    gen = {"language": "turkish", "task": "transcribe", "num_beams": args.num_beams}

    hyps = []
    with Timer() as t:
        for i, chunk in enumerate(batches(list(df["audio_path"]), args.batch_size)):
            inputs = [{"raw": load_audio(p), "sampling_rate": 16000} for p in chunk]
            outs = pipe(inputs, batch_size=args.batch_size, generate_kwargs=gen)
            hyps.extend(o["text"] for o in outs)
            if (i + 1) % 10 == 0:
                print(f"{len(hyps)}/{len(df)}")

    save_system_run(args.tag, df, hyps, {
        "model": args.model, "revision": revision, "family": "attention encoder-decoder (Whisper)",
        "role": "baseline", "training_by_group": "none (zero-shot)",
        "settings": {**gen, "batch_size": args.batch_size, "dtype": str(dtype)},
        "inference_seconds": t.seconds,
    })


if __name__ == "__main__":
    main()
