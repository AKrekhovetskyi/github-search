import os
from datetime import timedelta
from pathlib import Path

CACHE_NAME = Path(__file__).parent.parent / ".cache" / "http-cache"
CACHE_TTL_DEV = timedelta(minutes=60)
CACHE_TTL_PROD = timedelta(minutes=5)

# Set separate global logging level for console and file.
# Supported values: DEBUG, INFO, WARNING, ERROR, CRITICAL.
CONSOLE_LOG_LEVEL = os.environ["CONSOLE_LOG_LEVEL"]
FILE_LOG_LEVEL = os.environ["FILE_LOG_LEVEL"]
