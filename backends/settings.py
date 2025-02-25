import os

ENABLE_DEBUG_MODE = os.environ.get("ENABLE_DEBUG_MODE", "True").lower() == "true"
