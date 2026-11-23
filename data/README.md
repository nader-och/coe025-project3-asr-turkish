# Data (Part 1 - Çınar Sabancı)

## Dataset

**Mozilla Common Voice, Scripted Speech, Turkish**, release given in `data/dataset_info.json`
(downloaded from Mozilla Data Collective: https://datacollective.mozillafoundation.org).
Volunteers read prompted Turkish sentences aloud; the prompt sentence is the reference transcript,
and every clip in `validated.tsv` was checked by other volunteers. Reference and speech are in the
same language (Turkish).

Annotation contract: the reference is the written prompt sentence (with its punctuation and casing).
It is not a verbatim transcript of hesitations. Before scoring we apply one normalization to every
reference and every hypothesis (see `src/common.py`, version `tr-norm-v1`):
Unicode NFKC, Turkish lowercasing (I→ı, İ→i), apostrophes removed (İstanbul'da → istanbulda),
other punctuation → space, whitespace collapsed. Turkish letters and digits are kept.

## Split rule: by speaker, not by clip

We use the **official Common Voice `train.tsv` / `dev.tsv` / `test.tsv`** split
(`--split-mode official`). Common Voice builds these files so that one speaker (`client_id`)
is in only one split; our script checks this again and stops if any speaker is shared.
The result of the check is in `results/data/overlap_report.json` (must be 0 / 0 / 0).

`--split-mode grouped` is the alternative: group `validated.tsv` by `client_id` and assign whole
speakers to train / validation / test with `GroupShuffleSplit` and a fixed seed (42).

Common Voice has no session or recording-group IDs; each clip is one short recording, so the
speaker is the grouping unit.

## Reduced splits (compute budget)

To run every system on a free Colab GPU we reduce each split, keeping the speaker rule:

1. Validation and test: at most 20 clips per speaker (random, seed 42), so a few very active speakers
   do not dominate the score.
2. Train: at most 250 clips per speaker. The official Common Voice 27.0 Turkish train split has only
   28 speakers (41,465 clips), so a cap of 20 would leave only 560 training clips.
3. Speakers are taken in a seeded random order and kept **whole** until the split reaches its size
   (train 6,000, validation 600, test 2,000 clips).

All systems are scored on exactly these test clips. Sizes before reduction are recorded in
`data/dataset_info.json`.

## Audio

Every selected MP3 clip is decoded, resampled to 16 kHz mono and written as 16-bit PCM WAV
(`data/wav16k/`, not committed). The measured duration of each clip is stored in the manifest.

## What we report (`results/data/`)

- `split_statistics.csv`: speakers, utterances and hours for each split.
- `overlap_report.json`: speakers shared between splits, and how many test sentences appear
  word for word in our training split (and in the full official training split).

## Files

- `manifest.csv`: one row per clip (Common Voice client IDs are replaced by pseudonyms `spk00001`, …) - `clip_id, split, speaker_id, audio_path, source_file, reference, reference_norm, duration_seconds, sample_rate`.
- `dataset_info.json`: release, split mode, seed, caps.

The audio is not in this repository. Download it yourself and follow the Common Voice terms
(do not try to identify speakers).
