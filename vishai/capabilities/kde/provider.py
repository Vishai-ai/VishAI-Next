from abc import ABC, abstractmethod
from typing import List
from vishai.models.resource import SystemResource

class ResourceProvider(ABC):
    """
    Base interface for all Knowledge Discovery Providers.
    Allows dynamically registering discovery plugins without modifying Kernel logic.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The unique identifier for this provider."""
        pass

    @abstractmethod
    def discover(self) -> List[SystemResource]:
        """Runs the discovery process and returns discovered SystemResources."""
        pass
