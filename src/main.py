from flask import Flask
import database_operations as db_ops

app = Flask(__name__)


@app.route("/")
def hello_world():
    db = db_ops.get_database()
    movies = db.movies
    movie = movies.find_one()
    title = movie["title"]
    response = f"Hello, {title}!"
    return response
