"""Part 2 - Baselines: transducer (RNN-T) family.

Checkpoint: atasoglu/seda-v0.1, a streaming Zipformer2 transducer for Turkish (Apache-2.0),
run with sherpa-onnx on CPU. Greedy search, no external language model, so the comparison
with the other systems is acoustic-model only.

Install: pip install sherpa-onnx
"""
import argparse
from pathlib import Path

import numpy as np

from common import Timer, batches, load_audio, load_manifest, local_model_path, save_system_run


def pick(folder, prefix):
    files = sorted(Path(folder).glob(f"{prefix}*.onnx"))
    int8 = [f for f in files if "int8" in f.name]
    if not (int8 or files):
        raise SystemExit(f"No {prefix}*.onnx file found in {folder}")
    return str((int8 or files)[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="atasoglu/seda-v0.1")
    ap.add_argument("--tag", default="seda_rnnt")
    ap.add_argument("--split", default="test")
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--batch-size", type=int, default=32)
    args = ap.parse_args()
    import sherpa_onnx

    df = load_manifest(args.split)
    path, revision = local_model_path(args.model, allow_patterns=["*.onnx", "tokens.txt", "*.md"])
    rec = sherpa_onnx.OnlineRecognizer.from_transducer(
        tokens=str(Path(path) / "tokens.txt"), encoder=pick(path, "encoder"),
        decoder=pick(path, "decoder"), joiner=pick(path, "joiner"),
        num_threads=args.threads, sample_rate=16000, feature_dim=80, decoding_method="greedy_search")
    tail = np.zeros(int(0.8 * 16000), dtype=np.float32)  # flush the last frames of a streaming model

    hyps = []
    with Timer() as t:
        for i, chunk in enumerate(batches(list(df["audio_path"]), args.batch_size)):
            streams = []
            for p in chunk:
                s = rec.create_stream()
                s.accept_waveform(16000, load_audio(p))
                s.accept_waveform(16000, tail)
                s.input_finished()
                streams.append(s)
            while True:
                ready = [s for s in streams if rec.is_ready(s)]
                if not ready:
                    break
                rec.decode_streams(ready)
            hyps.extend(rec.get_result(s) for s in streams)
            if (i + 1) % 10 == 0:
                print(f"{len(hyps)}/{len(df)}")

    save_system_run(args.tag, df, hyps, {
        "model": args.model, "revision": revision, "family": "transducer (Zipformer2 RNN-T, streaming)",
        "role": "baseline", "training_by_group": "none (zero-shot)",
        "settings": {"decoding": "greedy_search", "language_model": "none", "threads": args.threads,
                     "runtime": "sherpa-onnx CPU, int8", "tail_padding_seconds": 0.8},
        "inference_seconds": t.seconds,
    })


if __name__ == "__main__":
    main()
