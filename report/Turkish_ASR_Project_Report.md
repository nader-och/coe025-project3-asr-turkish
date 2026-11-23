# Turkish Automatic Speech Recognition — Project 3 Report

**Course:** COE025 Natural Language Processing, Istinye University, Fall 2026
**Team:** Çınar Sabancı (Part 1 – Data), Bashir Alzoubi (Part 2 – Baselines), Nader Ochen (Part 3 – Contribution and evaluation)
**Language:** Turkish

---

## Abstract

We evaluate Turkish speech recognition with 4 pretrained baselines from the Week 9 model
families (attention encoder-decoder, wav2vec 2.0 + CTC, transducer, and a pretrained multilingual ASR
checkpoint) and with our own contribution: CTC fine-tuning of a Turkish wav2vec 2.0 checkpoint on our
training split. All systems are scored on the same 2,000 speaker-separated test clips from Mozilla
Common Voice Turkish (release 27.0) with one normalization policy. The best baseline is
seda v0.1 (RNN-T) with 16.1% WER. Our fine-tuned model reaches 30.3% WER
(6.5% CER), a change of -3.6 points against its starting checkpoint (-4.3 to -2.9 points,
95% speaker-bootstrap interval). Fine-tuning lowered test WER by 3.6 points; the 95% interval does not include zero.

## 1. Task and language

The task is automatic speech recognition: Turkish speech in, a Turkish transcript out (same language).
Turkish is not English and not the mother tongue of any group member, and it was approved for our group.
Turkish is agglutinative: suffixes create many word forms (*ev, evler, evlerimizden*), so one wrong suffix
makes a whole word wrong. This is why we report CER next to WER.

## 2. Data (Part 1 – Çınar Sabancı)

**Dataset.** Mozilla Common Voice Scripted Speech, Turkish, release 27.0. Volunteers read
prompted sentences; the prompt sentence is the reference transcript, and clips are validated by other
volunteers. References are read-speech prompts with punctuation and casing, not verbatim transcripts of
hesitations; we normalize them (Section 5).

**Split by speaker.** We use the official Common Voice splits (`train.tsv`, `dev.tsv`, `test.tsv`). Each speaker
(`client_id`) belongs to only one split; our script checks this and stops otherwise. Common Voice has no
session IDs, and each clip is one short recording, so the speaker is the grouping unit.

**Reduced splits.** To run every system on one free Colab T4 GPU, we reduce each split and keep whole
speakers, in a seeded random order (seed 42), until the split reaches its size. Validation and test keep at
most 20 clips per speaker, so a few very active speakers do not dominate the score. The official Common Voice
27.0 Turkish train split has only 28 speakers (41,465 clips), so for train we allow up to 250 clips per
speaker; a cap of 20 would leave only 560 training clips.

| Split | Speakers | Utterances | Hours |
|---|---:|---:|---:|
| Train | 25 | 5,909 | 6.03 |
| Validation | 34 | 600 | 0.60 |
| Test | 293 | 2,000 | 2.49 |

Speakers shared between splits (train–validation / train–test / validation–test): 0 / 0 / 0.
Test sentences that appear word for word in our training split: 11 / 2000
(in the full official training split: 29 / 2000). Common Voice lets different volunteers read
the same prompt, so a few sentences repeat across splits, read by different speakers. The number is small,
but it can make the fine-tuned model look slightly better on those clips, so we report it.

**Audio.** Every clip is decoded, resampled to 16 kHz mono and stored as 16-bit PCM WAV. The duration is
measured from the decoded audio, so a wrong sample-rate label cannot change the clip length.

## 3. Baselines (Part 2 – Bashir Alzoubi)

A baseline is any system our group did not train. Every baseline is run zero-shot with the language set
to Turkish and downloaded at a fixed Hugging Face commit (`results/model_revisions.json`).

| Family (Week 9) | Checkpoint @ revision | Decoding |
|---|---|---|
| Attention encoder-decoder | `openai/whisper-small` @ 973afd2 | greedy, language=turkish, task=transcribe |
| wav2vec 2.0 + CTC head | `m3hrdadfi/wav2vec2-large-xlsr-turkish` @ 8699cf3 | greedy CTC |
| Transducer (RNN-T) | `atasoglu/seda-v0.1` @ 5cbbda1 | greedy, no language model (sherpa-onnx) |
| Pretrained ASR checkpoint | `Qwen/Qwen3-ASR-0.6B` @ 5eb1441 | language=Turkish |

