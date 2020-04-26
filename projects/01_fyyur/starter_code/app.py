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
# App Configuration
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models
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
# Filters
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
# Helper Functions
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


def add_genres_to_model(genre_ids, model):
    """
    Loads genres by ID and associates them with a model.
    """
    for genre_id in genre_ids:
        genre = Genre.query.get(genre_id)
        model.genres.append(genre)


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
    add_genres_to_model(genre_ids, venue)
    return venue


def build_artist_from_form(artist_form, artist):
    artist.name = artist_form["name"]
    artist.city = artist_form["city"]
    artist.state = artist_form["state"]
    artist.phone = artist_form["phone"]
    artist.website_link = artist_form["website_link"]
    artist.facebook_link = artist_form["facebook_link"]
    artist.seeking_venue = artist_form["seeking_venue"] == "True"
    artist.seeking_description = artist_form.get("seeking_description")
    artist.image_link = artist_form["image_link"]

    genre_ids = artist_form.getlist("genres")
    add_genres_to_model(genre_ids, artist)
    return artist


def flash_form_errors(form, message):
    flash(message)
    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            flash(err)


# ----------------------------------------------------------------------------#
# Venue Repository
# ----------------------------------------------------------------------------#


def get_areas_by_city_state():
    return (
        db.session.query(Venue.city, Venue.state)
        .group_by(Venue.city)
        .group_by(Venue.state)
        .order_by(Venue.city)
        .all()
    )


def get_venues_in_area(area):
    return (
        db.session.query(Venue.id, Venue.name)
        .filter(Venue.city == area.city)
        .filter(Venue.state == area.state)
        .all()
    )


def get_num_upcoming_shows_by_venue(venue):
    return (
        db.session.query(Show.venue_id)
        .filter(Show.venue_id == venue.id)
        .filter(Show.start_time > datetime.today())
        .count()
    )


def get_shows_at_venue(venue):
    return (
        db.session.query(
            Show.artist_id, Artist.name, Artist.image_link, Show.start_time
        )
        .join(Artist)
        .filter(Show.venue_id == venue.id)
    )


def build_venue_data_short(venues):
    venue_data = []
    for venue in venues:
        venue_data.append(
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": get_num_upcoming_shows_by_venue(venue),
            }
        )
    return venue_data


# ----------------------------------------------------------------------------#
# Artist Repository
# ----------------------------------------------------------------------------#


def get_num_upcoming_shows_by_artist(artist):
    return (
        db.session.query(Show.artist_id)
        .filter(Show.artist_id == artist.id)
        .filter(Show.start_time > datetime.today())
        .count()
    )


def get_shows_by_artist(artist):
    return (
        db.session.query(Show.venue_id, Venue.name, Venue.image_link, Show.start_time)
        .join(Venue)
        .filter(Show.artist_id == artist.id)
    )


def build_artist_data_short(artists):
    artist_data = []
    for artist in artists:
        artist_data.append(
            {
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": get_num_upcoming_shows_by_artist(artist),
            }
        )
    return artist_data


# ----------------------------------------------------------------------------#
# Controllers
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


# ----------------------------------------------------------------------------#
# Temp
# ----------------------------------------------------------------------------#


# ----------------------------------------------------------------------------#
#  Create Venues
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


# ----------------------------------------------------------------------------#
# Display Venues
# ----------------------------------------------------------------------------#


@app.route("/venues", methods=["GET"])
def venues():
    areas = get_areas_by_city_state()
    data = []
    for area in areas:
        venues = get_venues_in_area(area)
        venue_data = build_venue_data_short(venues)
        data.append(
            {"city": area.city, "state": area.state, "venues": venue_data,}
        )
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/<int:venue_id>", methods=["GET"])
def show_venue(venue_id):
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        return render_template("errors/404.html"), 404

    venue_shows = get_shows_at_venue(venue)

    genre_list = []
    for genre in venue.genres:
        genre_list.append(genre.name)

    upcoming_shows = []
    past_shows = []
    for show in venue_shows:
        show_details = {
            "artist_id": show.artist_id,
            "artist_name": show.name,
            "artist_image_link": show.image_link,
            "start_time": show.start_time.strftime("%m/%d/%y, %H:%M"),
        }
        if show.start_time > datetime.now(timezone.utc):
            upcoming_shows.append(show_details)
        else:
            past_shows.append(show_details)

    past_shows_count = venue_shows.filter(Show.start_time <= datetime.today()).count()
    upcoming_shows_count = venue_shows.filter(
        Show.start_time > datetime.today()
    ).count()
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
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
    }
    return render_template("pages/show_venue.html", venue=data)


