import sys
sys.path.append('.')
from vishai.kernel.config import SystemConfig
from vishai.models.resource import SystemResource
from vishai.capabilities.kde.index import ResourceIndex
import time

index = ResourceIndex(data_dir='./data')
res = SystemResource(
    id="test_chrome",
    display_name="chrome",
    type="application",
    source="mock",
    path="/usr/bin/chrome",
    last_seen=time.time(),
    aliases=["google chrome"]
)
index.add_or_update(res)
index.save()
print("Added chrome")
