"""Part 3 - Our contribution: fine-tune a Turkish wav2vec 2.0 + CTC checkpoint on OUR training split.

- Only the train split updates the weights.
- The validation split is scored after every epoch (WER); the best epoch is kept.
- The test split is never read here. It is scored once, later, with evaluate_wav2vec2.py.

Outputs
  results/checkpoints/wav2vec2_finetuned/best/   fine-tuned model (large, not committed)
  results/training/training_summary.json         settings, data sizes, best epoch, validation WER per epoch
  results/training/log_history.json              full Trainer log (loss, learning rate, validation metrics)
"""
import argparse
import json
import time
from dataclasses import dataclass

import numpy as np
import torch
from transformers import Trainer, TrainingArguments, Wav2Vec2ForCTC, Wav2Vec2Processor, set_seed

from common import RESULTS, environment_info, load_audio, load_manifest, local_model_path, normalize_tr


class SpeechDataset(torch.utils.data.Dataset):
    def __init__(self, frame, processor):
        self.paths = list(frame["audio_path"])
        self.texts = [normalize_tr(x) for x in frame["reference"]]
        self.processor = processor

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, i):
        audio = load_audio(self.paths[i])
        values = self.processor.feature_extractor(audio, sampling_rate=16000).input_values[0]
        labels = self.processor.tokenizer(self.texts[i]).input_ids
        return {"input_values": values, "labels": labels}


@dataclass
class DataCollatorCTCWithPadding:
    """Pads audio and labels in a batch; padded label positions become -100 so the CTC loss ignores them."""
    processor: Wav2Vec2Processor

    def __call__(self, features):
        audio = [{"input_values": f["input_values"]} for f in features]
        labels = [{"input_ids": f["labels"]} for f in features]
        batch = self.processor.feature_extractor.pad(audio, padding=True, return_tensors="pt")
        lab = self.processor.tokenizer.pad(labels, padding=True, return_tensors="pt")
        batch["labels"] = lab["input_ids"].masked_fill(lab["attention_mask"].ne(1), -100)
        return batch


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="m3hrdadfi/wav2vec2-large-xlsr-turkish")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--grad-accum", type=int, default=2)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--output", default=str(RESULTS / "checkpoints" / "wav2vec2_finetuned"))
    args = ap.parse_args()
    set_seed(args.seed)

    train_df, val_df = load_manifest("train"), load_manifest("validation")
    if train_df.empty or val_df.empty:
        raise SystemExit("Empty train or validation split. Run src/prepare_common_voice.py first.")

    path, revision = local_model_path(args.model)
    processor = Wav2Vec2Processor.from_pretrained(path)
    model = Wav2Vec2ForCTC.from_pretrained(
        path, ctc_loss_reduction="mean", ctc_zero_infinity=True,
        pad_token_id=processor.tokenizer.pad_token_id)
    model.freeze_feature_encoder()  # CNN feature encoder stays fixed; transformer layers + CTC head train

    # Characters the tokenizer cannot produce become [UNK]; report how many there are.
    vocab = set(processor.tokenizer.get_vocab())
    train_chars = "".join(normalize_tr(x) for x in train_df["reference"]).replace(" ", "")
    oov = sorted({c for c in train_chars if c not in vocab})
    oov_rate = sum(c not in vocab for c in train_chars) / max(len(train_chars), 1)

    train_ds, val_ds = SpeechDataset(train_df, processor), SpeechDataset(val_df, processor)

    def logits_to_ids(logits, labels):
        return torch.argmax(logits, dim=-1)

    def compute_metrics(pred):
        import jiwer
        ids = pred.predictions
        label_ids = pred.label_ids.copy()
        label_ids[label_ids == -100] = processor.tokenizer.pad_token_id
        hyps = [normalize_tr(x) for x in processor.batch_decode(ids)]
        refs = [normalize_tr(x) for x in processor.batch_decode(label_ids, group_tokens=False)]
        keep = [i for i, r in enumerate(refs) if r]
        refs, hyps = [refs[i] for i in keep], [hyps[i] for i in keep]
        return {"wer": jiwer.wer(refs, hyps), "cer": jiwer.cer(refs, hyps)}

    cuda = torch.cuda.is_available()
    targs = TrainingArguments(
        output_dir=args.output,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        warmup_ratio=0.1,
        num_train_epochs=args.epochs,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="wer",
        greater_is_better=False,
        save_total_limit=2,
        logging_steps=25,
        fp16=cuda,
        gradient_checkpointing=True,
        dataloader_num_workers=2,
        remove_unused_columns=False,
        seed=args.seed,
        report_to="none",
    )
    trainer = Trainer(model=model, args=targs, train_dataset=train_ds, eval_dataset=val_ds,
                      data_collator=DataCollatorCTCWithPadding(processor),
                      processing_class=processor.feature_extractor,
                      compute_metrics=compute_metrics, preprocess_logits_for_metrics=logits_to_ids)

    start = time.time()
    epoch0 = trainer.evaluate()  # validation score of the starting checkpoint (epoch 0)
    trainer.train()
    minutes = (time.time() - start) / 60

    best_dir = f"{args.output}/best"
    trainer.save_model(best_dir)
    processor.save_pretrained(best_dir)

    per_epoch = [{"epoch": 0, "validation_wer": epoch0["eval_wer"], "validation_cer": epoch0["eval_cer"]}]
    per_epoch += [{"epoch": round(h["epoch"]), "validation_wer": h["eval_wer"], "validation_cer": h["eval_cer"]}
                  for h in trainer.state.log_history if "eval_wer" in h and (h.get("epoch") or 0) > 0]
    best = min(per_epoch[1:], key=lambda r: r["validation_wer"])
    summary = {
        "base_model": args.model, "base_revision": revision,
        "method": "CTC fine-tuning of all transformer layers and the CTC head; CNN feature encoder frozen",
        "train_utterances": len(train_df), "train_hours": round(train_df["duration_seconds"].sum() / 3600, 3),
        "validation_utterances": len(val_df),
        "settings": {"epochs": args.epochs, "learning_rate": args.lr, "batch_size": args.batch_size,
                     "gradient_accumulation": args.grad_accum,
                     "effective_batch": args.batch_size * args.grad_accum,
                     "warmup_ratio": 0.1, "fp16": cuda, "seed": args.seed},
        "characters_not_in_vocab": oov, "oov_character_rate": round(oov_rate, 5),
        "validation_by_epoch": per_epoch,
        "best_epoch": best["epoch"], "best_validation_wer": best["validation_wer"],
        "selection_rule": "lowest validation WER; test split not used",
        "training_minutes": round(minutes, 1),
        "environment": environment_info(),
    }
    out = RESULTS / "training"
    out.mkdir(parents=True, exist_ok=True)
    (out / "training_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "log_history.json").write_text(json.dumps(trainer.state.log_history, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ["validation_by_epoch", "best_epoch", "training_minutes"]}, indent=2))
    print(f"Best checkpoint: {best_dir}")
    print("Settings are now frozen. Next: evaluate this checkpoint once on the test split.")


if __name__ == "__main__":
    main()
