import os
import json
from dataclasses import dataclass
from typing import Dict, Any

from vishai.utils.logger import SystemLogger

logger = SystemLogger.get_logger()

@dataclass
class SystemConfig:
    environment: str
    debug: bool
    data_dir: str

class ConfigLoader:
    """
    Loads and validates system configurations from environment variables and files.
    """
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self._config_cache: Dict[str, Any] = {}

    def load(self) -> SystemConfig:
        logger.info(f"Loading configuration from {self.config_path} (fallback to env)")
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config_cache = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config file: {e}")
                raise

        # Map to SystemConfig with environment variable fallbacks
        env = os.getenv("VISHAI_ENV", self._config_cache.get("environment", "production"))
        debug_str = os.getenv("VISHAI_DEBUG", str(self._config_cache.get("debug", "False")))
        debug = debug_str.lower() in ("true", "1", "yes")
        data_dir = os.getenv("VISHAI_DATA_DIR", self._config_cache.get("data_dir", "./data"))

        os.makedirs(data_dir, exist_ok=True)

        config = SystemConfig(
            environment=env,
            debug=debug,
            data_dir=data_dir
        )
        
        logger.info(f"Configuration loaded: {config}")
        return config
