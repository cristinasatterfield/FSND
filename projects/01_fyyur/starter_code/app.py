# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    jsonify,
    abort,
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.sql.functions as func
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime, timezone
import sys

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
artists_genres = db.Table(
    "artists_genres",
    db.Column(
        "artist_id",
        db.Integer,
        db.ForeignKey("artists.id", ondelete="cascade", primary_key=True),
        nullable=False,
    ),
    db.Column(
        "genre_id",
        db.Integer,
        db.ForeignKey("genres.id", ondelete="cascade", primary_key=True),
        nullable=False,
    ),
)

venues_genres = db.Table(
    "venues_genres",
    db.Column(
        "venue_id",
        db.Integer,
        db.ForeignKey("venues.id", ondelete="cascade", primary_key=True),
        nullable=False,
    ),
    db.Column(
        "genre_id",
        db.Integer,
        db.ForeignKey("genres.id", ondelete="cascade", primary_key=True),
        nullable=False,
    ),
)


class Show(db.Model):
    __tablename__ = "shows"
    artist_id = db.Column(
        db.Integer, db.ForeignKey("artists.id", ondelete="cascade"), primary_key=True
    )
    venue_id = db.Column(
        db.Integer, db.ForeignKey("venues.id", ondelete="cascade"), primary_key=True
    )
    start_time = db.Column(db.DateTime(timezone=True), nullable=False, primary_key=True)
    venues = db.relationship("Venue", backref=db.backref("show", lazy=True))


class Artist(db.Model):
    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(120), server_default="", nullable=False)
    facebook_link = db.Column(db.String(120), server_default="", nullable=False)
    seeking_venue = db.Column(
        db.Boolean, nullable=False, server_default="false", default=False
    )
    seeking_description = db.Column(db.String(500), nullable=False, server_default="")
    image_link = db.Column(
        db.String(500),
        nullable=False,
        server_default="https://www.pexels.com/photo/mic-microphone-recording-audio-14166/",
    )
    shows = db.relationship("Show", backref=db.backref("artist", lazy=True))
    genres = db.relationship(
        "Genre", secondary=artists_genres, backref=db.backref("artists", lazy=True)
    )


class Venue(db.Model):
    __tablename__ = "venues"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(120), server_default="", nullable=False)
    facebook_link = db.Column(db.String(120), server_default="", nullable=False)
    seeking_talent = db.Column(
        db.Boolean, nullable=False, server_default="false", default=False
    )
    seeking_description = db.Column(db.String(500), nullable=False, server_default="")
    image_link = db.Column(
        db.String(500),
        nullable=False,
        server_default="https://images.all-free-download.com/images/graphiclarge/scene_layout_04_hd_picture_167802.jpg",
    )
    genres = db.relationship(
        "Genre", secondary=venues_genres, backref=db.backref("venues", lazy=True)
    )


class Genre(db.Model):
    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters["datetime"] = format_datetime


# ----------------------------------------------------------------------------#
# Utils
# ----------------------------------------------------------------------------#


def build_genres_choices(genres):
    """
    Build genre id and name pair for form validation.

    We need this to dynamically load genre options from the database into the frontend.
    """
    genre_choices = []
    for genre in genres:
        choice = (genre.id, genre.name)
        genre_choices.append(choice)
    return genre_choices


def add_genres_to_venue(genre_ids, venue):
    """
    Loads genres by ID and associates them with a venue object.
    """
    for genre_id in genre_ids:
        genre = Genre.query.get(genre_id)
        venue.genres.append(genre)


def build_venue_from_form(venue_form, venue):
    venue.name = venue_form["name"]
    venue.city = venue_form["city"]
    venue.state = venue_form["state"]
    venue.address = venue_form["address"]
    venue.phone = venue_form["phone"]
    venue.website_link = venue_form["website_link"]
    venue.facebook_link = venue_form["facebook_link"]
    venue.seeking_talent = venue_form["seeking_talent"] == "True"
    venue.seeking_description = venue_form.get("seeking_description")
    venue.image_link = venue_form["image_link"]

    genre_ids = venue_form.getlist("genres")
    add_genres_to_venue(genre_ids, venue)
    return venue


