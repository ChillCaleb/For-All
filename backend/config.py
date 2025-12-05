# backend/config.py
import os
from typing import Optional
from supabase import create_client, Client

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is optional, but recommended
    pass

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_client() -> Client:
    """Return the global Supabase client or raise if missing."""
    if supabase is None:
        raise RuntimeError(
            "Supabase client not initialized. "
            "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your .env."
        )
    return supabase
