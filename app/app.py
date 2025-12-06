
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import app.backend
BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from flask import Flask, render_template, request, redirect, url_for
from app.backend.db import (
    list_resources,
    add_resource,
    get_stats,
    recommend_resource,
    NEIGHBORHOODS,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)


@app.route("/", methods=["GET", "POST"])
def index():
    recommendation = None
    if request.method == "POST":
        user_text = request.form.get("need_description", "").strip()
        if user_text:
            recommendation = recommend_resource(user_text)
    return render_template("index.html", recommendation=recommendation)


@app.route("/category/<category>")
def category_page(category):
    neighborhood = request.args.get("neighborhood", "")
    query = request.args.get("q", "")
    resources = list_resources(category=category, neighborhood=neighborhood, query=query)
    return render_template(
        "category.html",
        category=category,
        neighborhoods=NEIGHBORHOODS,
        selected_neighborhood=neighborhood,
        query=query,
        resources=resources,
    )


@app.route("/tips")
def tips():
    # Hard-coded community tips for now
    posts = [
        {
            "title": "Staying Warm in Winter",
            "body": "Layer clothing, use local warming centers, and check shelters with extended hours.",
        },
        {
            "title": "Making the Most of Food Pantries",
            "body": "Bring reusable bags, ask about dietary options, and look for fresh produce days.",
        },
        {
            "title": "Important Documents",
            "body": "Keep copies of IDs and important papers in a safe folder or with a trusted friend.",
        },
    ]
    return render_template("tips.html", posts=posts)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    created = None
    if request.method == "POST":
        form = request.form
        created = add_resource(
            {
                "name": form.get("name", ""),
                "category": form.get("category", ""),
                "neighborhood": form.get("neighborhood", ""),
                "description": form.get("description", ""),
                "address": form.get("address", ""),
                "phone": form.get("phone", ""),
            }
        )
    # Show all resources so NGOs can see their additions
    resources = list_resources()
    return render_template(
        "admin.html", created=created, neighborhoods=NEIGHBORHOODS, resources=resources
    )


@app.route("/analytics")
def analytics():
    stats = get_stats()
    return render_template("analytics.html", stats=stats)


if __name__ == "__main__":
    # For demo, enable debug so you see changes live
    app.run(debug=True)
