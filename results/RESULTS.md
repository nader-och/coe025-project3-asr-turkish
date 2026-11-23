# Results

Dataset: Mozilla Common Voice - Turkish (Scripted Speech), release 27.0, split mode: official, seed 42.

## Data splits

| split      |   speakers |   utterances |   hours |   mean_clip_seconds |
|:-----------|-----------:|-------------:|--------:|--------------------:|
| train      |         25 |         5909 |   6.032 |                3.68 |
| validation |         34 |          600 |   0.602 |                3.61 |
| test       |        293 |         2000 |   2.494 |                4.49 |

Speaker overlap between splits: {'train-validation': 0, 'train-test': 0, 'validation-test': 0}. Test sentences that appear word for word in our training split: 11 / 2000 (in the full official train split: 29).

## Baselines (no training by our group)

| System | Checkpoint @ revision | Family | WER | 95% CI (speakers) | CER | S / D / I | Clips | RTF |
|---|---|---|---:|---|---:|---|---:|---:|
| seda_rnnt | `atasoglu/seda-v0.1` @ 5cbbda1b34bd | transducer (Zipformer2 RNN-T, streaming) | 16.10% | 14.87% - 17.46% | 4.60% | 1452 / 265 / 175 | 2000 | 0.0724 |
| qwen3_asr_0.6b | `Qwen/Qwen3-ASR-0.6B` @ 5eb144179a02 | pretrained ASR checkpoint (Qwen3-ASR) | 22.61% | 21.40% - 23.91% | 7.00% | 2090 / 373 / 194 | 2000 | 0.0573 |
| whisper_small | `openai/whisper-small` @ 973afd24965f | attention encoder-decoder (Whisper) | 24.66% | 22.94% - 26.47% | 8.07% | 2219 / 396 / 283 | 2000 | 0.0164 |
| wav2vec2_xlsr_tr | `m3hrdadfi/wav2vec2-large-xlsr-turkish` @ 8699cf317b8f | wav2vec 2.0 + CTC head | 33.93% | 31.09% - 36.84% | 7.38% | 3081 / 434 / 472 | 2000 | 0.0211 |

## Our contribution (trained by our group)

| System | Checkpoint @ revision | Family | WER | 95% CI (speakers) | CER | S / D / I | Clips | RTF |
|---|---|---|---:|---|---:|---|---:|---:|
| wav2vec2_xlsr_tr_finetuned | `results/checkpoints/wav2vec2_finetuned/best` @ local | wav2vec 2.0 + CTC head | 30.34% | 27.54% - 33.18% | 6.53% | 2875 / 488 / 202 | 2000 | 0.0211 |

Paired comparison on 2000 identical test clips: WER(wav2vec2_xlsr_tr_finetuned) - WER(wav2vec2_xlsr_tr) = -3.59 points (95% speaker-bootstrap interval -4.32 to -2.88).

## Fine-tuning: validation WER by epoch (test not used)

|   epoch | validation_wer   | validation_cer   |
|--------:|:-----------------|:-----------------|
|       0 | 50.74%           | 18.65%           |
|       1 | 47.06%           | 17.73%           |
|       2 | 46.42%           | 17.56%           |
|       3 | 45.89%           | 17.50%           |

Selected epoch: 3 (lowest validation WER).

## Baselines not run, and why

| family                    | checkpoint_or_method                     | turkish_support                                | status        | evidence_or_reason                                                                                                                                                     |
|:--------------------------|:-----------------------------------------|:-----------------------------------------------|:--------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Pretrained ASR checkpoint | nvidia/canary-1b-v2                      | no (25 European languages; Turkish not listed) | not_supported | https://huggingface.co/nvidia/canary-1b-v2                                                                                                                             |
| Pretrained ASR checkpoint | nvidia/parakeet-tdt-0.6b-v3              | no (25 European languages; Turkish not listed) | not_supported | https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3                                                                                                                     |
| HuBERT + CTC head         | no Turkish HuBERT + CTC checkpoint found | not available                                  | not_run       | HuBERT-TR (Safaya & Erzin 2022) is not on the authors' Hugging Face page (https://huggingface.co/asafaya); a bare HuBERT encoder has no ASR head and cannot transcribe |
| Classical                 | MFCC + GMM-HMM                           | possible only if we train it                   | not_run       | No ready Turkish GMM-HMM system; needs a Turkish lexicon and a Kaldi recipe; not implemented in the time available                                                     |
| Hybrid CTC/attention      | no Turkish checkpoint identified         | not verified                                   | not_run       | No Turkish hybrid CTC/attention checkpoint with a model card was identified; Whisper represents the attention encoder-decoder family                                   |

Scoring: corpus-level WER and CER (total edits / total reference words or characters) after one shared Turkish normalization (src/common.py). RTF = compute seconds / audio seconds.
