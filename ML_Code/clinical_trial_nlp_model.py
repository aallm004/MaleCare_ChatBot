"""
Clinical Trial Chatbot - NLP Training

Module for training the NLP models for intent classification and entity
extraction.
"""

import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    TrainingArguments,
    Trainer,
    DataCollatorForTokenClassification,
    TrainerCallback
)
import pandas as pd
from typing import List, Dict, Tuple
import seqeval
import evaluate


class PrinterCallback(TrainerCallback):
    """Callback to print training progress"""

    def on_epoch_begin(self, args, state, control, **kwargs):
        """Called at the beginning of each epoch"""
        print(f"\n{'='*60}")
        print(f"Starting Epoch {state.epoch + 1}/{state.num_train_epochs}")
        print(f"{'='*60}")

    def on_log(self, args, state, control, logs=None, **kwargs):
        """Called when logging occurs"""
        if logs:
            # Print training loss
            if 'loss' in logs:
                print(f"  Step {state.global_step} - Training Loss: {logs['loss']:.4f}")

            # Print learning rate
            if 'learning_rate' in logs:
                print(f"  Learning Rate: {logs['learning_rate']:.2e}")

    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        """Called after evaluation"""
        if metrics:
            print(f"\n{'─'*60}")
            print(f"Evaluation Results (Epoch {state.epoch}):")
            print(f"{'─'*60}")
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    print(f"  {key}: {value:.4f}")
            print(f"{'─'*60}\n")


class IntentDataset(Dataset):
    """Dataset for intent classification"""

    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }


