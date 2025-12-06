# backend/db.py

"""
Backend data layer for For-All.

Right now this is an in-memory store so the app can run
without needing a real database. You can swap this later
for SQLite using the same function names.
"""

from collections import Counter
from typing import Optional

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
