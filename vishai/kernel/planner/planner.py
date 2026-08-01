import uuid
from typing import Optional

from vishai.models.intent import Intent
from vishai.models.resolution import ResolutionResult
from vishai.kernel.planner.execution_plan import ExecutionPlan
from vishai.kernel.planner.step import ExecutionStep
from vishai.utils.logger import SystemLogger

logger = SystemLogger.get_logger()

class PlannerEngine:
    """
    Transforms an Intent and a resolved SystemResource into an ExecutionPlan.
    Designed to support multiple steps, conditions, loops, and retries in the future.
    """
    def __init__(self):
        logger.info("Planner Engine initialized.")

    def create_plan(self, intent: Intent, resolution: ResolutionResult) -> Optional[ExecutionPlan]:
        """Generates an ExecutionPlan based on intent and resolved resource."""
        if not intent.is_valid() or not resolution.resource:
            logger.warning("Planner cannot create plan: Invalid intent or missing resource.")
            return None
            
        plan_id = str(uuid.uuid4())
        plan = ExecutionPlan(id=plan_id, intent_action=intent.action)
        resource = resolution.resource
        
        # Step 1: Launch
        step1_id = f"{plan_id}_step_1"
        step1 = ExecutionStep(
            id=step1_id,
            action="launch",
            target=resource.path,
            capability="os_control",
            parameters={"resource_id": resource.id, "display_name": resource.display_name}
        )
        plan.steps.append(step1)
        
        # Step 2: Wait until application is ready
        step2_id = f"{plan_id}_step_2"
        step2 = ExecutionStep(
            id=step2_id,
            action="wait",
            target="system",
            capability="os_control",
            parameters={"duration": 1.0},
            depends_on=[step1_id]
        )
        plan.steps.append(step2)

        # Step 3: Focus window
        step3_id = f"{plan_id}_step_3"
        step3 = ExecutionStep(
            id=step3_id,
            action="focus",
            target=resource.display_name,
            capability="os_control",
            parameters={"window_title": resource.display_name},
            depends_on=[step2_id]
        )
        plan.steps.append(step3)

        # Determine if there are secondary actions from unknown_tokens
        # e.g., "search python tutorial" or "write hello vishai"
        unknowns = intent.unknown_tokens
        last_step_id = step3_id
        step_idx = 4
        
        if "search" in unknowns:
            idx = unknowns.index("search")
            query = " ".join(unknowns[idx+1:])
            step_id = f"{plan_id}_step_{step_idx}"
            step4 = ExecutionStep(
                id=step_id,
                action="search",
                target="search_bar",
                capability="os_control",
                parameters={"query": query},
                depends_on=[last_step_id]
            )
            plan.steps.append(step4)
            last_step_id = step_id
            step_idx += 1
            
        elif "write" in unknowns or "type" in unknowns:
            keyword = "write" if "write" in unknowns else "type"
            idx = unknowns.index(keyword)
            query = " ".join(unknowns[idx+1:])
            step_id = f"{plan_id}_step_{step_idx}"
            step4 = ExecutionStep(
                id=step_id,
                action="type",
                target="text_input",
                capability="os_control",
                parameters={"text": query},
                depends_on=[last_step_id]
            )
            plan.steps.append(step4)
            
        logger.info(f"Planner generated ExecutionPlan '{plan_id}' with {len(plan.steps)} step(s).")
        return plan