class IntentClassifier:
    """Intent classification model using BioClinicalBERT"""

    def __init__(self, model_name='emilyalsentzer/Bio_ClinicalBERT',
                 num_labels=10):
        """Initialize the intent classifier.

        Args:
            model_name: Pretrained model to use (BioClinicalBERT)
            num_labels: Number of intent classes
        """
        self.model_name = model_name
        self.num_labels = num_labels
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = None
        self.label_map = {}
        self.reverse_label_map = {}

    def prepare_data(self, training_data: List[Dict]):
        """Prepare training data from list of dictionaries.

        Args:
            training_data: List of dictionaries with 'text' and 'intent' keys

        Returns:
            Tuple of (texts, encoded_labels)
        """
        texts = [item['text'] for item in training_data]
        intents = [item['intent'] for item in training_data]

        # Create label mapping
        unique_intents = sorted(list(set(intents)))
        self.label_map = {intent: idx for idx, intent in
                          enumerate(unique_intents)}
        self.reverse_label_map = {idx: intent for intent, idx in
                                  self.label_map.items()}

        # Encode labels
        encoded_labels = [self.label_map[intent] for intent in intents]

        return texts, encoded_labels

    def train(self, training_data: List[Dict],
              validation_split=0.2,
              epochs=20,
              batch_size=16,
              learning_rate=2e-5,
              output_dir='./intent_model'):
        """Train the intent classification model.

        Args:
            training_data: List of training examples
            validation_split: Fraction of data to use for validation
            epochs: Number of epochs
            batch_size: Batch size for training
            learning_rate: Learning rate
            output_dir: Directory to save the model
        """
        # Prepare data
        texts, labels = self.prepare_data(training_data)

        # Split into train and validation
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=validation_split, random_state=42,
            stratify=labels)

        print(f"\n{'='*60}")
        print(f"Training Configuration:")
        print(f"{'='*60}")
        print(f"Training samples: {len(train_texts)}")
        print(f"Validation samples: {len(val_texts)}")
        print(f"Intent classes: {list(self.label_map.keys())}")
        print(f"Number of classes: {len(self.label_map)}")
        print(f"Epochs: {epochs}")
        print(f"Batch size: {batch_size}")
        print(f"Learning rate: {learning_rate}")
        print(f"{'='*60}\n")

        # Create datasets
        train_dataset = IntentDataset(train_texts, train_labels,
                                      self.tokenizer)
        val_dataset = IntentDataset(val_texts, val_labels, self.tokenizer)

        # Initialize model
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=len(self.label_map)
        )

        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            eval_strategy="epoch",
            save_strategy="no",
            save_total_limit=1,
            load_best_model_at_end=False,
            metric_for_best_model="eval_loss",
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir=f'{output_dir}/logs',
            logging_steps=10
        )

        # Trainer with callback
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=compute_intent_metrics,
            callbacks=[PrinterCallback()])

        # Train
        print("\nStarting intent classification training...\n")
        trainer.train()

        # Evaluate
        print("\nFinal Evaluation...")
        results = trainer.evaluate()
        print(f"\n{'='*60}")
        print(f"Final Results:")
        print(f"{'='*60}")
        print(f"Validation loss: {results['eval_loss']:.4f}")
        for key, value in results.items():
            if key != 'eval_loss' and isinstance(value, (int, float)):
                print(f"{key}: {value:.4f}")
        print(f"{'='*60}\n")

        # Save model and tokenizer
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)

        # Save label mapping
        with open(f'{output_dir}/label_map.json', 'w') as f:
            json.dump(self.label_map, f, indent=2)

        print(f"\n Model saved to {output_dir}")

        return results

    def predict(self, text: str) -> Tuple[str, float]:
        """Extract entities from text.

        Args:
            text: Input text

        Returns:
            List of extracted entities with their types and positions
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first")

        # encode the tokens list for
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        # Predicts
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(**encoding)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class].item()

        predicted_intent = self.reverse_label_map[predicted_class]

        return predicted_intent, confidence


class NERDataset(Dataset):
    """Dataset for NER training"""

    def __init__(self, texts, tags, tokenizer, label_map, max_length=128):
        self.texts = texts
        self.tags = tags
        self.tokenizer = tokenizer
        self.label_map = label_map
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        words = self.texts[idx]
        tags = self.tags[idx]

        # Tokenize
        encoding = self.tokenizer(
            words,
            is_split_into_words=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        # Align labels with tokens
        word_ids = encoding.word_ids(batch_index=0)  # Get word_ids for first sequence
        label_ids = []
        previous_word_id = None

        for word_id in word_ids:
            if word_id is None:
                label_ids.append(-100)  # special tokens
            elif word_id != previous_word_id:  # Only label first token of each word
                if tags[word_id] not in self.label_map:
                    print(f"Warning: Unknown tag '{tags[word_id]}' found, using 'O'")
                    label_ids.append(self.label_map['O'])
                else:
                    label_ids.append(self.label_map[tags[word_id]])
            else:
                label_ids.append(-100)  # Subsequent tokens of same word
            previous_word_id = word_id

        encoding['labels'] = torch.tensor(label_ids, dtype=torch.long)

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': encoding['labels'].flatten()
        }


class ClinicalNER:
    """Named Entity Recognition model for clinical trial entities"""

    # Entity types we want to extract
    ENTITY_TYPES = [
        'O',  # Outside any entity
        'B-CANCER_TYPE', 'I-CANCER_TYPE',
        'B-AGE', 'I-AGE',
        'B-SEX', 'I-SEX',
        'B-LOCATION', 'I-LOCATION',
    ]

    def __init__(self, model_name='emilyalsentzer/Bio_ClinicalBERT'):
        """Initialize the NER model.

        Args:
            model_name: Pretrained model to use
        """
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = None
        self.label_map = {label: idx for idx, label in
                          enumerate(self.ENTITY_TYPES)}
        self.reverse_label_map = {idx: label for label, idx in
                                  self.label_map.items()}

    def prepare_data(self, annotated_data: List[Dict]):
        """Prepare NER training data

        Args:
            annotated_data: List of dicts with 'tokens' and 'tags' keys

        Returns:
            Tuple of (texts, tags)
        """
        texts = [item['tokens'] for item in annotated_data]
        tags = [item['tags'] for item in annotated_data]

        return texts, tags

    def train(self, training_data: List[Dict],
              validation_split=0.2,
              epochs=20,
              batch_size=16,
              learning_rate=3e-5,
              output_dir='./ner_model'):
        """Train the NER model

        Args:
            training_data: List of annotated examples
            validation_split: Fraction for validation
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
            output_dir: Directory to save model
        """
        # Prepare data
        texts, tags = self.prepare_data(training_data)

        # Split
        train_texts, val_texts, train_tags, val_tags = train_test_split(
            texts, tags, test_size=validation_split, random_state=42
        )

        print(f"\n{'='*60}")
        print(f"Training Configuration:")
        print(f"{'='*60}")
        print(f"Training samples: {len(train_texts)}")
        print(f"Validation samples: {len(val_texts)}")
        print(f"Entity types: {self.ENTITY_TYPES}")
        print(f"Number of entity types: {len(self.ENTITY_TYPES)}")
        print(f"Epochs: {epochs}")
        print(f"Batch size: {batch_size}")
        print(f"Learning rate: {learning_rate}")
        print(f"{'='*60}\n")

        # Create datasets
        train_dataset = NERDataset(train_texts, train_tags, self.tokenizer,
                                   self.label_map)
        val_dataset = NERDataset(val_texts, val_tags, self.tokenizer,
                                 self.label_map)

        # Initialize model
        self.model = AutoModelForTokenClassification.from_pretrained(
            self.model_name,
            num_labels=len(self.label_map)
        )

        # Data collator
        data_collator = DataCollatorForTokenClassification(self.tokenizer)

        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            eval_strategy="epoch",
            save_strategy="no",
            load_best_model_at_end=False,
            metric_for_best_model="eval_f1",
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir=f'{output_dir}/logs',
            logging_steps=10
        )

        label_list = self.ENTITY_TYPES

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            data_collator=data_collator,
            compute_metrics=lambda p:
            compute_ner_metrics(p, label_list=label_list),
            callbacks=[PrinterCallback()]
        )

        # Train
        print("\nStarting NER training...\n")
        trainer.train()

        # Evaluate
        print("\nFinal Evaluation...")
        results = trainer.evaluate()
        print(f"\n{'='*60}")
        print(f"Final Results:")
        print(f"{'='*60}")
        print(f"Validation Loss: {results['eval_loss']:.4f}")
        for key, value in results.items():
            if key != 'eval_loss' and isinstance(value, (int, float)):
                print(f"{key}: {value:.4f}")
        print(f"{'='*60}\n")

        # Save
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)

        with open(f'{output_dir}/label_map.json', 'w') as f:
            json.dump(self.label_map, f, indent=2)

        print(f"\n Model saved to {output_dir}")

        return results

    def predict(self, text: str) -> List[Dict]:
        """Extract entities from text

        Args:
            text: Input text

        Returns: List of extracted entities with their types and positions
        """

        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        tokens = text.split()

        encoding = self.tokenizer(
            tokens,
            is_split_into_words=True,
            return_tensors='pt',
            padding=True,
            truncation=True
        )

        # Predict
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(**encoding)
            predictions = torch.argmax(outputs.logits, dim=2)

        # Extract entities
        word_ids = encoding.word_ids(batch_index=0)
        entities = []
        current_entity = None
        previous_word_id = None

        for idx, word_id in enumerate(word_ids):
            if word_id is None:
                continue

            # Skip if this is a continuation of a subword token
            if word_id == previous_word_id:
                continue

            if word_id >= len(tokens):  # Safety check
                continue

            pred_id = predictions[0][idx]
            label = self.reverse_label_map[pred_id.item()]

            if label.startswith('B-'):
                # Start new entity
                if current_entity:
                    entities.append(current_entity)
                current_entity = {
                    'text': tokens[word_id],
                    'type': label[2:],  # In order to remove 'B-' prefix
                    'start': word_id,
                    'end': word_id
                }
            elif label.startswith('I-') and current_entity:
                # Continue entity
                if label[2:] == current_entity['type']:
                    current_entity['text'] += ' ' + tokens[word_id]
                    current_entity['end'] = word_id
            else:
                # Outside entity
                if current_entity:
                    entities.append(current_entity)
                    current_entity = None

            previous_word_id = word_id

        if current_entity:
            entities.append(current_entity)

        return entities


# HELPER FUNCTIONS


def load_intent_training_data(filepath: str) -> List[Dict]:
    """Load intent training data from JSON"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data


