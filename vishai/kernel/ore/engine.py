from typing import List, Optional

from vishai.models.intent import Intent
from vishai.models.resource import SystemResource
from vishai.models.resolution import ResolutionResult
from vishai.capabilities.kde.engine import KnowledgeDiscoveryEngine
from vishai.kernel.ore.ranking import RankingProfile
from vishai.kernel.ore.matcher import ObjectMatcher
from vishai.utils.logger import SystemLogger

logger = SystemLogger.get_logger()

class ObjectResolutionEngine:
    """
    Object Resolution Engine (ORE).
    Resolves an Intent or text query to a SystemResource without executing any action.
    """
    def __init__(self, kde: KnowledgeDiscoveryEngine):
        self.kde = kde
        self.ranking_profile = RankingProfile() # Configurable by Learning Engine
        self.matcher = ObjectMatcher(self.ranking_profile)
        logger.info("Object Resolution Engine (ORE) initialized.")

    def resolve(self, intent: Intent) -> ResolutionResult:
        """
        Resolves a full Intent into the best matching SystemResource.
        Uses intent.target or intent.object.
        """
        query = intent.target or intent.object
        if not query:
            return ResolutionResult(
                resource=None,
                confidence=0.0,
                reason="Intent has no target or object to resolve.",
                matching_method="none"
            )
            
        return self.resolve_by_name(query)

    def resolve_by_name(self, name: str) -> ResolutionResult:
        """
        Resolves a name, alias, or category into the best matching SystemResource.
        """
        logger.debug(f"ORE resolving by name: '{name}'")
        best_result = ResolutionResult(None, 0.0, "No matching resource found", "none")
        
        # We iterate over all resources from KDE.
        # In the future, KDE should provide a faster filter, but for now we evaluate all.
        for resource in self.kde.index._resources.values():
            result = self.matcher.evaluate(name, resource)
            if result.resource and result.confidence > best_result.confidence:
                best_result = result
                
        if best_result.resource:
            logger.info(f"ORE resolved '{name}' to {best_result.resource.display_name} (Confidence: {best_result.confidence:.2f} via {best_result.matching_method})")
        else:
            logger.warning(f"ORE failed to resolve '{name}'.")
            
        return best_result

    def resolve_by_id(self, resource_id: str) -> ResolutionResult:
        """
        Resolves a specific resource ID exactly.
        """
        logger.debug(f"ORE resolving by ID: '{resource_id}'")
        resource = self.kde.index._resources.get(resource_id)
        if resource:
            logger.info(f"ORE resolved ID '{resource_id}' to {resource.display_name}")
            return ResolutionResult(
                resource=resource,
                confidence=1.0,
                reason="Exact ID match",
                matching_method="id"
            )
            
        logger.warning(f"ORE failed to resolve ID '{resource_id}'.")
        return ResolutionResult(
            resource=None,
            confidence=0.0,
            reason="Resource ID not found in KDE index.",
            matching_method="none"
        )
