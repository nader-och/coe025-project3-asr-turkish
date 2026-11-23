# Turkish Automatic Speech Recognition — Project 3 Report

**Course:** COE025 Natural Language Processing, Istinye University, Fall 2026
**Team:** Çınar Sabancı (Part 1 – Data), Bashir Alzoubi (Part 2 – Baselines), Nader Ochen (Part 3 – Contribution and evaluation)
**Language:** Turkish

---

## Abstract

We evaluate Turkish speech recognition with {{BASELINES_RUN}} pretrained baselines from the Week 9 model
families (attention encoder-decoder, wav2vec 2.0 + CTC, transducer, and a pretrained multilingual ASR
checkpoint) and with our own contribution: CTC fine-tuning of a Turkish wav2vec 2.0 checkpoint on our
training split. All systems are scored on the same {{TEST_UTT}} speaker-separated test clips from Mozilla
Common Voice Turkish (release {{DATASET_VERSION}}) with one normalization policy. The best baseline is
{{BEST_BASELINE}} with {{BEST_BASELINE_WER}} WER. Our fine-tuned model reaches {{FT_WER}} WER
({{FT_CER}} CER), a change of {{FT_DELTA}} against its starting checkpoint ({{FT_DELTA_CI}} points,
95% speaker-bootstrap interval). {{FT_VERDICT}}

## 1. Task and language

The task is automatic speech recognition: Turkish speech in, a Turkish transcript out (same language).
Turkish is not English and not the mother tongue of any group member, and it was approved for our group.
Turkish is agglutinative: suffixes create many word forms (*ev, evler, evlerimizden*), so one wrong suffix
makes a whole word wrong. This is why we report CER next to WER.

## 2. Data (Part 1 – Çınar Sabancı)

**Dataset.** Mozilla Common Voice Scripted Speech, Turkish, release {{DATASET_VERSION}}. Volunteers read
prompted sentences; the prompt sentence is the reference transcript, and clips are validated by other
volunteers. References are read-speech prompts with punctuation and casing, not verbatim transcripts of
hesitations; we normalize them (Section 5).

**Split by speaker.** We use the {{SPLIT_MODE}} (`train.tsv`, `dev.tsv`, `test.tsv`). Each speaker
(`client_id`) belongs to only one split; our script checks this and stops otherwise. Common Voice has no
session IDs, and each clip is one short recording, so the speaker is the grouping unit.

**Reduced splits.** To run every system on one free Colab T4 GPU, we reduce each split and keep whole
speakers, in a seeded random order (seed 42), until the split reaches its size. Validation and test keep at
most 20 clips per speaker, so a few very active speakers do not dominate the score. The official Common Voice
27.0 Turkish train split has only 28 speakers (41,465 clips), so for train we allow up to 250 clips per
speaker; a cap of 20 would leave only 560 training clips.

| Split | Speakers | Utterances | Hours |
|---|---:|---:|---:|
| Train | {{TRAIN_SPK}} | {{TRAIN_UTT}} | {{TRAIN_HRS}} |
| Validation | {{VAL_SPK}} | {{VAL_UTT}} | {{VAL_HRS}} |
| Test | {{TEST_SPK}} | {{TEST_UTT}} | {{TEST_HRS}} |

Speakers shared between splits (train–validation / train–test / validation–test): {{SPK_OVERLAP}}.
Test sentences that appear word for word in our training split: {{SENT_OVERLAP}}
(in the full official training split: {{SENT_OVERLAP_FULL}}). Common Voice lets different volunteers read
the same prompt, so a few sentences repeat across splits, read by different speakers. The number is small,
but it can make the fine-tuned model look slightly better on those clips, so we report it.

**Audio.** Every clip is decoded, resampled to 16 kHz mono and stored as 16-bit PCM WAV. The duration is
measured from the decoded audio, so a wrong sample-rate label cannot change the clip length.

## 3. Baselines (Part 2 – Bashir Alzoubi)

A baseline is any system our group did not train. Every baseline is run zero-shot with the language set
to Turkish and downloaded at a fixed Hugging Face commit (`results/model_revisions.json`).

| Family (Week 9) | Checkpoint @ revision | Decoding |
|---|---|---|
| Attention encoder-decoder | `openai/whisper-small` @ {{WHISPER_REV}} | greedy, language=turkish, task=transcribe |
| wav2vec 2.0 + CTC head | `m3hrdadfi/wav2vec2-large-xlsr-turkish` @ {{W2V_REV}} | greedy CTC |
| Transducer (RNN-T) | `atasoglu/seda-v0.1` @ {{RNNT_REV}} | greedy, no language model (sherpa-onnx) |
| Pretrained ASR checkpoint | `Qwen/Qwen3-ASR-0.6B` @ {{QWEN_REV}} | language=Turkish |

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
| Training data | {{TRAIN_UTT}} clips, {{TRAIN_HRS}} h (train split only) |
| Epochs | {{EPOCHS}} |
| Learning rate | {{LR}} (10% warm-up, then linear decay) |
| Effective batch | {{EFF_BATCH}} clips |
| Precision / hardware | fp16 on {{FT_GPU}} |
| Training time | {{TRAIN_MIN}} min |
| Reference characters outside the model vocabulary | {{OOV_RATE}} |

