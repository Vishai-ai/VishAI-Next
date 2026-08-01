import re
from typing import List, Tuple

from vishai.models.intent import Intent
from vishai.planner.vocabulary import VocabularyManager
from vishai.utils.logger import SystemLogger

logger = SystemLogger.get_logger()

class IntentParser:
    """
    Parses natural language into structured Intent objects.
    Uses VocabularyManager to resolve meanings and filter noise.
    """
    def __init__(self, vocabulary: VocabularyManager):
        self.vocabulary = vocabulary
        # Define core system actions that the OS supports
        self.supported_actions = {"launch", "close", "search", "type"}

    def parse(self, text: str) -> Intent:
        """Parses raw text and returns a strongly typed Intent."""
        intent = Intent(original_text=text)
        
        # 1. Normalize
        normalized = self._normalize_text(text)
        intent.normalized_text = normalized
        
        # 2. Tokenize
        raw_tokens = normalized.split()
        
        # 3. Filter and Resolve
        filtered_tokens = []
        for token in raw_tokens:
            if self.vocabulary.is_polite(token):
                continue
            resolved = self.vocabulary.resolve(token)
            filtered_tokens.append(resolved)
        
        # 4. Extract Intent Components
        self._extract_components(filtered_tokens, intent)
        
        # 5. Calculate Confidence (Basic implementation, will be enhanced by Learning Engine)
        if intent.action:
            intent.confidence = 0.8 if not intent.unknown_tokens else 0.5
            if intent.target:
                intent.confidence = min(1.0, intent.confidence + 0.2)
        else:
            intent.confidence = 0.0
            
        return intent

    def _normalize_text(self, text: str) -> str:
        """Removes punctuation and converts to lowercase."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def _extract_components(self, tokens: List[str], intent: Intent) -> None:
        """Heuristically extracts action, target, and objects from tokens."""
        for token in tokens:
            if token in self.supported_actions and not intent.action:
                intent.action = token
                intent.matched_tokens.append(token)
            elif intent.action and not intent.target:
                # If we have an action, assume the next significant word is the target
                intent.target = token
                intent.matched_tokens.append(token)
            else:
                # Store extra words as unknown or object depending on context
                # For now, put them in unknown tokens for the Learning Engine
                intent.unknown_tokens.append(token)
