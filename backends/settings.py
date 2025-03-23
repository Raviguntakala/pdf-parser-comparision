import os

ENABLE_DEBUG_MODE = os.environ.get("ENABLE_DEBUG_MODE", "True").lower() == "true"
ENABLE_FORMULA = os.environ.get("ENABLE_FORMULA", "False").lower() == "true"
