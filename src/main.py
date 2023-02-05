from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, session
import bcrypt
import database_operations as db_ops

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=1)


@app.before_request
def update_session():
    session.modified = True


@app.route("/")
def index():
    if session:
        if session["login"]:
            return redirect(url_for("home"))
    return render_template("index.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/movies")
def movies():
    if session:
        if session["login"]:
            action_movies = db_ops.get_many_documents(
                "movies", {"genres": "Action",
                           "poster": {"$exists": "true"}}, 15
            )

            fantasy_movies = db_ops.get_many_documents(
                "movies", {"genres": "Fantasy",
                           "poster": {"$exists": "true"}}, 15
            )
            horror_movies = db_ops.get_many_documents(
                "movies", {"genres": "Horror",
                           "poster": {"$exists": "true"}}, 15
            )

            return render_template("movies.html", action_movies=action_movies, fantasy_movies=fantasy_movies, horror_movies=horror_movies)
    else:
        return redirect(url_for("index"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/login", methods=["POST"])
def login():

    email = request.form.get("email")
    password = request.form.get("password")

    user = db_ops.get_document("users", {"email": email})

    auth = bcrypt.checkpw(password.encode("utf-8"),
                          user["password"].encode("utf-8"))

    if auth:
        session["user"] = user["name"]
        session["email"] = user["email"]
        session["login"] = True
        session.permanent = True
        return redirect(url_for("home"))
    else:
        return "Invalid credentials. <a href='/'>try again</a>"


@app.route("/register", methods=["POST"])
def register():
    users = db_ops.get_collection("users")
    password = request.form.get("password")
    hash_password = bcrypt.hashpw(
        password.encode('utf-8'), bcrypt.gensalt())
    users.insert_one({
        "name": request.form.get("name"),
        "email": request.form.get("email"),
        "password": str(hash_password).removeprefix("b'").removesuffix("'")
    })
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
