# Baselines (Part 2 - Bashir Alzoubi)

A baseline is any system that our group did not train. All of them are run zero-shot with the
language set to Turkish, on the same test clips, with the same normalization and scoring.
Exact commits are recorded by `src/record_model_revisions.py` in `results/model_revisions.json`,
and every model is downloaded at that commit.

## Run

| Week 9 family | Checkpoint | Why it qualifies | Script |
|---|---|---|---|
| Attention encoder-decoder | `openai/whisper-small` | multilingual checkpoint (not `.en`), Turkish supported | `evaluate_whisper.py` (language=turkish, task=transcribe, greedy) |
| wav2vec 2.0 + CTC head (CTC encoder) | `m3hrdadfi/wav2vec2-large-xlsr-turkish` | XLSR-53 encoder with a CTC head fine-tuned for Turkish ASR by its author - a published fine-tuned checkpoint, so a baseline | `evaluate_wav2vec2.py` (greedy CTC) |
| Transducer (RNN-T) | `atasoglu/seda-v0.1` | Turkish streaming Zipformer2 transducer, Apache-2.0 | `evaluate_transducer.py` (sherpa-onnx, greedy, no LM) |
| Pretrained ASR checkpoint | `Qwen/Qwen3-ASR-0.6B` | Turkish is in the supported language list of `qwen-asr` | `evaluate_qwen3.py` (language=Turkish) |

## Checked and not run

| Checkpoint / method | Reason | Evidence |
|---|---|---|
| `nvidia/canary-1b-v2` | Turkish is not among its 25 supported languages. We do not run it with a wrong language setting. | https://huggingface.co/nvidia/canary-1b-v2 |
| `nvidia/parakeet-tdt-0.6b-v3` | Same 25 European languages; Turkish is not listed (v2 is English only). | https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3 |
| HuBERT + CTC head | We found no published Turkish HuBERT checkpoint with an ASR head. A bare HuBERT encoder has no transcript-token head and cannot transcribe. | https://huggingface.co/asafaya |
| MFCC + GMM-HMM | There is no ready Turkish GMM-HMM system to run; it needs a Turkish pronunciation lexicon, phone set and a Kaldi recipe. Not implemented in the time available. | Week 9 slides 35-41 |
| Hybrid CTC/attention | No Turkish checkpoint with a model card was identified. Whisper represents the attention encoder-decoder family. | - |

## Known data overlap risks (reported, not hidden)

- `m3hrdadfi/wav2vec2-large-xlsr-turkish` was trained on the Common Voice Turkish train and
  validation splits of an older release. Some of our test speakers or sentences may have been
  in its training data, which would make its score look better than for new speakers.
- `atasoglu/seda-v0.1` reports training on the Common Voice 27.0 Turkish **train** split, with
  sentences from the dev/test splits removed. Because we use the official test split, its test
  speakers should be new to it.
- Whisper and Qwen3-ASR do not publish their exact training data; overlap cannot be ruled out.
