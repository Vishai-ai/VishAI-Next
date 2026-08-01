import sys
import threading
import signal
from typing import Optional

from vishai.utils.logger import SystemLogger
from vishai.kernel.config import ConfigLoader, SystemConfig
from vishai.planner.engine import IntentEngine
from vishai.capabilities.kde import KnowledgeDiscoveryEngine
from vishai.capabilities.kde.providers import DEFAULT_PROVIDERS
from vishai.kernel.ore import ObjectResolutionEngine
from vishai.kernel.planner import PlannerEngine
from vishai.kernel.executor import ExecutionEngine
from vishai.brain import Brain

logger = SystemLogger.get_logger()

class Kernel:
    """
    The Core Engine of VishAI Operating System.
    Responsible for bootstrapping, lifecycle management, and graceful shutdown.
    """
    def __init__(self):
        self.config_loader = ConfigLoader()
        self.config: Optional[SystemConfig] = None
        self._shutdown_event = threading.Event()
        self.intent_engine: Optional[IntentEngine] = None
        self.kde: Optional[KnowledgeDiscoveryEngine] = None
        self.ore: Optional[ObjectResolutionEngine] = None
        self.planner: Optional[PlannerEngine] = None
        self.executor: Optional[ExecutionEngine] = None
        self.brain: Optional[Brain] = None

    def initialize(self) -> None:
        """Bootstraps the kernel and loads required sub-systems."""
        logger.info("Initializing VishAI Kernel...")
        try:
            self.config = self.config_loader.load()
            self._register_signal_handlers()
            
            # Initialize sub-systems
            self.intent_engine = IntentEngine(data_dir=self.config.data_dir)
            
            # Initialize Knowledge Discovery Engine
            self.kde = KnowledgeDiscoveryEngine(data_dir=self.config.data_dir)
            for provider_class in DEFAULT_PROVIDERS:
                self.kde.register_provider(provider_class)
                
            # Trigger initial discovery
            self.kde.discover_all()
            
            # Initialize Object Resolution Engine
            self.ore = ObjectResolutionEngine(kde=self.kde)
            
            # Initialize Execution Pipeline
            self.planner = PlannerEngine()
            self.executor = ExecutionEngine()
            self.brain = Brain(
                intent_engine=self.intent_engine,
                ore=self.ore,
                planner=self.planner,
                executor=self.executor
            )
            
            logger.info("VishAI Kernel initialized successfully.")
        except Exception as e:
            logger.error(f"Fatal error during initialization: {e}")
            sys.exit(1)

    def _register_signal_handlers(self) -> None:
        """Ensures graceful shutdown on OS signals."""
        signal.signal(signal.SIGINT, self._handle_shutdown_signal)
        signal.signal(signal.SIGTERM, self._handle_shutdown_signal)

    def _handle_shutdown_signal(self, signum: int, _frame) -> None:
        logger.info(f"Received termination signal ({signum}). Initiating shutdown sequence...")
        self.shutdown()

    def start(self) -> None:
        """Starts the main event loop of the Operating System."""
        if not self.config:
            raise RuntimeError("Kernel must be initialized before starting.")
        
        logger.info(f"VishAI OS started in {self.config.environment} mode.")
        
        try:
            # Main thread blocks until shutdown is requested
            self._shutdown_event.wait()
        except KeyboardInterrupt:
            self.shutdown()
        except Exception as e:
            logger.error(f"Unhandled exception in Kernel loop: {e}", exc_info=True)
            self.shutdown()

    def shutdown(self) -> None:
        """Gracefully shuts down the Kernel and all loaded capabilities."""
        if self._shutdown_event.is_set():
            return
            
        logger.info("Shutting down VishAI Kernel...")
        self._shutdown_event.set()
        
        # Safe shutdown logic for subsystems will go here
        
        logger.info("VishAI Shutdown complete. Goodbye.")
        sys.exit(0)
