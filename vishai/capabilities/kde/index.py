import json
import os
import dataclasses
from typing import Dict, List
from vishai.models.resource import SystemResource
from vishai.utils.logger import SystemLogger

logger = SystemLogger.get_logger()

class ResourceIndex:
    """
    Maintains the discovered resources.
    Supports incremental updates to preserve learned state and merges aliases.
    """
    def __init__(self, data_dir: str):
        self.data_dir = os.path.join(data_dir, "kde")
        self.index_file = os.path.join(self.data_dir, "resource_index.json")
        self._resources: Dict[str, SystemResource] = {}
        
        os.makedirs(self.data_dir, exist_ok=True)
        self.load()

    def add_or_update(self, resource: SystemResource) -> None:
        """
        Incrementally updates a resource, preserving data maintained by the Learning Engine.
        """
        if resource.id in self._resources:
            existing = self._resources[resource.id]
            
            # Preserve Learning Engine Fields
            resource.capabilities = existing.capabilities
            resource.usage_history = existing.usage_history
            resource.success_rate = existing.success_rate
            resource.failure_rate = existing.failure_rate
            resource.last_used = existing.last_used
            resource.favorite = existing.favorite
            
            # Merge dynamically learned aliases
            combined_aliases = set(existing.aliases + resource.aliases)
            resource.aliases = list(combined_aliases)
            
        self._resources[resource.id] = resource

    def search(self, query: str) -> List[SystemResource]:
        """
        Retrieves resources matching the semantic query.
        Matches against display_name and learned aliases.
        """
        query = query.lower()
        results = []
        for res in self._resources.values():
            if query in res.display_name.lower():
                results.append(res)
                continue
            for alias in res.aliases:
                if query in alias.lower():
                    results.append(res)
                    break
        return results

    def save(self) -> None:
        """Persists the resource index to disk."""
        data = {k: dataclasses.asdict(v) for k, v in self._resources.items()}
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            logger.debug(f"Saved {len(self._resources)} resources to index.")
        except Exception as e:
            logger.error(f"Failed to save resource index: {e}")

    def load(self) -> None:
        """Loads the resource index from disk."""
        if not os.path.exists(self.index_file):
            return
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for k, v in data.items():
                self._resources[k] = SystemResource(**v)
            logger.info(f"Loaded {len(self._resources)} resources from index.")
        except Exception as e:
            logger.error(f"Failed to load resource index: {e}")
