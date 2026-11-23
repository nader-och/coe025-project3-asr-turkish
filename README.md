# Project 3 — Turkish Automatic Speech Recognition

COE025 Natural Language Processing, Istinye University, Fall 2026.

We compare pretrained Turkish speech recognizers from the Week 9 model families (baselines) with a
wav2vec 2.0 model that **we fine-tuned on our own training split** (our contribution).
Every system is scored on the same speaker-separated test clips with one normalization policy,
using WER and CER.

**Results:** [`results/RESULTS.md`](results/RESULTS.md) · **Report:** [`report/Turkish_ASR_Project_Report.md`](report/Turkish_ASR_Project_Report.md) · **Slides:** [`presentation/Turkish_ASR_Presentation.pptx`](presentation/Turkish_ASR_Presentation.pptx)

## Team

| Student | Part | Files |
|---|---|---|
| Çınar Sabancı | **Part 1 — Data**: dataset, speaker-separated splits, audio preparation, split statistics, sentence-overlap check | `src/prepare_common_voice.py`, `data/`, `results/data/` |
| Bashir Alzoubi | **Part 2 — Baselines**: model selection by language support, pinned revisions, zero-shot evaluation of every supported family | `src/record_model_revisions.py`, `src/evaluate_whisper.py`, `src/evaluate_wav2vec2.py`, `src/evaluate_qwen3.py`, `src/evaluate_transducer.py`, `docs/baselines.md`, `results/baseline_matrix.csv`, `results/model_revisions.json`, baseline folders in `results/systems/` |
| Nader Ochen | **Part 3 — Contribution and evaluation**: shared scoring and normalization, fine-tuning, final test evaluation, comparison, error analysis, report and slides | `src/common.py`, `src/train_wav2vec2.py`, `src/summarize_results.py`, `src/error_analysis.py`, `src/fill_results.py`, `notebooks/`, `results/training/`, `results/systems/wav2vec2_xlsr_tr_finetuned/`, `results/error_analysis/`, `report/`, `presentation/` |

## Language and data

- **Language:** Turkish (not English and not the mother tongue of any group member).
- **Dataset:** Mozilla Common Voice Scripted Speech, Turkish (release in `data/dataset_info.json`).
- **Split:** the official Common Voice train / dev / test files. No speaker appears in two splits
  (checked by our script, `results/data/overlap_report.json`). Splits are reduced by keeping whole
  speakers (validation/test: at most 20 clips per speaker; train: at most 250, because the official
  train split has only 28 speakers). Details: [`data/README.md`](data/README.md).
- The validation split chooses the fine-tuning epoch. The test split is used once, at the end.

## Systems

| Role | System | Week 9 family |
|---|---|---|
| Baseline | `openai/whisper-small` | attention encoder-decoder |
| Baseline | `m3hrdadfi/wav2vec2-large-xlsr-turkish` | wav2vec 2.0 + CTC head |
| Baseline | `atasoglu/seda-v0.1` | transducer (RNN-T) |
| Baseline | `Qwen/Qwen3-ASR-0.6B` | pretrained ASR checkpoint |
| **Contribution** | `m3hrdadfi/wav2vec2-large-xlsr-turkish` **+ our CTC fine-tuning** | wav2vec 2.0 + CTC head |

Not run, with the reason and model-card link: Canary-1B-v2 and Parakeet-TDT-0.6B-v3 (Turkish not
supported), HuBERT + CTC (no Turkish ASR checkpoint), MFCC + GMM-HMM, hybrid CTC/attention.
See [`docs/baselines.md`](docs/baselines.md). Exact commits: `results/model_revisions.json`.

## Evaluation

- **WER** = (S + D + I) / N reference words: the standard ASR metric according to the Hugging Face
  Audio Course, chapter 5 "Evaluation" (https://huggingface.co/learn/audio-course/en/chapter5/evaluation).
  Turkish separates words with spaces, so WER is meaningful and is our main metric.
- **CER** = the same edit distance on characters. The course notes that CER gives partial credit for
  near-miss words, while WER counts one wrong letter as a wrong word. Turkish is agglutinative, so a
  wrong suffix is a typical near miss; we report CER next to WER to show this.
- References and predictions are normalized the same way before scoring, as the course recommends.
- Corpus-level scores (total edits / total reference words), with a 95% interval from resampling
  **speakers**, because clips of one speaker are not independent.
- Fine-tuned vs. its starting checkpoint: paired comparison on identical clips.
- Also reported: S / D / I counts, real-time factor (compute seconds / audio seconds), hardware.
- Normalization (`src/common.py`, `tr-norm-v1`): NFKC, Turkish lowercasing (I→ı, İ→i),
  apostrophes removed, other punctuation → space, whitespace collapsed. Same for all systems.

## How to reproduce

The easiest way is Google Colab with a T4 GPU: open
[`notebooks/run_all_colab.ipynb`](notebooks/run_all_colab.ipynb) and run all cells.
Locally (Python 3.10–3.12, CUDA GPU recommended):

```bash
pip install -r requirements.txt
pip install qwen-asr sherpa-onnx

# Part 1 - data (Common Voice Turkish extracted into data/common_voice_tr/)
python src/prepare_common_voice.py --cv-dir data/common_voice_tr --dataset-version 27.0 --seed 42 \
    --max-clips-per-speaker 20 --train-max-clips-per-speaker 250

# Part 2 - baselines
python src/record_model_revisions.py
python src/evaluate_whisper.py
python src/evaluate_wav2vec2.py
python src/evaluate_qwen3.py
python src/evaluate_transducer.py

# Part 3 - fine-tuning (train + validation only), then one test evaluation
python src/train_wav2vec2.py --epochs 3 --lr 2e-5 --batch-size 8 --grad-accum 2
python src/evaluate_wav2vec2.py --model results/checkpoints/wav2vec2_finetuned/best \
    --tag wav2vec2_xlsr_tr_finetuned --role contribution --base-model m3hrdadfi/wav2vec2-large-xlsr-turkish

# Results
python src/summarize_results.py
python src/error_analysis.py
python src/fill_results.py
```

Each system writes `results/systems/<tag>/` with `predictions.csv` (clip ID, reference,
hypothesis, error counts), `metrics.json` and `run_manifest.json` (model, revision, settings,
dataset release, normalization, package versions, GPU, timing).

## Repository layout

```text
src/            scripts (one per step)
notebooks/      Colab notebook that runs everything
data/           manifest and dataset notes (audio not included)
docs/           baseline selection and exclusions
results/        split statistics, per-system predictions and metrics, training log, error analysis
report/         project report (report_source.md is filled by src/fill_results.py)
presentation/   slides (slides_source.pptx is filled by src/fill_results.py)
```

## Limitations

- Common Voice is read speech; results may not hold for spontaneous or noisy speech.
- Reduced splits (2,000 test clips) give wider confidence intervals than the full test set.
- Possible pretraining overlap: see [`docs/baselines.md`](docs/baselines.md).
- Fine-tuning ran for 3 epochs on about 6,000 clips from only 25 training speakers (the official
  Common Voice 27.0 Turkish train split has 28 speakers).

## Data terms

Common Voice audio is not redistributed here; download it from Mozilla and follow its terms.
