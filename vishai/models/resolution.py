from dataclasses import dataclass
from typing import Optional
from vishai.models.resource import SystemResource

@dataclass
class ResolutionResult:
    """
    Result of a resolution query from the Object Resolution Engine (ORE).
    """
    resource: Optional[SystemResource]
    confidence: float
    reason: str
    matching_method: str
