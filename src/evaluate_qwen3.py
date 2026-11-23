"""Part 2 - Baselines: Qwen3-ASR, zero-shot, language set to Turkish.

Install separately: pip install qwen-asr   (it pins transformers==4.57.6, same as requirements.txt)
"""
import argparse

import torch

from common import Timer, batches, load_audio, load_manifest, local_model_path, save_system_run


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-ASR-0.6B")
    ap.add_argument("--tag", default="qwen3_asr_0.6b")
    ap.add_argument("--split", default="test")
    ap.add_argument("--batch-size", type=int, default=16)
    args = ap.parse_args()
    try:
        from qwen_asr import Qwen3ASRModel
    except ImportError as e:
        raise SystemExit("Install with: pip install qwen-asr") from e

    df = load_manifest(args.split)
    path, revision = local_model_path(args.model)
    if torch.cuda.is_available():
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        device_map = "cuda:0"
    else:
        dtype, device_map = torch.float32, "cpu"
    model = Qwen3ASRModel.from_pretrained(path, dtype=dtype, device_map=device_map,
                                          max_inference_batch_size=args.batch_size, max_new_tokens=256)

    hyps = []
    with Timer() as t:
        for i, chunk in enumerate(batches(list(df["audio_path"]), args.batch_size)):
            audio = [(load_audio(p), 16000) for p in chunk]
            results = model.transcribe(audio=audio, language="Turkish")
            hyps.extend(r.text for r in results)
            if (i + 1) % 10 == 0:
                print(f"{len(hyps)}/{len(df)}")

    save_system_run(args.tag, df, hyps, {
        "model": args.model, "revision": revision, "family": "pretrained ASR checkpoint (Qwen3-ASR)",
        "role": "baseline", "training_by_group": "none (zero-shot)",
        "settings": {"language": "Turkish", "batch_size": args.batch_size, "dtype": str(dtype),
                     "max_new_tokens": 256, "context": ""},
        "inference_seconds": t.seconds,
    })


if __name__ == "__main__":
    main()
