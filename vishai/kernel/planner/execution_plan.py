from dataclasses import dataclass, field
from typing import List, Optional
from vishai.kernel.planner.step import ExecutionStep

@dataclass
class ExecutionPlan:
    """
    Represents an ordered sequence of ExecutionSteps to fulfill a user Intent.
    """
    id: str
    intent_action: str
    steps: List[ExecutionStep] = field(default_factory=list)
    status: str = "pending"  # pending, running, success, failure
    
    # Learning Engine Hooks
    execution_time: float = 0.0
    failed_step_id: Optional[str] = None
    failure_reason: Optional[str] = None
    
    def get_skipped_steps(self) -> List[ExecutionStep]:
        return [s for s in self.steps if s.status == "skipped"]