# ----------------------------------------------------------------------------#
# Search Venues
# ----------------------------------------------------------------------------#


@app.route("/venues/search", methods=["POST"])
def search_venues():
    search_term = request.form["search_term"]
    venues = db.session.query(Venue.id, Venue.name).filter(
        Venue.name.ilike(f"%{search_term}%")
    )

    response = {
        "count": venues.count(),
        "data": build_venue_data_short(venues),
    }
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


# ----------------------------------------------------------------------------#
# Update Venues
# ----------------------------------------------------------------------------#
@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue_form(venue_id):
    venue_query = db.session.query(Venue).filter(Venue.id == venue_id).first()

    if not venue_query:
        return render_template("errors/404.html"), 404

    genre_list = []
    for genre in venue_query.genres:
        genre_list.append(genre.id)

    venue_data = {
        "id": venue_query.id,
        "name": venue_query.name,
        "genres": genre_list,
        "address": venue_query.address,
        "city": venue_query.city,
        "state": venue_query.state,
        "phone": venue_query.phone,
        "website_link": venue_query.website_link,
        "facebook_link": venue_query.facebook_link,
        "seeking_talent": venue_query.seeking_talent,
        "seeking_description": venue_query.seeking_description,
        "image_link": venue_query.image_link,
    }

    form = VenueForm(data=venue_data)

    genres = Genre.query.order_by("name").all()
    form.genres.choices = build_genres_choices(genres)

    return render_template("forms/edit_venue.html", form=form, venue=venue_data)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    genres = Genre.query.order_by("name").all()
    genre_choices = build_genres_choices(genres)

    form = VenueForm()
    form.genres.choices = genre_choices

    venue_query = db.session.query(Venue).filter(Venue.id == venue_id).first()

    if not form.validate_on_submit():
        flash_form_errors(form, "Failed to update venue.")
        return render_template("forms/edit_venue.html", form=form, venue=venue_query)

    data = request.form
    try:
        # Only update db if description exists.
        # No description, returns NULL, violating the constraint on the Venue model.
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

        # On edit, genre associations in db are overwritten.
        # This could cause problems if mult. people edit the same venue at the same time
        venue_query.genres = []
        genres = data.getlist("genres")
        add_genres_to_model(genres, venue_query)

        db.session.commit()

        flash("Venue '" + data["name"] + "' was successfully updated!")
    except:
        db.session.rollback()
        print(sys.exc_info())

        flash(f"An error occurred. Venue '{venue_query.name}' could not be updated.")
    finally:
        db.session.close()

    return redirect(url_for("show_venue", venue_id=venue_id))


# ----------------------------------------------------------------------------#
# Delete Venues
# ----------------------------------------------------------------------------#


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


# ----------------------------------------------------------------------------#
#  Create Artists
# ----------------------------------------------------------------------------#


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    genres = Genre.query.order_by("name").all()
    genre_choices = build_genres_choices(genres)

    form = ArtistForm()
    form.genres.choices = genre_choices
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    genres = Genre.query.order_by("name").all()
    genre_choices = build_genres_choices(genres)

    form = ArtistForm()
    form.genres.choices = genre_choices

    if not form.validate_on_submit():
        flash_form_errors(form, "Failed to create artist.")
        return render_template("forms/new_artist.html", form=form)

    data = request.form
    try:
        new_artist = Artist()
        build_artist_from_form(data, new_artist)
        db.session.add(new_artist)
        db.session.commit()

        flash("Artist " + data["name"] + " was successfully listed!")
    except:
        db.session.rollback()
        print(sys.exc_info())

        flash("An error has occured. Artist " + data["name"] + " could not be listed.")
    finally:
        db.session.close()

    return render_template("pages/home.html")


# ----------------------------------------------------------------------------#
# Display Artists
# ----------------------------------------------------------------------------#


