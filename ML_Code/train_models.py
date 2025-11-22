"""
Training script for Clinical Trial Chatbot NLP Models

This script trains both the intent classification and NER models

Usage:
    python train_models.py
"""

import json
import sys
from clinical_trial_nlp_model import (
    IntentClassifier,
    ClinicalNER,
    load_intent_training_data,
    load_ner_training_data
)


def train_intent_model():
    """Train the intent classification model."""

    print("\n" + "=" * 70)
    print("Training Intent Classification Model")
    print("=" * 70)

    # Load training data
    print("\n Loading intent training data...")
    try:
        training_data = load_intent_training_data("intent_training_data.json")
        print(f" Loaded {len(training_data)} training examples.")

        # Show intent distribution
        intent_counts = {}
        for item in training_data:
            intent = item['intent']
            intent_counts[intent] = intent_counts.get(intent, 0) + 1

        print("\n Intent distribution:")
        for intent, count in sorted(intent_counts.items()):
            print(f"  {intent}: {count} examples")

    except FileNotFoundError:
        print(" Error: intent_training_data.json file not found.")
        return None
    
    # Initialize model
    print("\n Initializing BioClinicalBERT model...")
    num_intents = len(set(item['intent'] for item in training_data))
    intent_model = IntentClassifier(
        model_name="emilyalsentzer/Bio_ClinicalBERT",
        num_labels=3)
    
    # Train model
    print("\n Starting training...")
    print(" This may take a while depending on your hardware.")

    results = intent_model.train(
        training_data=training_data,
        validation_split=0.2,
        epochs=20,
        batch_size=16,
        learning_rate=2e-5,
        output_dir="./models/intent_model"
    )

    print("\n Training complete.")
    print(" Model saved to ./models/intent_model")

    # Test predictions
    print("\n Testing model predictions on sample inputs:")
    test_texts = [
        "I want to find clinical trials for prostate cancer",
        "am I eligible for this study",
        "Where is the trial located",
        "what is a phase 2 clinical trial"
    ]
    
    for text in test_texts:
        intent, confidence = intent_model.predict(text)
        print(f" Text: {text}")
        print(f" Predicted Intent: {intent} (Confidence: {confidence:.2%})\n")

    return intent_model

def train_ner_model():
    """Train the Named Entity Recognition (NER) model."""

    print("\n" + "=" * 70)
    print("Training Clinical NER Model")
    print("=" * 70)

    # Load training data
    print("\n Loading NER training data...")
    try:
        training_data = load_ner_training_data("ner_training_data.json")
        print(f" Loaded {len(training_data)} training examples.")

        # show entity distribution
        entity_counts = {}
        for item in training_data:
            for tag in item['tags']:
                if tag != 'O':  # 'O' means Outside any entity
                    entity_type = tag.split('-')[1] if '-' in tag else tag
                    entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
                
        print("\n Entity distribution:")
        for entity, count in sorted(entity_counts.items()):
            print(f"  {entity}: {count} instances")

    except FileNotFoundError:
        print(" Error: ner_training_data.json file not found.")
        return None
    
    # Initialize model
    print("\n Initializing BioClinicalBERT model for NER...")
    ner_model = ClinicalNER(model_name="emilyalsentzer/Bio_ClinicalBERT")

    # Train model
    print("\n Starting training...")
    print(" This may take a while depending on your hardware.")

    results = ner_model.train(
        training_data=training_data,
        validation_split=0.2,
        epochs=20,
        batch_size=16,
        learning_rate=3e-5,
        output_dir="./models/ner_model"
    )

    print("\n Training complete.")
    print(" Model saved to ./models/ner_model")

    # Test predictions
    print("\n Testing entity extraction:")
    test_texts = [
        "I'm a 65 year old male with prostate cancer",
        "Looking for trials in Dallas Texas for breast cancer",
        "Female patient age 52 testicular cancer"
    ]
    
    for text in test_texts:
        entities = ner_model.predict(text)
        print(f" Text: {text}")
        if entities:
            print (" Extracted Entities:")
            for entity in entities:
                print(f"  - {entity['type']}: '{entity['text']}'")
        else:
            print(" No entities found.")
        print()

    return ner_model


def main():
    """Main training pipeline."""
    print("\n" + "=" * 70)
    print("Clinical Trial Chatbot NLP Model Training")
    print("=" * 70)
    print("\nTraining two models:")
    print(" 1. Intent Classification Model")
    print(" 2. Named Entity Recognition (NER) Model")
    print("\n Estimated total training time: ~30-60 minutes.")
    print("=" * 70)

    # Train both models
    try:
        # Train intent model
        intent_model = train_intent_model()
        
        if intent_model is None:
            print(" Intent model training failed. Exiting.")
            return
        
        # Train NER model
        ner_model = train_ner_model()
        
        if ner_model is None:
            print(" NER model training failed. Exiting.")
            return
        
        # If successful
        print("\n" + "=" * 70)
        print("Both models trained successfully!")
        print("=" * 70)
        print("\n Models saved to:")
        print("  - Intent Model: ./models/intent_model")
        print("  - NER Model: ./models/ner_model")

    except Exception as e:
        print(f"\n An error occurred during training: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\nTraining pipeline complete.")


if __name__ == "__main__":
    main()