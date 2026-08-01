from typing import Optional
from vishai.planner.engine import IntentEngine
from vishai.kernel.ore import ObjectResolutionEngine
from vishai.kernel.planner.planner import PlannerEngine
from vishai.kernel.planner.execution_plan import ExecutionPlan
from vishai.kernel.executor.executor import ExecutionEngine
from vishai.utils.logger import SystemLogger

logger = SystemLogger.get_logger()

class Brain:
    """
    The central coordinator for the VishAI Execution Pipeline.
    Strictly routes user input: Brain -> Intent -> ORE -> Planner -> Executor -> Capability.
    """
    def __init__(self, intent_engine: IntentEngine, ore: ObjectResolutionEngine, 
                 planner: PlannerEngine, executor: ExecutionEngine):
        self.intent_engine = intent_engine
        self.ore = ore
        self.planner = planner
        self.executor = executor
        logger.info("VishAI Brain initialized.")

    def plan_command(self, text: str) -> Optional[ExecutionPlan]:
        """Generates an ExecutionPlan without executing it."""
        logger.info(f"=== Brain Pipeline Initiated (Planning Only): '{text}' ===")
        intent = self.intent_engine.process(text)
        if not intent.is_valid():
            logger.warning("Brain Pipeline aborted: Intent could not be understood.")
            return None
            
        resolution = self.ore.resolve(intent)
        if not resolution.resource:
            logger.warning("Brain Pipeline aborted: ORE could not resolve the target object.")
            return None
            
        plan = self.planner.create_plan(intent, resolution)
        return plan

    def process_command(self, text: str) -> None:
        """Executes the full capability pipeline for a given user command."""
        logger.info(f"=== Brain Pipeline Initiated: '{text}' ===")
        
        # 1. Intent Understanding
        intent = self.intent_engine.process(text)
        if not intent.is_valid():
            logger.warning("Brain Pipeline aborted: Intent could not be understood.")
            return
            
        # 2. Object Resolution
        resolution = self.ore.resolve(intent)
        if not resolution.resource:
            logger.warning("Brain Pipeline aborted: ORE could not resolve the target object.")
            return
            
        # 3. Planning
        plan = self.planner.create_plan(intent, resolution)
        if not plan:
            logger.warning("Brain Pipeline aborted: Planner could not generate an execution plan.")
            return
            
        # 4. Execution
        success = self.executor.execute_plan(plan)
        if success:
            logger.info("=== Brain Pipeline completed successfully. ===")
        else:
            logger.error("=== Brain Pipeline failed during execution. ===")
