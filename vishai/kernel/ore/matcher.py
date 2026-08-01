from typing import List, Tuple
from vishai.models.resource import SystemResource
from vishai.models.resolution import ResolutionResult
from vishai.kernel.ore.ranking import RankingProfile

class ObjectMatcher:
    """
    Evaluates how well a query matches a resource using a configurable RankingProfile.
    """
    def __init__(self, profile: RankingProfile):
        self.profile = profile

    def evaluate(self, query: str, resource: SystemResource) -> ResolutionResult:
        query = query.lower().strip()
        display_name = resource.display_name.lower()
        
        confidence = 0.0
        reason = "No match"
        matching_method = "none"

        # 1. Exact Name Match
        if query == display_name:
            confidence = self.profile.exact_match_weight
            reason = "Exact display name match"
            matching_method = "exact"
        
        # 2. Alias Match
        elif any(query == alias.lower() for alias in resource.aliases):
            confidence = self.profile.alias_match_weight
            reason = "Exact alias match"
            matching_method = "alias"
            
        # 3. Partial Match
        elif query in display_name or any(query in alias.lower() for alias in resource.aliases):
            confidence = self.profile.partial_match_weight
            reason = "Partial string match"
            matching_method = "partial"
            
        # 4. Category / Action match
        # E.g. "browser" -> resource with supported action "browse" or category "browser"
        # We check capabilities and supported_actions
        elif query in [cap.lower() for cap in resource.capabilities] or query in [act.lower() for act in resource.supported_actions]:
            confidence = self.profile.category_match_weight
            reason = "Category/Capability match"
            matching_method = "category"

        # Boost by history if we have an initial match
        if confidence > 0.0:
            # Simple heuristic: boost by usage rate/history if learned
            history_boost = min(self.profile.history_weight_max, (len(resource.usage_history) * 0.05) + (resource.success_rate * 0.1))
            if resource.favorite:
                history_boost += 0.1
                
            confidence = min(1.0, confidence + history_boost)
            if history_boost > 0:
                reason += " (boosted by history/learning)"
                
        return ResolutionResult(
            resource=resource if confidence >= self.profile.minimum_confidence_threshold else None,
            confidence=confidence,
            reason=reason,
            matching_method=matching_method
        )