def load_ner_training_data(filepath: str) -> List[Dict]:
    """Load NER training data from JSON"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

intent_accuracy_metric = evaluate.load("accuracy")
intent_precision_metric = evaluate.load("precision")
intent_recall_metric = evaluate.load("recall")
intent_f1_metric = evaluate.load("f1")
ner_metric = evaluate.load("seqeval")


def compute_intent_metrics(p):
    """Compute metrics for intent classification"""
    preds = np.argmax(p.predictions, axis=1)
    accuracy = intent_accuracy_metric.compute(predictions=preds,
                                            references=p.label_ids)["accuracy"]
    precision = intent_precision_metric.compute(predictions=preds,
                                              references=p.label_ids,
                                              average='weighted')["precision"]
    recall = intent_recall_metric.compute(predictions=preds,
                                        references=p.label_ids,
                                        average='weighted')["recall"]
    f1 = intent_f1_metric.compute(predictions=preds,
                                references=p.label_ids,
                                average='weighted')["f1"]
    return {
        'eval_accuracy': accuracy,
        'eval_f1': f1,
        'eval_precision': precision,
        'eval_recall': recall,
    }


def compute_ner_metrics(p, label_list):
    """Compute metrics for NER"""

    preds = np.argmax(p.predictions, axis=2)
    labels = p.label_ids

    # Convert to label names
    true_predictions = []
    true_labels = []

    for pred, label in zip(preds, labels):
        pred_labels = []
        true_label_list = []
        for p_id, l_id in zip(pred, label):
            if l_id != -100:
                pred_labels.append(label_list[p_id])
                true_label_list.append(label_list[l_id])

        # Only add non-empty sequences
        if pred_labels and true_label_list:
            true_predictions.append(pred_labels)
            true_labels.append(true_label_list)

    # Check if we have any valid sequences
    if not true_predictions or not true_labels:
        return {
            "eval_precision": 0.0,
            "eval_recall": 0.0,
            "eval_f1": 0.0,
            "eval_accuracy": 0.0,
        }

    # Compute metrics using seqeval library
    results = ner_metric.compute(predictions=true_predictions,
                                  references=true_labels)

    # Return overall metrics
    return {
        "eval_precision": results["overall_precision"],
        "eval_recall": results["overall_recall"],
        "eval_f1": results["overall_f1"],
        "eval_accuracy": results["overall_accuracy"],
    }

def main():
    """Main function for training models"""
    print("Clinical Trial NLP Model Training")
    print("=" * 50)


    # Train Intent Classifier
    intent_data = load_intent_training_data('intent_training_data.json')
    intent_classifier = IntentClassifier()
    intent_classifier.train(intent_data)

    # Train NER Model
    ner_data = load_ner_training_data('ner_training_data.json')
    ner_model = ClinicalNER()
    ner_model.train(ner_data)

    print("\nTraining complete.")


if __name__ == "__main__":
    main()
