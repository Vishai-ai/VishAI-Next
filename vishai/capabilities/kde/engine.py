from typing import List, Type
from vishai.models.resource import SystemResource
from vishai.capabilities.kde.provider import ResourceProvider
from vishai.capabilities.kde.index import ResourceIndex
from vishai.utils.logger import SystemLogger

logger = SystemLogger.get_logger()

class KnowledgeDiscoveryEngine:
    """
    Knowledge Discovery Engine (KDE).
    Dynamically registers providers and orchestrates resource discovery 
    without knowing provider implementation details.
    """
    def __init__(self, data_dir: str):
        self.index = ResourceIndex(data_dir=data_dir)
        self._providers: List[ResourceProvider] = []
        
        logger.info("Knowledge Discovery Engine (KDE) initialized.")
        
    def register_provider(self, provider_class: Type[ResourceProvider]) -> None:
        """Dynamically loads a discovery provider."""
        try:
            provider = provider_class()
            self._providers.append(provider)
            logger.debug(f"Registered KDE provider: {provider.name}")
        except Exception as e:
            logger.error(f"Failed to register provider {provider_class.__name__}: {e}")

    def discover_all(self) -> None:
        """
        Orchestrates discovery across all registered providers.
        Incrementally updates the index.
        """
        logger.info("Starting knowledge discovery across all providers...")
        total_discovered = 0
        for provider in self._providers:
            try:
                resources = provider.discover()
                for res in resources:
                    self.index.add_or_update(res)
                total_discovered += len(resources)
                logger.debug(f"Provider '{provider.name}' discovered {len(resources)} resources.")
            except Exception as e:
                logger.error(f"Provider '{provider.name}' encountered an error: {e}", exc_info=True)
                
        self.index.save()
        logger.info(f"Knowledge discovery complete. Total resources updated: {total_discovered}")