def flash_form_errors(form, message):
    flash(message)
    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            flash(err)


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


# ----------------------------------------------------------------------------#
# Temp
# ----------------------------------------------------------------------------#


# ----------------------------------------------------------------------------#
# Venues.
# ----------------------------------------------------------------------------#


@app.route("/venues")
def venues():
    areas = (
        db.session.query(Venue.city, Venue.state)
        .group_by(Venue.city)
        .group_by(Venue.state)
        .all()
    )
    data = []
    for area in areas:
        venues = (
            db.session.query(Venue.id, Venue.name)
            .filter(Venue.city == area.city)
            .filter(Venue.state == area.state)
            .all()
        )
        venue_data = []
        for venue in venues:
            venue_data.append(
                {
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": db.session.query(Show.venue_id)
                    .filter(Show.venue_id == venue.id)
                    .filter(Show.start_time > datetime.today())
                    .count(),
                }
            )
        data.append(
            {"city": area.city, "state": area.state, "venues": venue_data,}
        )
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    search_term = request.form["search_term"]
    venues = db.session.query(Venue.id, Venue.name).filter(
        Venue.name.ilike(f"%{search_term}%")
    )

    venue_data = []
    for venue in venues:
        venue_data.append(
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": db.session.query(Show.venue_id)
                .filter(Show.venue_id == venue.id)
                .filter(Show.start_time > datetime.today())
                .count(),
            }
        )

    response = {
        "count": venues.count(),
        "data": venue_data,
    }
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        return render_template("errors/404.html"), 404
    else:
        venue_shows = (
            db.session.query(
                Show.artist_id, Artist.name, Artist.image_link, Show.start_time
            )
            .join(Artist)
            .filter(Show.venue_id == venue.id)
        )

        genre_list = []
        for genre in venue.genres:
            genre_list.append(
                db.session.query(Genre.name).filter(Genre.id == genre.id).first().name
            )

        upcoming_shows = []
        past_shows = []
        for show in venue_shows:
            if show.start_time > datetime.now(timezone.utc):
                upcoming_shows.append(
                    {
                        "artist_id": show.artist_id,
                        "artist_name": show.name,
                        "artist_image_link": show.image_link,
                        "start_time": show.start_time.strftime("%m/%d/%y, %H:%M"),
                    }
                )
            else:
                past_shows.append(
                    {
                        "artist_id": show.artist_id,
                        "artist_name": show.name,
                        "artist_image_link": show.image_link,
                        "start_time": show.start_time.strftime("%m/%d/%y, %H:%M"),
                    }
                )

        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": genre_list,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website_link,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": venue_shows.filter(
                Show.start_time <= datetime.today()
            ).count(),
            "upcoming_shows_count": venue_shows.filter(
                Show.start_time > datetime.today()
            ).count(),
        }
        return render_template("pages/show_venue.html", venue=data)


# ----------------------------------------------------------------------------#
#  Create Venue
# ----------------------------------------------------------------------------#


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    genres = Genre.query.order_by("name").all()
    genre_choices = build_genres_choices(genres)

    form = VenueForm()
    form.genres.choices = genre_choices
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    genres = Genre.query.order_by("name").all()
    genre_choices = build_genres_choices(genres)

    form = VenueForm()
    form.genres.choices = genre_choices

    if not form.validate_on_submit():
        flash_form_errors(form, "Failed to create venue.")
        return render_template("forms/new_venue.html", form=form)

    data = request.form
    try:
        new_venue = Venue()
        build_venue_from_form(data, new_venue)
        db.session.add(new_venue)
        db.session.commit()

        flash("Venue " + data["name"] + " was successfully listed!")
    except:
        db.session.rollback()
        print(sys.exc_info())

        flash("An error occurred. Venue " + data["name"] + " could not be listed.")
    finally:
        db.session.close()

    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


# ----------------------------------------------------------------------------#
#  Artists
# ----------------------------------------------------------------------------#