**Checked and not run.** `nvidia/canary-1b-v2` and `nvidia/parakeet-tdt-0.6b-v3` support 25 European
languages and Turkish is not one of them (model cards linked in `docs/baselines.md`); running them with a
wrong language setting would not be a valid result. We found no published Turkish HuBERT checkpoint with an
ASR head, and a bare HuBERT encoder cannot transcribe. MFCC + GMM-HMM has no ready Turkish system and needs a
pronunciation lexicon and a Kaldi recipe; we did not implement it. No Turkish hybrid CTC/attention checkpoint
was identified.

## 4. Our contribution: fine-tuning (Part 3 – Nader Ochen)

We continue training `m3hrdadfi/wav2vec2-large-xlsr-turkish` (wav2vec 2.0 encoder + CTC head) on our
training split with the CTC loss. The CNN feature encoder is frozen; the transformer layers and the CTC head
are updated.

| Setting | Value |
|---|---|
| Training data | 5,909 clips, 6.03 h (train split only) |
| Epochs | 3 |
| Learning rate | 2e-05 (10% warm-up, then linear decay) |
| Effective batch | 16 clips |
| Precision / hardware | fp16 on Tesla T4 |
| Training time | 28 min |
| Reference characters outside the model vocabulary | 0.00% |

**Choosing the checkpoint without the test set.** After every epoch we score the validation split. Epoch 0
is the starting checkpoint.

| Epoch | Validation WER |
|---:|---:|
| 0 (start) | 50.7% |
| 1 | 47.1% |
| 2 | 46.4% |
| 3 | 45.9% |

We keep epoch 3 (validation WER 45.9%), freeze the model, preprocessing and
decoding, and only then score the test split once.

## 5. Evaluation protocol

