import os
from pathlib import Path

print(os.listdir(os.path.join(Path.home(), '.surf', 'logs')))[-1]
