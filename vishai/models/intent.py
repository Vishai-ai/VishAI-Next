from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class Intent:
    """
    Core cognitive structure representing a user's understood command.
    Shared across the entire VishAI Operating System.
    """
    action: Optional[str] = None
    target: Optional[str] = None
    object: Optional[str] = None
    value: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Text Analysis
    original_text: str = ""
    normalized_text: str = ""
    
    # Token Tracking (Used by Learning Engine)
    matched_tokens: List[str] = field(default_factory=list)
    unknown_tokens: List[str] = field(default_factory=list)
    
    # Confidence Score (0.0 to 1.0)
    confidence: float = 0.0

    def is_valid(self) -> bool:
        """Returns True if the intent has at least an action."""
        return self.action is not None and self.confidence > 0.0
