# backend/db.py

"""
Backend data layer for For-All.

Right now this is an in-memory store so the app can run
without needing a real database. You can swap this later
for SQLite using the same function names.
"""

import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash

from app.backend.seed_data import RESOURCES as SEED_RESOURCES
from app.backend.models import Resource

# --- SQLite user database (for login/signup) ---

BASE_DIR = Path(__file__).parent.parent.parent  # project root
DB_FILE = BASE_DIR / "sql" / "forall.db"
DATA_FILE = BASE_DIR / "data" / "baltimore_resources.json"

_JSON_RESOURCES = None


def load_json_resources():
    """
    Load manual Baltimore resources from data/baltimore_resources.json.
    Returns a list of dicts with the same shape as RESOURCES entries.
    If the file is missing or invalid, returns an empty list.
    """
    global _JSON_RESOURCES
    if _JSON_RESOURCES is not None:
        return _JSON_RESOURCES

    if not DATA_FILE.exists():
        _JSON_RESOURCES = []
        return _JSON_RESOURCES

    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        _JSON_RESOURCES = []
        return _JSON_RESOURCES

    normalized = []
    for item in data:
        normalized.append(
            {
                "id": item.get("id"),
                "name": item.get("name", "").strip(),
                "category": item.get("category", "").strip(),
                "neighborhood": item.get("city", "Baltimore, MD"),
                "address": item.get("address", "").strip(),
                "phone": item.get("phone", "").strip(),
                "tags": [item.get("category", "").strip(), "baltimore"],
                "description": item.get("description", "").strip(),
                "website": item.get("website", "").strip(),
            }
        )
    _JSON_RESOURCES = normalized
    return _JSON_RESOURCES


def get_conn():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_user_table():
    """Ensure the users table exists."""
    conn = get_conn()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    conn.close()


# Initialize table on import
init_user_table()


def create_user(email: str, password: str):
    """Create a new user with a hashed password."""
    email = email.strip().lower()
    password_hash = generate_password_hash(password)
    conn = get_conn()
    with conn:
        conn.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, password_hash),
        )
    conn.close()


def get_user(email: str):
    """Return SQLite row for user or None."""
    email = email.strip().lower()
    conn = get_conn()
    cur = conn.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    return row


def verify_user(email: str, password: str) -> bool:
    row = get_user(email)
    if not row:
        return False
    return check_password_hash(row["password_hash"], password)


# --- Fake data for demo / prototype ---

NEIGHBORHOODS = [
    "Baltimore, MD",
    "East Baltimore",
    "West Baltimore",
    "Downtown",
]

RESOURCES = [
    {
        "id": 1,
        "name": "Baltimore Housing Assistance Center",
        "category": "housing",
        "neighborhood": "Baltimore, MD",
        "address": "123 Main St",
        "phone": "(410) 555-0001",
        "tags": ["rental", "voucher", "shelter"],
        "description": "Helps residents find emergency and long-term housing."
    },
    {
        "id": 2,
        "name": "Community Food Pantry",
        "category": "food",
        "neighborhood": "East Baltimore",
        "address": "456 Green Ave",
        "phone": "(410) 555-0002",
        "tags": ["groceries", "food pantry"],
        "description": "Weekly free groceries for families in need."
    },
    {
        "id": 3,
        "name": "Clothing Closet",
        "category": "clothing",
        "neighborhood": "West Baltimore",
        "address": "789 Hope Blvd",
        "phone": "(410) 555-0003",
        "tags": ["winter", "kids", "adult clothing"],
        "description": "Provides free seasonal clothing for all ages."
    },
]

# Merge real Baltimore organizations from seed_data into the generic RESOURCES list.
# This lets the UI show all organizations even if the /api/resources endpoint is not used.
for seed in SEED_RESOURCES:
    if isinstance(seed, Resource):
        RESOURCES.append(
            {
                "id": seed.id + 1000,  # offset to avoid id collisions
                "name": seed.name,
                "category": seed.category,
                "neighborhood": "Baltimore, MD",
                "address": f"{seed.address}, {seed.city}, {seed.state}",
                "phone": seed.phone or "",
                "tags": [seed.category, "community", "support"],
                "description": seed.notes or "",
            }
        )

# Merge manual Baltimore resources (from JSON file) into the RESOURCES list.
RESOURCES.extend(load_json_resources())


# ---------- Core helper functions used by app.py ----------

def list_resources(category: Optional[str] = None, neighborhood: Optional[str] = None, query: Optional[str] = None):
    """
    Return a list of resources filtered by:
      - category (optional)
      - neighborhood (optional)
      - query text in name/description/tags (optional)
    """
    category = (category or "").lower()

    def match(r):
        if category and r["category"].lower() != category:
            return False
        if neighborhood and neighborhood != "All" and r["neighborhood"] != neighborhood:
            return False
        if query:
            q = query.lower()
            haystack = " ".join(
                [r["name"], r["description"], " ".join(r["tags"])]
            ).lower()
            if q not in haystack:
                return False
        return True

    return [r for r in RESOURCES if match(r)]


def add_resource(resource_data: dict):
    """
    Very simple: assign an ID and append to RESOURCES.
    """
    next_id = max((r["id"] for r in RESOURCES), default=0) + 1
    resource = {
        "id": next_id,
        "name": resource_data.get("name", "Untitled"),
        "category": resource_data.get("category", "other").lower(),
        "neighborhood": resource_data.get("neighborhood", "Baltimore, MD"),
        "address": resource_data.get("address", ""),
        "phone": resource_data.get("phone", ""),
        "tags": resource_data.get("tags", []),
        "description": resource_data.get("description", ""),
    }
    RESOURCES.append(resource)
    return resource


def get_stats():
    """
    Return simple stats for the analytics page:
      - count per category
      - count per neighborhood
    """
    by_category = Counter(r["category"] for r in RESOURCES)
    by_neighborhood = Counter(r["neighborhood"] for r in RESOURCES)

    return {
        "total_resources": len(RESOURCES),
        "by_category": dict(by_category),
        "by_neighborhood": dict(by_neighborhood),
    }


def recommend_resource(user_text: str):
    """
    Super simple text-match “recommender”:
    look at the text and pick a resource whose tags/description best match.
    """
    if not user_text:
        return None

    text = user_text.lower()
    scored = []

    for r in RESOURCES:
        score = 0
        # Boost if category keywords show up
        if "house" in text or "shelter" in text:
            if r["category"] == "housing":
                score += 2
        if "food" in text or "meal" in text or "grocer" in text:
            if r["category"] == "food":
                score += 2
        if "clothes" in text or "jacket" in text or "coat" in text:
            if r["category"] == "clothing":
                score += 2

        # Light keyword overlap with tags / description
        haystack = " ".join([r["description"], " ".join(r["tags"])]).lower()
        for word in text.split():
            if word in haystack:
                score += 1

        if score > 0:
            scored.append((score, r))

    if not scored:
        return None

    scored.sort(reverse=True, key=lambda x: x[0])
    return scored[0][1]