- Same 2,000 test clips and the same references for every system (identical clip sets checked: yes).
- One normalization (`src/common.py`, `tr-norm-v1`) for references and hypotheses: Unicode NFKC; Turkish
  lowercasing (I→ı, İ→i, because Python's default lowercasing is not Turkish-aware); apostrophes removed
  (*İstanbul'da* = *istanbulda*); other punctuation → space; whitespace collapsed. Turkish letters and digits
  are kept and nothing is transliterated.
- **WER** = (S + D + I) / N, where S, D and I are substituted, deleted and inserted words after the
  minimum-edit alignment and N is the number of reference words. The Hugging Face Audio Course
  (chapter 5, "Evaluation") describes WER as the standard ASR metric. It has no upper bound, because
  insertions add errors without adding reference words. Turkish has clear spaces between words, so WER is
  meaningful and is our main metric.
- **CER** uses the same edit distance on characters. The course explains that CER gives partial credit for
  a word that is almost right, while WER counts a single wrong letter as a whole wrong word. In agglutinative
  Turkish a wrong suffix is exactly this kind of near miss, so we report CER next to WER to show it.
- **Normalization before scoring.** The course recommends normalizing both references and predictions
  (casing, punctuation) before computing WER; we do this with one function for every system.
- Corpus-level scores: total edits / total reference words (or characters), computed with `jiwer`.
- Uncertainty: 95% interval from 1,000 bootstrap resamples of **speakers**, because clips of one speaker are
  not independent. Fine-tuned vs. starting checkpoint: paired bootstrap on identical clips.
- Speed: real-time factor RTF = compute seconds / audio seconds (the course's RTFx is 1 / RTF), with the
  hardware recorded.

## 6. Results (test split)

### 6.1 Baselines (no training by our group)

| System | WER | 95% CI | CER | S / D / I | RTF |
|---|---:|---|---:|---|---:|
| Whisper small | 24.7% | 22.9-26.5% | 8.1% | 2219 / 396 / 283 | 0.016 |
| wav2vec2 XLSR Turkish (CTC) | 33.9% | 31.1-36.8% | 7.4% | 3081 / 434 / 472 | 0.021 |
| seda v0.1 (RNN-T) | 16.1% | 14.9-17.5% | 4.6% | 1452 / 265 / 175 | 0.072 |
| Qwen3-ASR 0.6B | 22.6% | 21.4-23.9% | 7.0% | 2090 / 373 / 194 | 0.057 |

RTF for seda was measured on CPU (sherpa-onnx); the others on Tesla T4.

### 6.2 Our contribution (trained by our group)

| System | WER | 95% CI | CER | S / D / I | RTF |
|---|---:|---|---:|---|---:|
| wav2vec2 XLSR Turkish + our fine-tuning | 30.3% | 27.5-33.2% | 6.5% | 2875 / 488 / 202 | 0.021 |

Change against the starting checkpoint on identical clips: **-3.6 points** (95% interval -4.3 to -2.9).
Fine-tuning lowered test WER by 3.6 points; the 95% interval does not include zero.

## 7. Error analysis

We put the word errors of our fine-tuned wav2vec2 into categories (`src/error_analysis.py`; full tables and examples in
`results/error_analysis/`):

| Category | Count |
|---|---:|
| Substitution – same stem, different suffix | 1,161 |
| Substitution – Turkish letter only (ç/c, ğ/g, ı/i, ö/o, ş/s, ü/u) | 28 |
| Substitution – other | 1,686 |
| Deletion | 488 |
| Insertion | 202 |
| Clips wrong only because of word spacing | 78 |

Suffix errors are 40.4% of the substitutions and Turkish-letter errors 1.0%.

Examples from the test split:

| Type | Reference | Hypothesis | Error |
|---|---|---|---|
| Suffix | Sanatta herşey kendi yerine düşer. | sanatda herşey kendi yerne düşer | sanatta -> sanatda |
| Turkish letter | Suyun yanından geçip gidermiş, bir de ne görsün: | suun yanından geçip gidermiş birde ne görsun | görsün -> görsun |
| Other | Seçimlerde usulsüzlük bildirilmedi. | seçimlerde ulsözsüzlük bildirilmedi | usulsüzlük -> ulsözsüzlük |

A suffix error keeps the meaning of the stem but can change number, case or person, so WER counts it as a
full word error while CER counts only the changed letters. This is why the two metrics are reported together.

## 8. Limitations

1. **Read speech only.** Common Voice is prompted read speech; noisy or spontaneous speech may be harder.
2. **Reduced splits.** 2,000 test clips from 293 speakers. The confidence intervals show the
   resulting uncertainty.
3. **Possible pretraining overlap.** `m3hrdadfi/wav2vec2-large-xlsr-turkish` was trained on the Common Voice
   Turkish train and validation splits of an older release, so some of our test speakers or sentences may
   have been in its training data. Whisper and Qwen3-ASR do not publish their training data. `seda-v0.1` was
   trained on the Common Voice 27.0 train split with dev/test sentences removed.
4. **Short fine-tuning, few training speakers.** 3 epochs on 6.03 h from 25
   speakers (the official train split has only 28). More speakers would likely help the model generalize to
   the 293 unseen test speakers.
5. **Families not run.** MFCC + GMM-HMM, HuBERT + CTC and hybrid CTC/attention (Section 3).

## 9. Conclusion

Among the baselines, seda v0.1 (RNN-T) gave the lowest test WER (16.1%). Fine-tuning the
Turkish wav2vec 2.0 checkpoint on our training split gave 30.3% WER. Fine-tuning lowered test WER by 3.6 points; the 95% interval does not include zero. Next steps: train on
the full training split, add a language model for CTC decoding (tuned on validation), and implement an
MFCC + GMM-HMM system as the classical baseline.

## Team contributions

| Student | Contribution |
|---|---|
| Çınar Sabancı | Dataset selection and download, speaker-separated splits, audio conversion, split statistics, sentence-overlap check (`src/prepare_common_voice.py`, `data/`) |
| Bashir Alzoubi | Baseline selection by language support, model revisions, evaluation of Whisper, wav2vec2, Qwen3-ASR and the transducer, documentation of excluded models (`src/evaluate_*.py`, `docs/baselines.md`) |
| Nader Ochen | Shared normalization and scoring, fine-tuning, final test evaluation, paired comparison, error analysis, report and presentation (`src/common.py`, `src/train_wav2vec2.py`, `src/summarize_results.py`, `src/error_analysis.py`) |

## References

- Mozilla Common Voice datasets — https://datacollective.mozillafoundation.org
- Hugging Face Audio Course, chapter 5 "Evaluation" — https://huggingface.co/learn/audio-course/en/chapter5/evaluation
- Jurafsky & Martin, *Speech and Language Processing*, chapters 14–15 (Week 9 slides)
- openai/whisper-small — https://huggingface.co/openai/whisper-small
- m3hrdadfi/wav2vec2-large-xlsr-turkish — https://huggingface.co/m3hrdadfi/wav2vec2-large-xlsr-turkish
- atasoglu/seda-v0.1 — https://huggingface.co/atasoglu/seda-v0.1
- Qwen/Qwen3-ASR-0.6B — https://huggingface.co/Qwen/Qwen3-ASR-0.6B
- nvidia/canary-1b-v2 — https://huggingface.co/nvidia/canary-1b-v2
- nvidia/parakeet-tdt-0.6b-v3 — https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3
- JiWER — https://github.com/jitsi/jiwer
