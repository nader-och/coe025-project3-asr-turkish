"""Part 2 - Baselines: record the exact Hugging Face commit of every checkpoint we use or exclude.

The evaluation scripts download each model at the commit saved here, so the results can be
reproduced with exactly the same weights. "Whisper" is a model family; "openai/whisper-small"
at a fixed commit is a specific model.
"""
import json

from huggingface_hub import HfApi

from common import REVISIONS_FILE

MODELS = {
    # evaluated baselines
    "openai/whisper-small": "attention encoder-decoder (multilingual, not .en)",
    "m3hrdadfi/wav2vec2-large-xlsr-turkish": "wav2vec 2.0 + CTC head, fine-tuned for Turkish",
    "Qwen/Qwen3-ASR-0.6B": "pretrained ASR checkpoint (Qwen3-ASR)",
    "Qwen/Qwen3-ASR-1.7B": "pretrained ASR checkpoint (Qwen3-ASR, optional larger size)",
    "atasoglu/seda-v0.1": "transducer (streaming Zipformer2 RNN-T)",
    # checked but not supported for Turkish (documented, not run)
    "nvidia/canary-1b-v2": "not run: Turkish not in the model card language list",
    "nvidia/parakeet-tdt-0.6b-v3": "not run: Turkish not in the model card language list",
}


def main():
    api = HfApi()
    out = {}
    for model, role in MODELS.items():
        try:
            info = api.model_info(model)
            out[model] = {"revision": info.sha, "role": role,
                          "last_modified": str(info.last_modified),
                          "url": f"https://huggingface.co/{model}/tree/{info.sha}"}
            print(f"{model:45s} {info.sha}")
        except Exception as e:
            out[model] = {"revision": "LOOKUP_FAILED", "role": role, "error": str(e)}
            print(f"Could not resolve {model}: {e}")
    REVISIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    REVISIONS_FILE.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {REVISIONS_FILE}")


if __name__ == "__main__":
    main()
