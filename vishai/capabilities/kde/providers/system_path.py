import os
import sys
import time
from typing import List
from vishai.models.resource import SystemResource
from vishai.capabilities.kde.provider import ResourceProvider
from vishai.utils.logger import SystemLogger

logger = SystemLogger.get_logger()

class SystemPathProvider(ResourceProvider):
    """
    Discovers generic portable executable files exposed in the system PATH.
    """
    
    @property
    def name(self) -> str:
        return "system_path_executables"

    def discover(self) -> List[SystemResource]:
        resources: List[SystemResource] = []
        path_env = os.environ.get("PATH", "")
        if not path_env:
            return resources
            
        directories = path_env.split(os.pathsep)
        seen = set()
        
        # extensions for windows
        exts = os.environ.get("PATHEXT", ".COM;.EXE;.BAT;.CMD").split(";") if sys.platform == "win32" else [""]
        current_time = time.time()
        
        for directory in directories:
            if not os.path.isdir(directory):
                continue
                
            try:
                for filename in os.listdir(directory):
                    if filename in seen:
                        continue
                        
                    filepath = os.path.join(directory, filename)
                    if os.path.isfile(filepath) and os.access(filepath, os.X_OK):
                        seen.add(filename)
                        display_name = filename
                        
                        if sys.platform == "win32":
                            # Strip extension for display name
                            for ext in exts:
                                if filename.upper().endswith(ext.upper()):
                                    display_name = filename[:-len(ext)]
                                    break
                                    
                        res = SystemResource(
                            id=f"path_{display_name.lower().replace(' ', '_')}",
                            display_name=display_name,
                            type="executable",
                            source=self.name,
                            path=filepath,
                            last_seen=current_time
                        )
                        resources.append(res)
            except OSError:
                # Permission denied or invalid directory structure
                continue
                
        return resources