@app.route("/artists")
def artists():
    artists = db.session.query(Artist.id, Artist.name).all()
    data = []

    for artist in artists:
        data.append(
            {
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": db.session.query(Show.artist_id)
                .filter(Show.artist_id == artist.id)
                .filter(Show.start_time > datetime.today())
                .count(),
            }
        )
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    search_term = request.form["search_term"]
    artists = db.session.query(Artist.id, Artist.name).filter(
        Artist.name.ilike(f"%{search_term}%")
    )

    artist_data = []
    for artist in artists:
        artist_data.append(
            {
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": db.session.query(Show.artist_id)
                .filter(Show.artist_id == artist.id)
                .filter(Show.start_time > datetime.today())
                .count(),
            }
        )

    response = {
        "count": artists.count(),
        "data": artist_data,
    }
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        return render_template("errors/404.html"), 404
    else:
        artist_shows = (
            db.session.query(
                Show.venue_id, Venue.name, Venue.image_link, Show.start_time
            )
            .join(Venue)
            .filter(Show.artist_id == artist.id)
        )

        genre_list = []
        for genre in artist.genres:
            genre_list.append(
                db.session.query(Genre.name).filter(Genre.id == genre.id).first().name
            )

        upcoming_shows = []
        past_shows = []
        for show in artist_shows:
            if show.start_time > datetime.now(timezone.utc):
                upcoming_shows.append(
                    {
                        "venue_id": show.venue_id,
                        "venue_name": show.name,
                        "venue_image_link": show.image_link,
                        "start_time": show.start_time.strftime("%m/%d/%y, %H:%M"),
                    }
                )
            else:
                past_shows.append(
                    {
                        "venue_id": show.venue_id,
                        "venue_name": show.name,
                        "venue_image_link": show.image_link,
                        "start_time": show.start_time.strftime("%m/%d/%y, %H:%M"),
                    }
                )
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": genre_list,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_description,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": artist_shows.filter(
            Show.start_time <= datetime.today()
        ).count(),
        "upcoming_shows_count": artist_shows.filter(
            Show.start_time > datetime.today()
        ).count(),
    }
    return render_template("pages/show_artist.html", artist=data)


# ----------------------------------------------------------------------------#
#  Update
# ----------------------------------------------------------------------------#
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET", "POST"])
def edit_venue(venue_id):
    genres = Genre.query.order_by("name").all()
    genre_choices = []
    for genre in genres:
        choice = (genre.id, genre.name)
        genre_choices.append(choice)
    venue_query = db.session.query(Venue).filter(Venue.id == venue_id).first()
    if not venue_query:
        return render_template("errors/404.html"), 404
    else:
        genre_list = []
        for genre in venue_query.genres:
            genre_list.append(genre.id)

        venue = {
            "id": venue_query.id,
            "name": venue_query.name,
            "genres": genre_list,
            "address": venue_query.address,
            "city": venue_query.address,
            "state": venue_query.state,
            "phone": venue_query.phone,
            "website_link": venue_query.website_link,
            "facebook_link": venue_query.facebook_link,
            "seeking_talent": venue_query.seeking_talent,
            "seeking_description": venue_query.seeking_description,
            "image_link": venue_query.image_link,
        }
    form = VenueForm(data=venue)
    form.genres.choices = genre_choices

    if form.validate_on_submit():
        error = False
        data = request.form
        try:
            seeking_description = data.get("seeking_description")
            if seeking_description:
                venue_query.seeking_description = seeking_description

            venue_query.name = data["name"]
            venue_query.city = data["city"]
            venue_query.state = data["state"]
            venue_query.address = data["address"]
            venue_query.phone = data["phone"]
            venue_query.website_link = data["website_link"]
            venue_query.facebook_link = data["facebook_link"]
            venue_query.seeking_talent = data["seeking_talent"] == "True"
            venue_query.image_link = data["image_link"]
            venue_query.genres = []

            genres = data.getlist("genres")
            for genre_id in genres:
                genre = Genre.query.get(genre_id)
                venue_query.genres.append(genre)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            flash(
                "An error occurred. Venue '"
                + venue_query.name
                + "' could not be updated."
            )
        # on successful db update, flash success
        else:
            flash("Venue '" + data["name"] + "' was successfully updated!")
        return redirect(url_for("show_venue", venue_id=venue_id))
    elif request.method == "POST":
        flash("Failed to update venue.")
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(err)
    return render_template("forms/edit_venue.html", form=form, venue=venue)


