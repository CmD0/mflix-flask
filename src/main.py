from datetime import timedelta
import re
from flask import Flask, render_template, redirect, url_for, request, session
import bcrypt
import database_operations as db_ops
from bson import objectid

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=1)


@app.before_request
def update_session():
    session.modified = True


@app.route("/")
def index(error=None):
    if session:
        if session.get('login'):
            return redirect(url_for("home"))
        if session.get('error'):
            return render_template("index.html", error=session.get('error'))
    return render_template("index.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/movies")
def movies():
    if session:
        if session["login"]:
            if session.get("query"):
                query = session.get("query")
                session.pop("query")
                query = re.sub("[\[\]{}\"']+", "", query)
                query_movies = db_ops.get_many_documents(
                    "movies", {
                        "title": {"$regex": ".*"+query+".*"},
                        "poster": {"$exists": "true"}
                    }
                ).sort("year", -1)
                return render_template("movies.html",
                                       query_movies=query_movies,
                                       search=True,
                                       query=query)

            action_movies = db_ops.get_many_documents(
                "movies", {"genres": "Action",
                           "poster": {"$exists": "true"},
                           "year": {"$gt": 2010}}, 15
            )

            fantasy_movies = db_ops.get_many_documents(
                "movies", {"genres": "Fantasy",
                           "poster": {"$exists": "true"},
                           "year": {"$gt": 2010}}, 15
            )
            horror_movies = db_ops.get_many_documents(
                "movies", {"genres": "Horror",
                           "poster": {"$exists": "true"},
                           "year": {"$gt": 2010}}, 15
            )

            return render_template("movies.html",
                                   action_movies=action_movies,
                                   fantasy_movies=fantasy_movies,
                                   horror_movies=horror_movies)
    return redirect(url_for("index"))


@app.route("/movie")
def movie():
    if session:
        if session["login"]:
            movie_id = request.args.get("id")
            movie = db_ops.get_document(
                "movies", {"_id": objectid.ObjectId(movie_id)}
            )
            return render_template("movie.html", movie=movie)
    return redirect(url_for("index"))


@app.route("/search", methods=["POST"])
def search():
    if session:
        if session["login"]:
            query = request.form.get("query")
            session["query"] = query
            return redirect(url_for("movies"))
    return redirect(url_for("index"))


@ app.route("/about")
def about():
    return render_template("about.html")


@ app.route("/login", methods=["POST"])
def login():

    email = request.form.get("email")
    password = request.form.get("password")

    user = db_ops.get_document("users", {"email": email})

    auth = bcrypt.checkpw(password.encode("utf-8"),
                          user["password"].encode("utf-8"))

    if auth:
        session.clear()
        session["user"] = user["name"]
        session["email"] = user["email"]
        session["login"] = True
        session.permanent = True
        return redirect(url_for("home"))
    else:
        session['error'] = "Invalid credentials, try again."
        return redirect(url_for("index"))


@ app.route("/register", methods=["POST"])
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


@ app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
