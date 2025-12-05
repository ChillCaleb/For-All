# test_backend.py
from backend import db

def main():
    print("Listing organizations...")
    orgs = db.list_organizations()
    print(orgs)

    print("\nSearching for food resources...")
    resources = db.search_resources(category="food")
    for r in resources:
        print(f"- {r['name']} ({r.get('availability_status')})")

if __name__ == "__main__":
    main()
