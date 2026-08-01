import time
from typing import Dict
from vishai.kernel.planner.execution_plan import ExecutionPlan
from vishai.kernel.planner.step import ExecutionStep
from vishai.capabilities.os_control import OSControlCapability
from vishai.utils.logger import SystemLogger

logger = SystemLogger.get_logger()

class ExecutionEngine:
    """
    Executes an ExecutionPlan strictly by delegating steps to Capabilities.
    Never understands English, never parses intents.
    """
    def __init__(self):
        # In a fully mature state, capabilities will be injected dynamically
        self.capabilities = {
            "os_control": OSControlCapability()
        }
        logger.info("Execution Engine initialized.")

    def execute_plan(self, plan: ExecutionPlan) -> bool:
        """Runs the ordered steps inside the ExecutionPlan."""
        logger.info(f"Executor starting Plan ID '{plan.id}' ({len(plan.steps)} steps)")
        plan.status = "running"
        plan_start_time = time.time()
        
        step_results = {}  # step_id -> bool success
        
        for step in plan.steps:
            if plan.status == "failed":
                step.status = "skipped"
                continue
                
            # Check dependencies
            can_run = True
            for dep in step.depends_on:
                if not step_results.get(dep, False):
                    can_run = False
                    break
                    
            if not can_run:
                step.status = "skipped"
                if not step.optional:
                    plan.status = "failed"
                    plan.failed_step_id = step.id
                    plan.failure_reason = f"Dependency '{dep}' failed"
                continue
                
            success = self._execute_step(step)
            step_results[step.id] = success
            
            if not success and not step.optional:
                plan.status = "failed"
                plan.failed_step_id = step.id
                plan.failure_reason = step.result.get("reason", "Unknown failure") if step.result else "Unknown failure"
                logger.error(f"Executor aborted Plan '{plan.id}' due to failure at step '{step.id}'.")
                
        plan.execution_time = time.time() - plan_start_time
        
        if plan.status != "failed":
            plan.status = "success"
            logger.info(f"Executor successfully completed Plan '{plan.id}' in {plan.execution_time:.2f}s.")
            return True
        else:
            skipped_count = len(plan.get_skipped_steps())
            logger.warning(f"Plan '{plan.id}' failed at '{plan.failed_step_id}'. Skipped {skipped_count} remaining steps.")
            return False
            
    def _execute_step(self, step: ExecutionStep) -> bool:
        """Delegates a single step to the requested Capability."""
        logger.debug(f"Executor dispatching Step '{step.id}' -> Capability: [{step.capability}]")
        step.status = "running"
        
        capability = self.capabilities.get(step.capability)
        if not capability:
            step.status = "failure"
            step.result = {"success": False, "reason": f"Capability '{step.capability}' not found in registry."}
            logger.error(step.result["reason"])
            return False
            
        # The Capability executes the operation
        # Handling retry logic
        attempts = 0
        max_attempts = step.retry_count + 1
        
        while attempts < max_attempts:
            result = capability.execute(step)
            step.result = result
            
            if result.get("success"):
                step.status = "success"
                logger.info(f"Executor: Step '{step.id}' succeeded. (Time: {result.get('execution_time'):.4f}s)")
                return True
                
            attempts += 1
            if attempts < max_attempts:
                logger.info(f"Executor: Retrying Step '{step.id}' (Attempt {attempts}/{max_attempts})")
                
        step.status = "failure"
        logger.error(f"Executor: Step '{step.id}' failed after {max_attempts} attempts. Reason: {step.result.get('reason')}")
        return False
