from dataclasses import dataclass

@dataclass
class RankingProfile:
    """
    Configurable weights for the Object Resolution Engine (ORE).
    Allows the future Learning Engine to tune ranking without changing code.
    """
    exact_match_weight: float = 1.0
    alias_match_weight: float = 0.8
    partial_match_weight: float = 0.5
    history_weight_max: float = 0.3
    category_match_weight: float = 0.6
    
    # Thresholds
    minimum_confidence_threshold: float = 0.4
