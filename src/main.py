from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, session
import bcrypt
import database_operations as db_ops

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"


@app.route("/")
def index():
    if session:
        if datetime.now() - datetime.strptime(session["timestamp"], "%y-%m-%d %H:%M:%S") > timedelta(minutes=5):
            session.clear()
            return render_template("index.html")
        elif session["login"]:
            return redirect(url_for("home"))
    return render_template("index.html")


@ app.route("/home")
def home():
    return render_template("home.html")


@ app.route("/login", methods=["POST"])
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
        session["timestamp"] = datetime.now().strftime("%y-%m-%d %H:%M:%S")
        return redirect(url_for("home"))
    else:
        return "Invalid credentials. <a href='/index'>try again</a>"


@ app.route("/register", methods=["POST"])
def register():
    if request.method == "POST":
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
    else:
        return redirect(url_for("/"))
