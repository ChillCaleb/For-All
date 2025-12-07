"""
Seed data with real Baltimore organizations.

This module provides a list of actual Baltimore community resources
for housing, food, and clothing assistance.
"""

from app.backend.models import Resource

# Real Baltimore organizations
RESOURCES = [
    # Housing resources
    Resource(
        id=1,
        name="Weinberg Housing & Resource Center",
        category="housing",
        address="620 Fallsway",
        city="Baltimore",
        state="MD",
        phone="(410) 396-4884",
        notes="Emergency shelter and housing assistance"
    ),
    Resource(
        id=2,
        name="Sarah's Hope Shelter",
        category="housing",
        address="1114 Mount Street",
        city="Baltimore",
        state="MD",
        phone="(410) 467-9000",
        notes="Emergency shelter for families"
    ),
    Resource(
        id=3,
        name="Project PLASE",
        category="housing",
        address="3549-3601 Old Frederick Rd",
        city="Baltimore",
        state="MD",
        phone="(410) 837-1400",
        notes="Transitional housing and support services"
    ),
    Resource(
        id=4,
        name="Helping Up Mission",
        category="housing",
        address="1029 E Baltimore St",
        city="Baltimore",
        state="MD",
        phone="(410) 675-7500",
        notes="Emergency shelter and recovery services"
    ),
    
    # Food resources
    Resource(
        id=5,
        name="Bea Gaddy Family Center",
        category="food",
        address="425 N Chester St",
        city="Baltimore",
        state="MD",
        phone="(410) 563-2749",
        notes="Food pantry and meal services"
    ),
    Resource(
        id=6,
        name="Beans and Bread",
        category="food",
        address="402 S Bond St",
        city="Baltimore",
        state="MD",
        phone="(410) 732-1892",
        notes="Daily meal service and food assistance"
    ),
    Resource(
        id=7,
        name="Second Shiloh Meal Kitchen & Emergency Food Pantry",
        category="food",
        address="1355 Homestead St",
        city="Baltimore",
        state="MD",
        phone="(410) 342-8000",
        notes="Meal kitchen and emergency food pantry"
    ),
    Resource(
        id=8,
        name="Donald Bentley Food Pantry",
        category="food",
        address="2405 Loch Raven Rd",
        city="Baltimore",
        state="MD",
        phone="(410) 467-4000",
        notes="Food pantry services"
    ),
    
    # Clothing resources
    Resource(
        id=9,
        name="Paul's Place Clothing Marketplace",
        category="clothing",
        address="1118 Ward St",
        city="Baltimore",
        state="MD",
        phone="(410) 625-0775",
        notes="Free clothing for community members"
    ),
    Resource(
        id=10,
        name="CFUF Clothes Closet",
        category="clothing",
        address="2201 N Monroe St",
        city="Baltimore",
        state="MD",
        phone="(410) 367-5691",
        notes="Clothing assistance program"
    ),
    Resource(
        id=11,
        name="KDW Cares Clothing Closet",
        category="clothing",
        address="6806 Harford Rd",
        city="Baltimore",
        state="MD",
        phone="(410) 426-6000",
        notes="Community clothing closet"
    ),
    Resource(
        id=12,
        name="The Blessing Closet",
        category="clothing",
        address="6000 Radecke Ave",
        city="Baltimore",
        state="MD",
        phone="(410) 426-6000",
        notes="Free clothing and household items"
    ),
    Resource(
        id=13,
        name="Dress for Success Baltimore",
        category="clothing",
        address="250 W Dickman St",
        city="Baltimore",
        state="MD",
        phone="(410) 727-8900",
        website="https://baltimore.dressforsuccess.org",
        notes="Professional attire for job interviews"
    ),
]

