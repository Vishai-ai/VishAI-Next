import logging
import sys
from typing import Optional

class SystemLogger:
    """
    Production-grade logger for VishAI.
    Ensures structured, consistent logging across all modules.
    """
    _instance: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls, name: str = "VishAI") -> logging.Logger:
        if cls._instance is not None:
            return cls._instance

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | [%(filename)s:%(lineno)d] | %(message)s'
        )
        ch.setFormatter(formatter)
        
        logger.addHandler(ch)
        cls._instance = logger
        
        return logger
