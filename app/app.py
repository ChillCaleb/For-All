
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import app.backend
BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from groq import Groq
from app.backend.db import (
    list_resources,
    add_resource,
    get_stats,
    recommend_resource,
    NEIGHBORHOODS,
    create_user,
    verify_user,
)
from app.backend.seed_data import RESOURCES as SEED_RESOURCES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "gsk_sMvN80aF0zXBml5uykVKWGdyb3FYTDYI7wkdNY5QQNX")


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


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if verify_user(email, password):
            session["user_email"] = email.strip().lower()
            flash("Logged in successfully.")
            return redirect(url_for("index"))
        else:
            error = "Invalid email or password."

    return render_template("login.html", error=error)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not email or not password:
            error = "Email and password are required."
        elif password != confirm:
            error = "Passwords do not match."
        else:
            try:
                create_user(email, password)
                flash("Account created successfully. Please log in.")
                return redirect(url_for("login"))
            except Exception:
                # most likely UNIQUE constraint
                error = "An account with that email already exists."

    return render_template("signup.html", error=error)


@app.route("/logout")
def logout():
    session.pop("user_email", None)
    flash("You have been logged out.")
    return redirect(url_for("index"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    if request.method == "POST":
        user_message = request.json.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        try:
            client = Groq(api_key=GROQ_API_KEY)
            
            # Create a helpful system prompt for resource assistance
            system_prompt = """You are a helpful assistant for the For All platform, which connects Baltimore residents with essential resources including housing, food, clothing, and aid services. 
            
Your role is to:
- Help users find resources they need
- Answer questions about available services
- Provide guidance on how to access resources
- Be empathetic and supportive
- Direct users to call 211 for emergencies

Keep responses concise, friendly, and focused on connecting people with resources."""
            
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            bot_response = response.choices[0].message.content
            return jsonify({"response": bot_response})
            
        except Exception as e:
            return jsonify({"error": f"Error: {str(e)}"}), 500
    
    return render_template("chatbot.html")


@app.route("/news")
def news():
    # Hard-coded articles for now
    posts = [
        {
            "id": 1,
            "title": "For All launches in Baltimore",
            "snippet": "Connecting neighbors to housing, food, and clothing.",
            "body": "For All is excited to announce its official launch in Baltimore, Maryland. Our mission is to connect community members with essential resources including housing assistance, food pantries, and clothing services.\n\nWe've partnered with over a dozen local organizations across the city, including Weinberg Housing & Resource Center, Bea Gaddy Family Center, Paul's Place, and many others. These trusted community partners provide critical support services to residents in need.\n\nWhether you're looking for emergency shelter, weekly groceries, or professional attire for job interviews, For All makes it easy to find the right resource in your neighborhood. Simply describe what you need, and we'll help you find the best match.\n\nOur platform is designed to be accessible and user-friendly, with a mobile-first approach that works on any device. We believe everyone deserves access to essential resources, and we're here to help make those connections happen."
        },
        {
            "id": 2,
            "title": "How to get the most from resource centers",
            "snippet": "Tips for preparing before you go.",
            "body": "Visiting a resource center for the first time can feel overwhelming. Here are some practical tips to help you prepare and make the most of your visit:\n\n**Before You Go:**\n- Call ahead to confirm hours and requirements. Many centers have specific days or times for different services.\n- Bring identification if you have it. While not always required, having ID can help streamline the process.\n- Prepare a list of questions about services, eligibility, and what documentation might be needed.\n\n**What to Bring:**\n- Reusable bags for food pantries (many centers appreciate this eco-friendly approach)\n- A notebook to write down important information, contact numbers, and follow-up dates\n- Any relevant documents like proof of address, income statements, or family size (if required)\n\n**During Your Visit:**\n- Arrive early if possible, as some services operate on a first-come, first-served basis\n- Be patient and respectful with staff and volunteers who are there to help\n- Ask about additional services or programs that might be available\n- Inquire about future appointments or recurring services if you need ongoing support\n\n**After Your Visit:**\n- Follow up on any referrals or next steps that were discussed\n- Save contact information for future needs\n- Share your experience with others who might benefit from the same resources\n\nRemember, these centers exist to support you. Don't hesitate to ask questions or request clarification about any services offered."
        },
    ]
    return render_template("news.html", posts=posts)


@app.route("/news/<int:post_id>")
def article(post_id):
    # Reuse the same posts list as in /news
    # Find the post by id and render an article page
    posts = [
        {
            "id": 1,
            "title": "For All launches in Baltimore",
            "snippet": "Connecting neighbors to housing, food, and clothing.",
            "body": "For All is excited to announce its official launch in Baltimore, Maryland. Our mission is to connect community members with essential resources including housing assistance, food pantries, and clothing services.\n\nWe've partnered with over a dozen local organizations across the city, including Weinberg Housing & Resource Center, Bea Gaddy Family Center, Paul's Place, and many others. These trusted community partners provide critical support services to residents in need.\n\nWhether you're looking for emergency shelter, weekly groceries, or professional attire for job interviews, For All makes it easy to find the right resource in your neighborhood. Simply describe what you need, and we'll help you find the best match.\n\nOur platform is designed to be accessible and user-friendly, with a mobile-first approach that works on any device. We believe everyone deserves access to essential resources, and we're here to help make those connections happen."
        },
        {
            "id": 2,
            "title": "How to get the most from resource centers",
            "snippet": "Tips for preparing before you go.",
            "body": "Visiting a resource center for the first time can feel overwhelming. Here are some practical tips to help you prepare and make the most of your visit:\n\n**Before You Go:**\n- Call ahead to confirm hours and requirements. Many centers have specific days or times for different services.\n- Bring identification if you have it. While not always required, having ID can help streamline the process.\n- Prepare a list of questions about services, eligibility, and what documentation might be needed.\n\n**What to Bring:**\n- Reusable bags for food pantries (many centers appreciate this eco-friendly approach)\n- A notebook to write down important information, contact numbers, and follow-up dates\n- Any relevant documents like proof of address, income statements, or family size (if required)\n\n**During Your Visit:**\n- Arrive early if possible, as some services operate on a first-come, first-served basis\n- Be patient and respectful with staff and volunteers who are there to help\n- Ask about additional services or programs that might be available\n- Inquire about future appointments or recurring services if you need ongoing support\n\n**After Your Visit:**\n- Follow up on any referrals or next steps that were discussed\n- Save contact information for future needs\n- Share your experience with others who might benefit from the same resources\n\nRemember, these centers exist to support you. Don't hesitate to ask questions or request clarification about any services offered."
        },
    ]
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return redirect(url_for("news"))
    return render_template("article.html", post=post)


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


@app.route("/api/resources", methods=["GET"])
def api_resources():
    """
    GET /api/resources
    
    Query parameters:
    - category (optional): "housing" | "food" | "clothing"
    - city (optional, default: "Baltimore"): Filter by city (case-insensitive)
    
    Returns JSON array of resource dictionaries.
    """
    category = request.args.get("category", "").lower().strip()
    city = request.args.get("city", "Baltimore").strip()
    
    # Filter resources
    filtered = []
    for resource in SEED_RESOURCES:
        # Filter by category if provided
        if category and resource.category.lower() != category:
            continue
        # Filter by city (case-insensitive)
        if resource.city.lower() != city.lower():
            continue
        filtered.append(resource.to_dict())
    
    return jsonify(filtered)


if __name__ == "__main__":
    # For demo, enable debug so you see changes live
    # Run on all interfaces (0.0.0.0) so it's accessible on local network
    # Using port 5001 to avoid conflict with macOS AirPlay Receiver on port 5000
    app.run(host="0.0.0.0", port=5001, debug=True)
