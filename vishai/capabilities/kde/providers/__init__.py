from .system_path import SystemPathProvider
from .windows_registry import WindowsRegistryProvider

# Kernel will use this generic list to avoid hardcoding specific providers
DEFAULT_PROVIDERS = [
    SystemPathProvider,
    WindowsRegistryProvider
]
