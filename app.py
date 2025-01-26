# For API
from dotenv import load_dotenv
import requests
import os
# For Flask app
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
# For password hashing
from werkzeug.security import check_password_hash, generate_password_hash
# For helpers functions
from helpers import login_required
# For database
from flask_sqlalchemy import SQLAlchemy
# For converting dict to JSON
from json import dumps, loads
from ast import literal_eval

# Configure application
app = Flask(__name__)

# Load api key from environment
load_dotenv()
api_key = os.getenv("API_KEY")

# Load secret key from environment
app.secret_key = os.getenv("SECRET_KEY")

# Configure API
host = "https://v1.formula-1.api-sports.io"
headers = {
    "x-rapidapi-host": host,
    "x-rapidapi-key": api_key
}

# Configure session
app.config["SESSION_PERMANENT"] = False     # Session will be cleared when browser is closed
app.config["SESSION_TYPE"] = "filesystem"   # Session will be stored on server's filesystem instead of cookies
Session(app)                                # Initialize session

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Id, integer not null, primary key
    username = db.Column(db.String(100), unique=True, nullable=False)  # Username, varchar(100) not null (unique)
    hash = db.Column(db.String(255), nullable=False)  # Hash, varchar(255) not null

    def __repr__(self):
        return f"<User {self.username}>"
    
class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Id, integer not null, primary key
    type = db.Column(db.String(100), nullable=False)  # Type, string, not null
    data = db.Column(db.JSON, nullable=False)  # Data, JSON, not null
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User Id, integer, foreign key

    user = db.relationship("User", backref=db.backref("favorites", lazy=True))  # Relationship with Users table

    def __repr__(self):
        return f"<Favorite {self.id}, Type: {self.type}>"

# Initialize database before first request
with app.app_context():
    db.create_all()

# Ensure responses aren't cached (Called after each HTTP response)
@app.after_request
def after_request(response):
    """Modifies HTTP response headers to ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/add-favorite", methods=["POST"])
@login_required
def add_favorite():
    """Add an element to favorites"""

    print("Favorite added!")

    # Data needed to add a favorite
    selected = request.form.get("selected")
    data_type = request.form.get("type")

    # Data needed to rerender the page
    season = request.form.get("season")
    results = request.form.get("results")
    data = request.form.get("data")

    # Check if selected is in the favorites database
    rows = [row[0] for row in Favorite.query.filter_by(type=data_type, user_id=session["user_id"]).with_entities(Favorite.data).all()]
    selected_checked = False
    for row in rows:
        if literal_eval(loads(row))["id"] == literal_eval(selected)["id"]:
            selected_checked = True
            break

    # Check if favorite is already in the database
    if selected_checked:
        # Remove from favorites
        pass
    else:
        # Add to favorites
        new_favorite = Favorite(type=data_type, data=dumps(selected), user_id=session["user_id"])
        db.session.add(new_favorite)
        db.session.commit()

    if data_type == "race":
        return render_template("races.html", results=int(results), data=literal_eval(data), season=int(season), selected=literal_eval(selected), selected_checked=not selected_checked)
    elif data_type == "team":
        return render_template("teams.html", results=int(results), data=literal_eval(data), selected=literal_eval(selected), selected_checked=not selected_checked)

@app.route("/change-theme", methods=["POST"])
@login_required
def change_theme():
    """Handle the toggle switch mode change"""
    data = request.get_json()
    mode = data.get("mode")
    session["theme"] = mode
    return jsonify({"Result": "Success", "mode": mode})

@app.route("/")
@login_required
def index():
    return render_template("index.html", theme=session.get("theme", "light"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

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
        rows = User.query.filter_by(username=request.form.get("username")).all()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0].hash ,request.form.get("password")):
            flash("Invalid username and/or password")
            return redirect("/login")
            
        # Clear session before logging in and remember which user has logged in
        session.clear()
        session["user_id"] = rows[0].id
        return redirect("/")

    # User clicked a link or was redirected
    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # check if username is provided
        if not request.form.get("username"):
            flash("Must provide username")
            return redirect("/register")

        # check if password is provided
        elif not request.form.get("password"):
            flash("Must provide password")
            return redirect("/register")

        # check if confirmation match password
        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords don't match")
            return redirect("/register")

        # Check if username already exist
        rows = User.query.filter_by(username=request.form.get("username")).all()
        if len(rows) != 0:
            flash("Username already exists")
            return redirect("/register")

        # Insert new user into database
        username = request.form.get('username')
        hash = generate_password_hash(request.form.get('password'))
        new_user = User(username=username, hash=hash)
        db.session.add(new_user)
        db.session.commit()

        # Remember which user is currently logged in
        user_id = User.query.filter_by(username=username).with_entities(User.id).first()
        session["user_id"] = user_id[0]

        # redirect user to home page
        return redirect("/")

    # user reached route via GET (by clicking a link or via redirect)
    else:
        return render_template("register.html")

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
                "logo_link": result.get("logo", ""),
                "base": result.get("base", "Unknown"),
                "entry_year": result.get("first_team_entry", "Unknown"),
                "championships": result.get("world_championships", 0),
                "pole_positions": result.get("pole_positions", "Unknown"),
                "fastest_laps": result.get("fastest_laps", "Unknown"),
                "president": result.get("president", "Unknown"),
                "director": result.get("director", "Unknown"),
                "technical_manager": result.get("technical_manager", "Unknown"),
                "chassis": result.get("chassis", "Unknown"),
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

        # Check if selected is in the favorites database
        rows = [row[0] for row in Favorite.query.filter_by(type="team", user_id=session["user_id"]).with_entities(Favorite.data).all()]
        selected_checked = False
        for row in rows:
            if literal_eval(loads(row))["id"] == selected_id:
                selected_checked = True
                break
        return render_template("teams.html", results=results, data=data, selected=selected, selected_checked=selected_checked)
    else:
        return render_template("teams.html", results=results)

@app.route("/races", methods=["GET", "POST"])
@login_required
def races():
    """Show seasons and races"""

    # After selecting the season
    if request.args.get("season"):
        season = request.args.get("season")

        response = requests.get(host+"/races", headers=headers, params={"season": season}).json()

        results = response["results"]
        data=[]
        for result in response["response"]:
            data.append(
                {
                    "id": result["id"],
                    "circuit_name": result["circuit"]["name"],
                    "circuit_image_link": result["circuit"]["image"],
                    "date": f"{result['date'][11:16]}, {result['date'][:10]}",
                    "weather": result.get("weather", "Unknown"),
                    "status": result["status"],
                    "distance": result["distance"],
                    "best_time": result["fastest_lap"]["time"],
                    "laps_count": result["laps"]["total"],
                    "location": f"{result['competition']['name']}, {result['competition']['location']['city']}, {result['competition']['location']['country']}",
                }
            )

        if results:
            selected_id = int(request.form.get("selected_id", data[0]["id"]))
            for race in data:
                if race["id"] == selected_id:
                    selected = race
                    break

            # Check if selected is in the favorites database
            rows = [literal_eval(loads(row[0])) for row in Favorite.query.filter_by(type="race", user_id=session["user_id"]).with_entities(Favorite.data).all()]
            print(rows)
            selected_checked = False
            for row in rows:
                if row["id"] == selected_id:
                    selected_checked = True
                    break

            return render_template("races.html", results=results, data=data, season=season, selected=selected, selected_checked=selected_checked)
        else:
            return "Brak wyników"


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

# Runs the app in development mode only if the script was called directly
if __name__ == "__main__":
    app.run(debug=True)