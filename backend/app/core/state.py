from typing import Optional, List

class ConversationState:
    """Conversation context for each session/user."""
    def __init__(self):
        self.cancer_type: Optional[str] = None
        self.stage: Optional[str] = None
        self.age: Optional[int] = None
        self.sex: Optional[str] = None
        self.location: Optional[str] = None
        self.comorbidities: List[str] = []
        self.prior_treatments: List[str] = []

    def is_complete(self) -> bool:
        """Check if enough info is collected to query trials."""
        required_fields = [self.cancer_type, self.stage, self.location]
        return all(required_fields)

    def to_dict(self):
        return self.__dict__

# In production, you’d persist state per user session (e.g., Redis, in-memory store)
active_states = {}