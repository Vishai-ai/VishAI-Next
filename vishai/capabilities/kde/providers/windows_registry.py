import sys
import time
from typing import List
from vishai.models.resource import SystemResource
from vishai.capabilities.kde.provider import ResourceProvider
from vishai.utils.logger import SystemLogger

logger = SystemLogger.get_logger()

class WindowsRegistryProvider(ResourceProvider):
    """
    Discovers installed Windows applications by interrogating the Registry uninstall keys.
    Gracefully yields empty results if not running on Windows.
    """
    
    @property
    def name(self) -> str:
        return "windows_registry"

    def discover(self) -> List[SystemResource]:
        resources: List[SystemResource] = []
        if sys.platform != "win32":
            return resources
            
        try:
            import winreg
            keys_to_check = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            ]
            
            current_time = time.time()
            for hive, path in keys_to_check:
                try:
                    with winreg.OpenKey(hive, path) as key:
                        for i in range(0, winreg.QueryInfoKey(key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    except OSError:
                                        continue  # DisplayName is required
                                        
                                    display_icon = ""
                                    publisher = ""
                                    version = ""
                                    install_location = ""
                                    
                                    try: display_icon = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                                    except OSError: pass
                                    try: publisher = winreg.QueryValueEx(subkey, "Publisher")[0]
                                    except OSError: pass
                                    try: version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                    except OSError: pass
                                    try: install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                    except OSError: pass
                                    
                                    if display_name:
                                        res = SystemResource(
                                            id=f"winreg_{display_name.lower().replace(' ', '_')}",
                                            display_name=display_name,
                                            type="application",
                                            source=self.name,
                                            path=install_location if install_location else display_icon,
                                            publisher=publisher,
                                            version=version,
                                            last_seen=current_time,
                                            metadata={"registry_key": subkey_name}
                                        )
                                        resources.append(res)
                            except OSError:
                                continue
                except OSError:
                    continue
        except ImportError:
            logger.warning("winreg module not available on this platform despite sys.platform check.")
            
        return resources