**Choosing the checkpoint without the test set.** After every epoch we score the validation split. Epoch 0
is the starting checkpoint.

| Epoch | Validation WER |
|---:|---:|
| 0 (start) | {{EP0_WER}} |
| 1 | {{EP1_WER}} |
| 2 | {{EP2_WER}} |
| 3 | {{EP3_WER}} |

We keep epoch {{BEST_EPOCH}} (validation WER {{BEST_VAL_WER}}), freeze the model, preprocessing and
decoding, and only then score the test split once.

## 5. Evaluation protocol

- Same {{TEST_UTT}} test clips and the same references for every system (identical clip sets checked: {{IDENTICAL_CLIPS}}).
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
| Whisper small | {{WHISPER_WER}} | {{WHISPER_CI}} | {{WHISPER_CER}} | {{WHISPER_SDI}} | {{WHISPER_RTF}} |
| wav2vec2 XLSR Turkish (CTC) | {{W2V_WER}} | {{W2V_CI}} | {{W2V_CER}} | {{W2V_SDI}} | {{W2V_RTF}} |
| seda v0.1 (RNN-T) | {{RNNT_WER}} | {{RNNT_CI}} | {{RNNT_CER}} | {{RNNT_SDI}} | {{RNNT_RTF}} |
| Qwen3-ASR 0.6B | {{QWEN_WER}} | {{QWEN_CI}} | {{QWEN_CER}} | {{QWEN_SDI}} | {{QWEN_RTF}} |

RTF for seda was measured on CPU (sherpa-onnx); the others on {{GPU}}.

### 6.2 Our contribution (trained by our group)

| System | WER | 95% CI | CER | S / D / I | RTF |
|---|---:|---|---:|---|---:|
| wav2vec2 XLSR Turkish + our fine-tuning | {{FT_WER}} | {{FT_CI}} | {{FT_CER}} | {{FT_SDI}} | {{FT_RTF}} |

Change against the starting checkpoint on identical clips: **{{FT_DELTA}}** (95% interval {{FT_DELTA_CI}}).
{{FT_VERDICT}}

## 7. Error analysis

We put the word errors of {{ERR_SYS}} into categories (`src/error_analysis.py`; full tables and examples in
`results/error_analysis/`):

| Category | Count |
|---|---:|
| Substitution – same stem, different suffix | {{ERR_SUFFIX}} |
| Substitution – Turkish letter only (ç/c, ğ/g, ı/i, ö/o, ş/s, ü/u) | {{ERR_LETTER}} |
| Substitution – other | {{ERR_OTHER}} |
| Deletion | {{ERR_DEL}} |
| Insertion | {{ERR_INS}} |
| Clips wrong only because of word spacing | {{ERR_SPACE}} |

Suffix errors are {{ERR_SUFFIX_SHARE}} of the substitutions and Turkish-letter errors {{ERR_LETTER_SHARE}}.

Examples from the test split:

| Type | Reference | Hypothesis | Error |
|---|---|---|---|
| Suffix | {{EX1_REF}} | {{EX1_HYP}} | {{EX1_ERR}} |
| Turkish letter | {{EX2_REF}} | {{EX2_HYP}} | {{EX2_ERR}} |
| Other | {{EX3_REF}} | {{EX3_HYP}} | {{EX3_ERR}} |

A suffix error keeps the meaning of the stem but can change number, case or person, so WER counts it as a
full word error while CER counts only the changed letters. This is why the two metrics are reported together.

## 8. Limitations

1. **Read speech only.** Common Voice is prompted read speech; noisy or spontaneous speech may be harder.
2. **Reduced splits.** {{TEST_UTT}} test clips from {{TEST_SPK}} speakers. The confidence intervals show the
   resulting uncertainty.
3. **Possible pretraining overlap.** `m3hrdadfi/wav2vec2-large-xlsr-turkish` was trained on the Common Voice
   Turkish train and validation splits of an older release, so some of our test speakers or sentences may
   have been in its training data. Whisper and Qwen3-ASR do not publish their training data. `seda-v0.1` was
   trained on the Common Voice 27.0 train split with dev/test sentences removed.
4. **Short fine-tuning, few training speakers.** {{EPOCHS}} epochs on {{TRAIN_HRS}} h from {{TRAIN_SPK}}
   speakers (the official train split has only 28). More speakers would likely help the model generalize to
   the {{TEST_SPK}} unseen test speakers.
5. **Families not run.** MFCC + GMM-HMM, HuBERT + CTC and hybrid CTC/attention (Section 3).

## 9. Conclusion

Among the baselines, {{BEST_BASELINE}} gave the lowest test WER ({{BEST_BASELINE_WER}}). Fine-tuning the
Turkish wav2vec 2.0 checkpoint on our training split gave {{FT_WER}} WER. {{FT_VERDICT}} Next steps: train on
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
