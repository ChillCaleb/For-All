# backend/db.py
import math
from typing import Optional, List, Dict, Any
from .config import get_client  # use the shared client


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points in miles."""
    R = 3958.8  # Earth radius in miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = phi2 - phi1
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ---------- organization ops ----------

def list_organizations() -> List[Dict[str, Any]]:
    client = get_client()
    resp = client.table("organizations").select("*").execute()
    return resp.data or []


def create_organization(name: str, **kwargs) -> Dict[str, Any]:
    client = get_client()
    data = {"name": name, **kwargs}
    resp = client.table("organizations").insert(data).execute()
    return resp.data[0]


# ---------- resource ops ----------

def create_resource(
    org_id: Optional[str],
    name: str,
    category: str,
    description: str = "",
    address: str = "",
    city: str = "",
    state: str = "",
    zip_code: str = "",
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    capacity_total: int = 0,
    capacity_available: int = 0,
) -> Dict[str, Any]:
    """Insert a new resource row."""
    client = get_client()
    data = {
        "org_id": org_id,
        "name": name,
        "category": category,
        "description": description,
        "address": address,
        "city": city,
        "state": state,
        "zip": zip_code,
        "lat": lat,
        "lng": lng,
        "capacity_total": capacity_total,
        "capacity_available": capacity_available,
    }
    resp = client.table("resources").insert(data).execute()
    return resp.data[0]


def search_resources(
    category: Optional[str] = None,
    org_ids: Optional[List[str]] = None,
    keyword: Optional[str] = None,
    user_lat: Optional[float] = None,
    user_lng: Optional[float] = None,
    max_distance_miles: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Core search logic:
    - filter by category
    - filter by organization IDs
    - search by keyword in name/description
    - optionally filter by distance from user_lat/user_lng
    """
    client = get_client()
    # use a view if you create one, otherwise change to "resources"
    query = client.table("resource_with_status").select("*")

    if category:
        query = query.eq("category", category)

    if org_ids:
        query = query.in_("org_id", org_ids)

    if keyword:
        # OR over name/description using ilike
        query = query.or_(f"name.ilike.%{keyword}%,description.ilike.%{keyword}%")

    resp = query.execute()
    resources = resp.data or []

    # Client-side distance filter
    if user_lat is not None and user_lng is not None and max_distance_miles is not None:
        filtered: List[Dict[str, Any]] = []
        for r in resources:
            if r.get("lat") is None or r.get("lng") is None:
                continue
            d = haversine_miles(user_lat, user_lng, r["lat"], r["lng"])
            if d <= max_distance_miles:
                r = dict(r)  # shallow copy so we don't mutate the original
                r["distance_miles"] = round(d, 2)
                filtered.append(r)
        resources = filtered

    return resources


# ---------- request workflow ----------

def submit_request(
    resource_id: str,
    requester_name: str,
    requester_phone: str,
    requester_notes: str = "",
) -> Dict[str, Any]:
    """
    Backing logic for 'Request this resource':
    - creates a request row
    - decrements resource.capacity_available (simple, non-transactional)
    """
    client = get_client()
    req_resp = client.table("requests").insert(
        {
            "resource_id": resource_id,
            "requester_name": requester_name,
            "requester_phone": requester_phone,
            "requester_notes": requester_notes,
        }
    ).execute()
    request = req_resp.data[0]

    res_resp = (
        client.table("resources")
        .select("id, capacity_available")
        .eq("id", resource_id)
        .single()
        .execute()
    )
    resource = res_resp.data

    if resource and resource.get("capacity_available") is not None and resource["capacity_available"] > 0:
        new_avail = resource["capacity_available"] - 1
        client.table("resources").update(
            {"capacity_available": new_avail}
        ).eq("id", resource_id).execute()

    return request


def update_request_status(request_id: str, status: str) -> Dict[str, Any]:
    """Admin/provider uses this to mark a request as approved/denied/fulfilled/etc."""
    client = get_client()
    resp = (
        client.table("requests")
        .update({"status": status})
        .eq("id", request_id)
        .execute()
    )
    return resp.data[0]


def list_requests_for_resource(resource_id: str) -> List[Dict[str, Any]]:
    client = get_client()
    resp = (
        client.table("requests")
        .select("*")
        .eq("resource_id", resource_id)
        .execute()
    )
    return resp.data or []


# ---------- analytics ----------

def get_resource_counts_by_category() -> List[Dict[str, Any]]:
    """Return resource counts grouped by category (for analytics view)."""
    client = get_client()
    resp = (
        client.table("resources")
        .select("category, count:id")
        .group("category")
        .execute()
    )
    return resp.data or []


def get_request_status_stats() -> Dict[str, int]:
    """Return counts of requests in each status and a total."""
    client = get_client()
    resp = (
        client.table("requests")
        .select("status, count:id")
        .group("status")
        .execute()
    )
    rows = resp.data or []
    stats: Dict[str, int] = {row["status"]: row["count"] for row in rows}
    stats["total"] = sum(stats.values())
    return stats
