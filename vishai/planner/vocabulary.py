import json
import os
from typing import Dict, List, Set

from vishai.utils.logger import SystemLogger

logger = SystemLogger.get_logger()

class VocabularyManager:
    """
    Manages the language understanding vocabulary.
    Supports synonyms, polite words, stop words, languages, learned words, and custom words.
    Designed to be updated by the Learning Engine.
    """
    def __init__(self, data_dir: str = "./data/vocabulary"):
        self.data_dir = data_dir
        self.synonyms: Dict[str, str] = {}
        self.polite_words: Set[str] = set()
        self.stop_words: Set[str] = set()
        self.languages: Set[str] = set()
        self.learned_words: Dict[str, str] = {}
        self.custom_words: Dict[str, str] = {}
        
        self._ensure_data_dir()
        self._load_defaults()
        self.load_all()

    def _ensure_data_dir(self) -> None:
        os.makedirs(self.data_dir, exist_ok=True)

    def _load_defaults(self) -> None:
        """Loads hardcoded foundational defaults if files are empty/missing."""
        # Polite words that should be ignored
        default_polite = [
            "please", "can", "could", "would", "you", "i", "want", "to", "need", "kindly",
            "kholo", "start", "my"  # adding some general noise words, 'kholo' is 'open' in Hindi
        ]
        
        # Synonyms mapping to core actions or targets
        default_synonyms = {
            "open": "launch",
            "start": "launch",
            "run": "launch",
            "kholo": "launch", # Multi-lingual alias
            "browser": "chrome"
        }
        
        self.polite_words.update(default_polite)
        self.synonyms.update(default_synonyms)

    def load_all(self) -> None:
        """Loads vocabulary from persistent storage."""
        # Future implementation will load learned/custom words from self.data_dir
        logger.debug("Vocabulary loaded.")

    def save_all(self) -> None:
        """Saves current vocabulary to persistent storage."""
        # Future implementation will save to self.data_dir
        pass

    def add_learned_word(self, word: str, mapping: str) -> None:
        """Allows the Learning Engine to teach new words."""
        self.learned_words[word.lower()] = mapping.lower()
        self.save_all()

    def resolve(self, word: str) -> str:
        """
        Resolves a word to its base meaning, checking learned, custom, and synonyms.
        """
        word_lower = word.lower()
        if word_lower in self.custom_words:
            return self.custom_words[word_lower]
        if word_lower in self.learned_words:
            return self.learned_words[word_lower]
        if word_lower in self.synonyms:
            return self.synonyms[word_lower]
        return word_lower

    def is_polite(self, word: str) -> bool:
        """Checks if a word is a polite or stop word."""
        return word.lower() in self.polite_words or word.lower() in self.stop_words
