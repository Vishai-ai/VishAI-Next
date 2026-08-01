from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class SystemResource:
    """
    Core resource model representing an executable entity (application, script, service, etc.).
    Shared across the entire VishAI OS.
    """
    id: str
    display_name: str
    aliases: List[str] = field(default_factory=list)
    path: str = ""
    type: str = ""  # e.g., 'application', 'executable', 'url'
    source: str = "" # Name of the provider that discovered this
    version: Optional[str] = None
    publisher: Optional[str] = None
    icon: Optional[str] = None
    last_seen: float = 0.0
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Learning Engine Hooks (Maintained incrementally by future learning modules)
    capabilities: List[str] = field(default_factory=list)
    supported_actions: List[str] = field(default_factory=list)
    usage_history: List[float] = field(default_factory=list)
    success_rate: float = 0.0
    failure_rate: float = 0.0
    last_used: float = 0.0
    favorite: bool = False