# ----------------------------------------------------------------------------#
#  Create Artist
# ----------------------------------------------------------------------------#


@app.route("/artists/create", methods=["GET", "POST"])
def create_artist_submission():
    genres = Genre.query.order_by("name").all()
    genre_choices = []
    for genre in genres:
        choice = (genre.id, genre.name)
        genre_choices.append(choice)
    form = ArtistForm()
    form.genres.choices = genre_choices
    if form.validate_on_submit():
        error = False
        data = request.form
        try:
            name = data["name"]
            city = data["city"]
            state = data["state"]
            phone = data["phone"]
            genres = data.getlist("genres")
            website_link = data["website_link"]
            facebook_link = data["facebook_link"]
            seeking_venue = data["seeking_venue"] == "True"
            seeking_description = data.get("seeking_description")
            image_link = data["image_link"]
            new_artist = Artist(
                name=name,
                city=city,
                state=state,
                phone=phone,
                website_link=website_link,
                facebook_link=facebook_link,
                seeking_venue=seeking_venue,
                seeking_description=seeking_description,
                image_link=image_link,
            )
            for genre_id in genres:
                genre = Genre.query.get(genre_id)
                new_artist.genres.append(genre)
            db.session.add(new_artist)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            flash(
                "An error has occured. Artist " + data["name"] + " could not be listed."
            )
        # on successful db insert, flash success
        else:
            flash("Artist " + data["name"] + " was successfully listed!")
        return render_template("pages/home.html")
    elif request.method == "POST":
        flash("Failed to create artist.")
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(err)
    return render_template("forms/new_artist.html", form=form)

    # TODO: modify data to be the data object returned from db insertion


# ----------------------------------------------------------------------------#
#  Shows
# ----------------------------------------------------------------------------#


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    shows = (
        db.session.query(
            Show.venue_id,
            Venue.name.label("venue_name"),
            Show.artist_id,
            Artist.name.label("artist_name"),
            Artist.image_link,
            Show.start_time,
        )
        .join(Venue)
        .join(Artist)
        .filter(Show.start_time > datetime.today())
        .all()
    )
    data = []
    for show in shows:
        data.append(
            {
                "venue_id": show.venue_id,
                "venue_name": show.venue_name,
                "artist_id": show.artist_id,
                "artist_name": show.artist_name,
                "artist_image_link": show.image_link,
                "start_time": show.start_time.strftime("%m/%d/%y, %H:%M"),
            }
        )
    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create", methods=["GET", "POST"])
def create_show_submission():
    artists = Artist.query.order_by("name").all()
    artist_choices = []
    for artist in artists:
        choice = (artist.id, artist.name)
        artist_choices.append(choice)
    venues = Venue.query.order_by("name").all()
    venue_choices = []
    for venue in venues:
        choice = (venue.id, venue.name)
        venue_choices.append(choice)
    form = ShowForm()
    form.artist.choices = artist_choices
    form.venue.choices = venue_choices
    if form.validate_on_submit():
        error = False
        data = request.form
        try:
            artist_id = data["artist"]
            venue_id = data["venue"]
            start_time = datetime.strptime(data["start_time"], "%Y-%m-%d %H:%M:%S")
            new_show = Show(
                artist_id=artist_id, venue_id=venue_id, start_time=start_time
            )
            db.session.add(new_show)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            flash("An error has occured. Show could not be listed.")
        else:
            # on successful db insert, flash success
            flash("Show was successfully listed!")
        return render_template("pages/home.html")
    elif request.method == "POST":
        flash("Failed to create show.")
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(err)
    return render_template("forms/new_show.html", form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
