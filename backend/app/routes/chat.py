from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List, Optional
import logging
from app.services import nlp, clinicaltrials_api
from app.core.state import active_states, ConversationState

logger = logging.getLogger(__name__)
router = APIRouter()


class IntakeForm(BaseModel):
    user_id: str
    cancer_type: str
    stage: str
    age: int
    sex: str
    location: str
    comorbidities: Optional[List[str]] = []
    prior_treatments: Optional[List[str]] = []

@router.post("/intake")
async def submit_intake(intake: IntakeForm):
    """Receive intake form data from frontend."""

    # Get or create user state
    state = active_states.get(intake.user_id, ConversationState())

    # Store all intake data in state
    state.cancer_type = intake.cancer_type
    state.stage = intake.stage
    state.age = intake.age
    state.sex = intake.sex
    state.location = intake.location
    state.comorbidities = intake.comorbidities or []
    state.prior_treatments = intake.prior_treatments or []
    state.intake_complete = True

    # Persist state
    active_states[intake.user_id] = state

    return {
        "response": "Thank you for sharing that information with me. How can I"
        " help you find clinical trials today?",
        "intake_complete": True
    }


@router.post("/message")
async def handle_message(request: Request):
    """Main chat entrypoint."""
    data = await request.json()
    user_input = data.get("message", "")
    user_id = data.get("user_id", "default")

    # Retrieve or initialize user state
    state = active_states.get(user_id, ConversationState())

    # Check if intake is complete before processing
    if not state.intake_complete:
        return {
            "response": "Please complete the intake form before proceeding.",
            "requires_intake": True
        }
    # 1. NLP entity extraction with intake context
    intake_context = {
        "cancer_type": state.cancer_type,
        "location": state.location,
        "stage": state.stage,
        "age": state.age,
        "sex": state.sex,
        "comorbidities": state.comorbidities,
        "prior_treatments": state.prior_treatments
    }
    entities = nlp.extract_entities(user_input, intake_context=intake_context)
   

    # update state with new entitites mentioned in convo
    for key, value in entities.items():
        if hasattr(state, key):
            setattr(state, key, value)

    # 2 Handle non-find_trials intents
    if entities.get("intent") == "greeting":
        response = {"response": "Hello! How can I help you find clinical trials today?"}
    elif entities.get("intent") == "goodbye":
        response = {"response": "Goodbye! Feel free to return anytime you need help finding clinical trials."}
    elif entities.get("intent") == "find_trials":

        # 3. Query trials with full context
        trials = await clinicaltrials_api.search_clinical_trials(
            cancer_type=state.cancer_type,
            location=state.location,
            stage=state.stage,
            age=state.age
        )
        response = {
            "response": f"Here are some {state.cancer_type} clinical trials in {state.location}:",
            "trials": trials
        }

    else:
        response = {"response": "I'm here to help you find clinical trials. What would you like to know?"}

    # Persist state (in-memory)
    active_states[user_id] = state

    return response

@router.post("/end-session")
async def end_session(request: Request):
    """Clear all session data when user exits."""
    data = await request.json()
    user_id = data.get("user_id")
    
    if user_id in active_states:
        del active_states[user_id]
        logger.info("Session cleared")
    
    return {"status": "session_cleared"}