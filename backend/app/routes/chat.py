from fastapi import APIRouter, Request
from app.services import nlp, clinicaltrials_api
from app.core.state import active_states, ConversationState

router = APIRouter()

@router.post("/message")
async def handle_message(request: Request):
    """Main chat entrypoint."""
    data = await request.json()
    user_input = data.get("message", "")
    user_id = data.get("user_id", "default")

    # Retrieve or initialize user state
    state = active_states.get(user_id, ConversationState())

    # 1 NLP entity extraction
    entities = nlp.extract_entities(user_input)
    for key, value in entities.items():
        if hasattr(state, key):
            setattr(state, key, value)

    # 2 Handle non-find_trials intents
    if entities.get("intent") == "greeting":
        response = {"response": "Hello! I can help you find clinical trials. What type of cancer are you researching?"}
        active_states[user_id] = state
        return response
    elif entities.get("intent") == "goodbye":
        response = {"response": "Goodbye! Feel free to return anytime you need help finding clinical trials."}
        active_states[user_id] = state
        return response
    
    # 3 If complete, query trials
    if state.is_complete() and entities.get("intent") == "find_trials":
        trials = await clinicaltrials_api.search_clinical_trials(state.cancer_type, state.location)
        response = {
            "response": f"Here are some {state.cancer_type} clinical trials in {state.location}:",
            "trials": trials
        }
    else:
        # 4 Continue intake flow
        missing_fields = []
        if not state.cancer_type:
            missing_fields.append("cancer type")
        elif not state.location:
            missing_fields.append("location")

        next_question = f"Please tell me your {missing_fields[0]}." if missing_fields else "Could you clarify your request?"
        response = {"response": next_question}

    # Persist state (in-memory)
    active_states[user_id] = state

    return response