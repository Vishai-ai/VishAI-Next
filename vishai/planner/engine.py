from vishai.models.intent import Intent
from vishai.planner.vocabulary import VocabularyManager
from vishai.planner.parser import IntentParser
from vishai.utils.logger import SystemLogger

logger = SystemLogger.get_logger()

class IntentEngine:
    """
    The main facade for Intent Understanding.
    Coordinates the VocabularyManager and IntentParser.
    """
    def __init__(self, data_dir: str = "./data"):
        vocab_dir = f"{data_dir}/vocabulary"
        self.vocabulary = VocabularyManager(data_dir=vocab_dir)
        self.parser = IntentParser(vocabulary=self.vocabulary)
        
        logger.info("Intent Understanding Engine initialized.")

    def process(self, text: str) -> Intent:
        """
        Processes a natural language string and returns the understood Intent.
        """
        logger.debug(f"Processing text: '{text}'")
        intent = self.parser.parse(text)
        
        if intent.is_valid():
            logger.info(f"Understood Intent: Action={intent.action}, Target={intent.target}, Confidence={intent.confidence}")
        else:
            logger.warning(f"Failed to understand Intent from text: '{text}'")
            
        return intent
