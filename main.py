from flask import Flask, render_template, redirect, url_for, request
from flask.scaffold import setupmethod
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from sqlalchemy import asc
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///new-movies-collection.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy()
db.init_app(app)
Bootstrap(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, unique=True)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(500))
    img_url = db.Column(db.String(500), nullable=False)

class UpdateForm(FlaskForm):
    rating = StringField(name="Your Rating Out Of 10 eg. 7.3", validators=[DataRequired()])
    review = StringField(name="Your Review", validators=[DataRequired()])
    submit = SubmitField(name="done")

class AddForm(FlaskForm):
    title = StringField(name="movie title", validators=[DataRequired()])
    submit = SubmitField(name="add movie")

# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# with app.app_context():
#     db.create_all()
#     db.session.add(new_movie)
#     db.session.commit()
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    all_movies = Movie.query.order_by(asc(Movie.rating))
    all_movies = all_movies.all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", dat=all_movies)

@app.route("/edit?id=<num>", methods = ["GET","POST"])
def edit(num):
    form = UpdateForm()
    if request.method=="POST" and form.validate_on_submit():
        n = Movie.query.filter_by(id=num).first()
        n.rating = form.rating.data
        n.review = form.review.data
        db.session.commit()
        return redirect("/")
    return render_template("edit.html", form=form)

@app.route("/delete/<num>")
def delete(num):
    query_to_delete = Movie.query.filter_by(title=num).first()
    db.session.delete(query_to_delete)
    db.session.commit()
    return redirect("/")

@app.route("/add", methods=["POST","GET"])
def add():
    form = AddForm()
    if request.method == "POST" and form.validate_on_submit():
        movie = ((requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={your api key}&language=en-US&query={form.title.data}&page=1&include_adult=false")).json())["results"]
        return render_template("select.html", dat=movie)
    return render_template("add.html",form=form)

@app.route("/select/<num>")
def select(num):
    movie = requests.get(f"https://api.themoviedb.org/3/movie/{num}?api_key={your api key}&language=en-US").json()
    new_movie = Movie(
        title=movie["original_title"],
        year=((movie["release_date"]).split("-"))[0],
        description= movie["overview"],
        img_url="https://image.tmdb.org/t/p/w600_and_h900_bestv2"+movie["backdrop_path"]
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)
