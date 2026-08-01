import sys
from vishai.kernel.system import Kernel
from vishai.utils.logger import SystemLogger

logger = SystemLogger.get_logger()

def main():
    logger.info("Booting VishAI Next...")
    kernel = Kernel()
    
    try:
        kernel.initialize()
        
        # Developer testing flags
        if "--verify" in sys.argv:
            logger.info("Verification mode active. System boot successful. Shutting down...")
            kernel.shutdown()
        elif "--test-ore" in sys.argv:
            try:
                query_idx = sys.argv.index("--test-ore") + 1
                query = sys.argv[query_idx]
            except IndexError:
                logger.error("Missing query for --test-ore")
                sys.exit(1)
                
            logger.info(f"Testing ORE with query: '{query}'")
            intent = kernel.intent_engine.process(query)
            result = kernel.ore.resolve(intent)
            
            if result.resource:
                logger.info(f"Test Success: Resolved to {result.resource.display_name} (Method: {result.matching_method}, Confidence: {result.confidence})")
            else:
                logger.info("Test Result: No resource resolved.")
                
            kernel.shutdown()
        elif "--plan" in sys.argv:
            try:
                query_idx = sys.argv.index("--plan") + 1
                query = sys.argv[query_idx]
            except IndexError:
                logger.error("Missing query for --plan")
                sys.exit(1)
                
            logger.info(f"Planning full pipeline for query: '{query}'")
            plan = kernel.brain.plan_command(query)
            if plan:
                print(f"\n=== Generated Execution Plan ===")
                print(f"Plan ID: {plan.id}")
                print(f"Intent Action: {plan.intent_action}")
                for i, step in enumerate(plan.steps, 1):
                    print(f"  Step {i}:")
                    print(f"    ID: {step.id}")
                    print(f"    Action: {step.action}")
                    print(f"    Target: {step.target}")
                    print(f"    Capability: {step.capability}")
                    print(f"    Depends On: {step.depends_on}")
                    print(f"    Parameters: {step.parameters}")
                print("================================\n")
            else:
                logger.error("Failed to generate plan.")
            kernel.shutdown()
        elif "--test-action" in sys.argv:
            try:
                idx = sys.argv.index("--test-action")
                action = sys.argv[idx + 1]
                params = {}
                for arg in sys.argv[idx + 2:]:
                    if "=" in arg:
                        k, v = arg.split("=", 1)
                        if v.isdigit(): v = int(v)
                        elif v.replace(".", "", 1).isdigit(): v = float(v)
                        params[k] = v
                    else:
                        logger.warning(f"Ignoring param without '=': {arg}")
                        
                target_val = params.get("app", params.get("target", "test"))
                from vishai.kernel.planner.step import ExecutionStep
                step = ExecutionStep(
                    id="test_step",
                    action=action,
                    target=target_val,
                    capability="os_control",
                    parameters=params
                )
                logger.info(f"Testing OS action '{action}' with parameters {params}")
                result = kernel.executor.capabilities["os_control"].execute(step)
                logger.info(f"Result: {result}")
                
            except IndexError:
                logger.error("Missing arguments for --test-action")
                sys.exit(1)
            except Exception as e:
                logger.error(f"Error testing action: {e}", exc_info=True)
            kernel.shutdown()
        elif "--run" in sys.argv:
            try:
                query_idx = sys.argv.index("--run") + 1
                query = sys.argv[query_idx]
            except IndexError:
                logger.error("Missing query for --run")
                sys.exit(1)
                
            logger.info(f"Running full pipeline for query: '{query}'")
            kernel.brain.process_command(query)
            kernel.shutdown()
        else:
            kernel.start()
    except Exception as e:
        logger.error(f"Critical failure: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
