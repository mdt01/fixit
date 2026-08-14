"""Settings come from environment variables; nothing secret lives in the code."""

import os

DATABASE_URL = os.getenv("FIXIT_DB", "sqlite:///./fixit.db")
TOKEN_HOURS = int(os.getenv("FIXIT_TOKEN_HOURS", "12"))