@app.route("/artists")
def artists():
    artists = db.session.query(Artist.id, Artist.name).all()
    artist_data = build_artist_data_short(artists)
    return render_template("pages/artists.html", artists=artist_data)


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        return render_template("errors/404.html"), 404

    artist_shows = get_shows_by_artist(artist)

    genre_list = []
    for genre in artist.genres:
        genre_list.append(genre.name)

    upcoming_shows = []
    past_shows = []
    for show in artist_shows:
        show_details = {
            "venue_id": show.venue_id,
            "venue_name": show.name,
            "venue_image_link": show.image_link,
            "start_time": show.start_time.strftime("%m/%d/%y, %H:%M"),
        }
        if show.start_time > datetime.now(timezone.utc):
            upcoming_shows.append(show_details)
        else:
            past_shows.append(show_details)

    past_shows_count = artist_shows.filter(Show.start_time <= datetime.today()).count()
    upcoming_shows_count = artist_shows.filter(
        Show.start_time > datetime.today()
    ).count()
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
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
    }
    return render_template("pages/show_artist.html", artist=data)


# ----------------------------------------------------------------------------#
# Search Artists
# ----------------------------------------------------------------------------#


@app.route("/artists/search", methods=["POST"])
def search_artists():
    search_term = request.form["search_term"]
    artists = db.session.query(Artist.id, Artist.name).filter(
        Artist.name.ilike(f"%{search_term}%")
    )

    response = {
        "count": artists.count(),
        "data": build_artist_data_short(artists),
    }

    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


# ----------------------------------------------------------------------------#
#  Update Arists
# ----------------------------------------------------------------------------#


@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist_form(artist_id):
    artist_query = db.session.query(Artist).filter(Artist.id == artist_id).first()

    if not artist_query:
        return render_template("errors/404.html"), 404

    genre_list = []
    for genre in artist_query.genres:
        genre_list.append(genre.id)

    artist_data = {
        "id": artist_query.id,
        "name": artist_query.name,
        "genres": genre_list,
        "city": artist_query.city,
        "state": artist_query.state,
        "phone": artist_query.phone,
        "website_link": artist_query.website_link,
        "facebook_link": artist_query.facebook_link,
        "seeking_venue": artist_query.seeking_venue,
        "seeking_description": artist_query.seeking_description,
        "image_link": artist_query.image_link,
    }

    form = ArtistForm(data=artist_data)

    genres = Genre.query.order_by("name").all()
    form.genres.choices = build_genres_choices(genres)

    return render_template("forms/edit_artist.html", form=form, artist=artist_data)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    genres = Genre.query.order_by("name").all()
    genre_choices = build_genres_choices(genres)

    form = ArtistForm()
    form.genres.choices = genre_choices

    artist_query = db.session.query(Artist).filter(Artist.id == artist_id).first()

    if not form.validate_on_submit():
        flash_form_errors(form, "Failed to update Artist")
        return render_template("forms/edit_artist.html", form=form, artist=artist_query)

    data = request.form
    try:
        # Only update db if description exists.
        # No description, returns NULL, violating the constraint on the Venue model.
        seeking_description = data.get("seeking_description")
        if seeking_description:
            artist_query.seeking_description = seeking_description

        artist_query.name = data["name"]
        artist_query.city = data["city"]
        artist_query.state = data["state"]
        artist_query.phone = data["phone"]
        artist_query.website_link = data["website_link"]
        artist_query.facebook_link = data["facebook_link"]
        artist_query.seeking_venue = data["seeking_venue"] == "True"
        artist_query.image_link = data["image_link"]

        # On edit, genre associations in db are overwritten.
        # This could cause problems if mult. people edit the same venue at the same time
        artist_query.genres = []
        genres = data.getlist("genres")
        add_genres_to_model(genres, artist_query)

        db.session.commit()

        flash(f"Artist '{data['name']}' was successfully updated!")
    except:
        db.session.rollback()
        print(sys.exc_info())

        flash(f"An error occurred. Artist '{artist_query.name}' could not be updated.")
    finally:
        db.session.close()

    return redirect(url_for("show_artist", artist_id=artist_id))


# ----------------------------------------------------------------------------#
# Delete Artists
# ----------------------------------------------------------------------------#


@app.route("/artists/<artist_id>", methods=["DELETE"])
def delete_artist(artist_id):
    # TODO: Complete this endpoint for taking an artist_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete an Artist on an Artist Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


# ----------------------------------------------------------------------------#
#  Create Shows
# ----------------------------------------------------------------------------#


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


# ----------------------------------------------------------------------------#
#  Display Shows
# ----------------------------------------------------------------------------#


@app.route("/shows")
def shows():
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


# ----------------------------------------------------------------------------#
#  Error Handlers
# ----------------------------------------------------------------------------#


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
# Launch
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
