"""
NLP Service - BioClinicalBERT Model Integration
"""
import torch
from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                          AutoModelForTokenClassification)
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# MODEL CONFIGURATION

# Paths to trained BioClinicalBERT models
INTENT_MODEL_PATH = "../models/intent_model"
NER_MODEL_PATH = "../models/ner_model"

# Model loaded once at startup
intent_model = None
intent_tokenizer = None
ner_model = None
ner_tokenizer = None
device = None

# Intent labels
INTENT_LABELS = {
    0: "find_trials",
    1: "goodbye",
    2: "greeting"
}

# NER labels (B-I-O format)
NER_LABELS = {
    0: "O",
    1: "B-CANCER_TYPE",
    2: "I-CANCER_TYPE",
    3: "B-AGE",
    4: "I-AGE",
    5: "B-SEX",
    6: "I-SEX",
    7: "B-LOCATION",
    8: "I-LOCATION"
}

# Reverse mapping
LABEL_TO_ID = {v: k for k, v in NER_LABELS.items()}


def load_models():
    """
    Load both trained models at startup.
    Called once when the FastAPI app starts.
    """
    global intent_model, intent_tokenizer, ner_model, ner_tokenizer, device

    try:
        # Determine device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Loading models on device: {device}")

        # Load Intent Classification Model
        logger.info(f"Loading intent model from {INTENT_MODEL_PATH}")
        intent_tokenizer = AutoTokenizer.from_pretrained(INTENT_MODEL_PATH)
        intent_model = AutoModelForSequenceClassification.from_pretrained(
            INTENT_MODEL_PATH)
        intent_model.to(device)
        intent_model.eval()
        logger.info("Intent model loaded successfully")

        # Load NER Model
        logger.info(f"Loading NER model from {NER_MODEL_PATH}")
        ner_tokenizer = AutoTokenizer.from_pretrained(NER_MODEL_PATH)
        ner_model = AutoModelForTokenClassification.from_pretrained(
            NER_MODEL_PATH)
        ner_model.to(device)
        ner_model.eval()
        logger.info("NER model loaded successfully")

    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        raise


def predict_intent(text: str) -> str:
    """
    Predict intent using the trained intent classification model.

    Args:
        text: User input text

    Returns:
        Intent label (e.g., "find_trials", "goodbye", "greeting")
    """
    if intent_model is None:
        logger.error("Intent model not loaded")
        return "find_trials"  # Default fallback

    try:
        # Tokenize input
        inputs = intent_tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        ).to(device)

        # Get prediction
        with torch.no_grad():
            outputs = intent_model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=-1)
            intent_id = predictions.item()

        # Map to intent label
        intent = INTENT_LABELS.get(intent_id, "find_trials")
        logger.info(f"Predicted intent: {intent}")
        return intent

    except Exception as e:
        logger.error(f"Error predicting intent: {str(e)}")
        return "find_trials"  # Default fallback


def predict_entities(text: str) -> Dict[str, Optional[str]]:
    """
    Extract entities using the trained NER model.

    Args:
        text: User input text

    Returns:
        Dictionary of extracted entities
    """
    if ner_model is None:
        logger.error("NER model not loaded")
        return {}

    try:
        # Split into words
        words = text.split()
        
        # Tokenize with is_split_into_words=True
        inputs = ner_tokenizer(
            words,
            is_split_into_words=True,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )
        
        inputs_on_device = {k: v.to(device) for k, v in inputs.items()}

        # Get predictions
        with torch.no_grad():
            outputs = ner_model(**inputs_on_device)
            predictions = torch.argmax(outputs.logits, dim=-1)[0]

        # Use word_ids to map tokens back to words
        word_ids = inputs.word_ids(batch_index=0)
        
        # Get one prediction per word (use first subword token's prediction)
        word_predictions = []
        previous_word_id = None
        
        for idx, word_id in enumerate(word_ids):
            if word_id is None:  # Special tokens
                continue
            if word_id != previous_word_id:  # First token of a new word
                pred_id = predictions[idx].item()
                label = NER_LABELS.get(pred_id, "O")
                word_predictions.append((words[word_id], label))
                previous_word_id = word_id

        # Extract entities from word-level predictions
        entities = {
            "cancer_type": None,
            "age": None,
            "sex": None,
            "location": None,
        }

        current_entity = None
        current_words = []

        for word, label in word_predictions:
            # Handle B- (beginning) tags
            if label.startswith("B-"):
                # Save previous entity if exists
                if current_entity and current_words:
                    entity_text = " ".join(current_words)
                    entity_type = current_entity.lower()
                    if entity_type in entities:
                        entities[entity_type] = entity_text

                # Start new entity
                current_entity = label[2:]  # Remove "B-"
                current_words = [word]

            # Handle I- (inside) tags
            elif label.startswith("I-") and current_entity:
                entity_type = label[2:]
                if entity_type == current_entity:
                    current_words.append(word)

            # Handle O (outside) tags
            else:
                # Save previous entity if exists
                if current_entity and current_words:
                    entity_text = " ".join(current_words)
                    entity_type = current_entity.lower()
                    if entity_type in entities:
                        entities[entity_type] = entity_text
                current_entity = None
                current_words = []

        # Last entity
        if current_entity and current_words:
            entity_text = " ".join(current_words)
            entity_type = current_entity.lower()
            if entity_type in entities:
                entities[entity_type] = entity_text

        logger.info(f"Extracted entities: {entities}")
        return entities

    except Exception as e:
        logger.error(f"Error extracting entities: {str(e)}")
        return {}

def extract_entities(user_input: str) -> Dict[str, Optional[str]]:
    """
    Main function
    Extracts intent and entities from user input.

    Args:
        user_input: The user's message

    Returns:
        Dictionary with format:
        {
            'intent': 'find_trials',
            'cancer_type': 'Prostate',
            'stage': 'Stage 2',  # or None
            'location': 'Texas',
            'sex': 'Male',
            'age': '65'
        }
    """
    print(f"NLP: Processing user input: {user_input}")
    logger.info(f"Processing user input: {user_input}")

    # Get intent
    intent = predict_intent(user_input)
    print(f"NLP: Predicted intent: {intent}")


    # Get entities
    entities = predict_entities(user_input)
    print(f"NLP: Extracted entities: {entities}")


    # Build response
    result = {
        'intent': intent,
        'cancer_type': entities.get('cancer_type'),
        'location': entities.get('location'),
        'age': entities.get('age'),
        'sex': entities.get('sex')
    }

    # Clean up None values from result (keeps response cleaner)
    result = {k: v for k, v in result.items() if v is not None}

    print(f"NLP: Final result: {result}")
    logger.info(f"Final result: {result}")
    return result
