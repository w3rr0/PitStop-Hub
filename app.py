# For API
from dotenv import load_dotenv
import requests
import os
# For Flask app
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
# For password hashing
from werkzeug.security import check_password_hash, generate_password_hash
# For helpers functions
from helpers import login_required

# Load api key from environment
load_dotenv()
api_key = os.getenv("API_KEY")

# Configure API
host = "https://v1.formula-1.api-sports.io"
headers = {
    "x-rapidapi-host": host,
    "x-rapidapi-key": api_key
}

# Configure application
app = Flask(__name__)

# Load secret key from environment
app.secret_key = os.getenv("SECRET_KEY")

# Configure session
app.config["SESSION_PERMANENT"] = False     # Session will be cleared when browser is closed
app.config["SESSION_TYPE"] = "filesystem"   # Session will be stored on server's filesystem instead of cookies
Session(app)                                # Initialize session


# Ensure responses aren't cached (Called after each HTTP response)
@app.after_request
def after_request(response):
    """Modifies HTTP response headers to ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    # session.clear()

    # User submitted a form
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("No username provided")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("No password provided")
            return redirect("/login")

        # Query database for username
        # rows = db.execute(
        #     "SELECT * FROM users WHERE username = ?", request.form.get("username")
        # )
        rows = []
        with open('users.csv', mode='r') as file:
            for line in file:
                username, hash_pas = line.strip().split(', ')
            rows.append({'id': 1, 'username': username, 'hash': hash_pas})

        # Ensure username exists and password is correct
        # if len(rows) != 1 or not check_password_hash(
        #     rows[0]["hash"], request.form.get("password")
        # ):
        #     return apology("invalid username and/or password", 403)
        if len(rows) != 1 or hash_pas != request.form.get("password"):
            flash("Invalid username and/or password")
            return redirect("/login")
            
        # Clear session before logging in and remember which user has logged in
        session.clear()
        session["user_id"] = rows[0]["id"]
        return redirect("/")

    # User clicked a link or was redirected
    else:
        # flash("Test message") - jedyna wiadomość która się wyświetla na stronie
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/competitions")
@login_required
def competitions():
    """Show competitions"""

    response = requests.get(host+"/competitions", headers=headers).json()

    results = response["results"]

    data = []
    for result in response["response"]:
        data.append(
            {
                "id": result["id"],
                "name": result["name"],
                "city": result["location"]["city"],
                "country": result["location"]["country"]
            }
        )

    return render_template("competitions.html", results=results, data=data)


@app.route("/teams", methods=["GET", "POST"])
@login_required
def teams():
    """Show teams"""

    response = requests.get(host+"/teams", headers=headers).json()

    results = response["results"]

    data = []
    for result in response["response"]:
        data.append(
            {
                "id": result["id"],
                "name": result["name"],
                "logo-link": result.get("logo", ""),
                "base": result.get("base", "Unknown"),
                "entry-year": result.get("first_team_entry", "Unknown"),
                "championships": result.get("world_championships", 0),
                "pole_positions": result.get("pole_positions", "Unknown"),
                "fastest_laps": result.get("fastest_laps", "Unknown"),
                "president": result.get("president", "Unknown"),
                "director": result.get("director", "Unknown"),
                "technical_manager": result.get("technical_manager", "Unknown"),
                'chassis': result.get("chassis", "Unknown"),
                "engine": result.get("engine", "Unknown"),
                "tyres": result.get("tyres", "Unknown"),
            }
        )

    if results:
        selected_id = int(request.form.get("selected_id", data[0]["id"]))
        for team in data:
            if team["id"] == selected_id:
                selected = team
                break
    else:
        selected = None

    return render_template("teams.html", results=results, data=data, selected=selected)

@app.route("/races")
@login_required
def races():
    """Show seasons and races"""

    # After selecting the season
    if request.args.get("season"):
        season= request.args.get("season")

        response = requests.get(host+"/races", headers=headers, params={"season": season}).json()

        results = response["results"]
        data=[]
        for result in response["response"]:
            data.append(
                {
                    "id": result["id"],
                    "circuit_name": result["circuit"]["name"],
                    "circuit_image_link": result["circuit"]["image"],
                    "date": f"{result["date"][11:16]}, {result["date"][:10]}",
                    "weather": result.get("weather", "Unknown"),
                    "status": result["status"],
                    "distance": result["distance"],
                    "best_time": result["fastest_lap"]["time"],
                    "laps_count": result["laps"]["total"],
                    "location": f"{result["competition"]["name"]}, {result["competition"]["location"]["city"]}, {result['competition']['location']['country']}",
                }
            )
        
        return render_template("races.html", results=results, data=data, season=season)

    # Before choosing a season
    else:

        response = requests.get(host+"/seasons", headers=headers).json()

        results = response["results"]
        seasons = response["response"]

        return render_template("races.html", results=results, seasons=seasons)
    

@app.route("/favorites")
@login_required
def favorites():
    """Show all elements marked as favorite"""

    # Make database for users favorites

    return render_template("favorites.html")