from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

@dataclass
class ExecutionStep:
    """
    Represents a single atomic operation to be executed by a Capability.
    """
    id: str
    action: str
    target: str
    capability: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Advanced Planner Fields
    depends_on: List[str] = field(default_factory=list)
    retry_count: int = 0
    timeout: float = 30.0
    optional: bool = False
    
    # Execution state maintained by Executor
    status: str = "pending"  # pending, running, success, failure, skipped
    result: Optional[Dict[str, Any]] = None
