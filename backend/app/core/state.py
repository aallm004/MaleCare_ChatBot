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
        self.intake_complete: bool = False # tracks form submission

    def is_complete(self) -> bool:
        """Check if enough info is collected to query trials."""
        return self._intake_complete and self.cancer_type and self.location

    def to_dict(self):
        return self.__dict__

active_states = {}