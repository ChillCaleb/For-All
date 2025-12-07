# Resources API Documentation

## Overview

The Resources API provides access to community resources in Baltimore, including housing, food, and clothing assistance organizations.

## Resource Model

The `Resource` model is a dataclass with the following fields:

- `id` (int): Unique identifier for the resource
- `name` (str): Name of the organization
- `category` (str): Resource category - one of: `"housing"`, `"food"`, or `"clothing"`
- `address` (str): Street address
- `city` (str): City name (default: "Baltimore")
- `state` (str): State abbreviation (default: "MD")
- `phone` (str | None): Phone number (optional)
- `website` (str | None): Website URL (optional)
- `notes` (str | None): Additional notes or description (optional)

The model includes a `to_dict()` method that returns a plain dictionary for JSON serialization.

## Endpoint

### GET /api/resources

Returns a list of resources filtered by category and/or city.

#### Query Parameters

- `category` (optional): Filter by category. Valid values: `"housing"`, `"food"`, `"clothing"`
- `city` (optional, default: `"Baltimore"`): Filter by city name (case-insensitive)

#### Example Request

```
GET /api/resources?category=housing&city=Baltimore
```

#### Example Response

```json
[
  {
    "id": 1,
    "name": "Weinberg Housing & Resource Center",
    "category": "housing",
    "address": "620 Fallsway",
    "city": "Baltimore",
    "state": "MD",
    "phone": "(410) 396-4884",
    "website": null,
    "notes": "Emergency shelter and housing assistance"
  },
  {
    "id": 2,
    "name": "Sarah's Hope Shelter",
    "category": "housing",
    "address": "1114 Mount Street",
    "city": "Baltimore",
    "state": "MD",
    "phone": "(410) 467-9000",
    "website": null,
    "notes": "Emergency shelter for families"
  }
]
```

#### Response Codes

- `200 OK`: Successfully retrieved resources (may return empty array if no matches)
- `500 Internal Server Error`: Server error (should not occur with proper error handling)

#### Error Handling

If no resources match the criteria, the API returns an empty array `[]` rather than an error. This ensures the frontend can gracefully handle cases where no resources are found.

## Data Source

Currently, the API uses in-memory seed data with real Baltimore organizations:

- **Housing**: Weinberg Housing & Resource Center, Sarah's Hope Shelter, Project PLASE, Helping Up Mission
- **Food**: Bea Gaddy Family Center, Beans and Bread, Second Shiloh Meal Kitchen, Donald Bentley Food Pantry
- **Clothing**: Paul's Place Clothing Marketplace, CFUF Clothes Closet, KDW Cares Clothing Closet, The Blessing Closet, Dress for Success Baltimore

This seed data can later be moved to a database (SQLite, PostgreSQL, etc.) without changing the API interface.

## Future Enhancements

- Database integration (replace in-memory storage)
- Additional filtering options (zipcode, distance, etc.)
- Pagination for large result sets
- Authentication for admin endpoints

