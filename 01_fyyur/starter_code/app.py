#----------------------------------------------------------------------------#
# Imports all the nessasary libraryes.
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
# Will import all the models.
from models import *

#----------------------------------------------------------------------------#
# App Configration.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

# to return the home page using '/'.


@app.route('/')
def index():
    return render_template('pages/home.html')


# Venues Controllers.
#  ----------------------------------------------------------------
# Will return all the venues.

@app.route('/venues')
def venues():
    # Assignments.
    data = []
    information = []
# Return all the venues depending on city and state.
    outcome = db.session.query(Venue).with_entities(
        Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
# The first for will return venues depending on the city.
    for out in outcome:
        city = Venue.query.filter_by(city=out.city).all()
# The second for will return id, name, and num_upcoming_shows for the venues and append it to the information.
        for venue in city:
            information.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all())
            })
# Will append city, state, and venue results in the data.
        data.append({
            "city": out.city,
            "state": out.state,
            "venues": information
        })

    return render_template('pages/venues.html', areas=data)

# Will search in the venues.


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # Assignments.
    data = []
# Return what the user typed using get.
    search_term = request.form.get('search_term', '')
# Will return venues names and it is case-insensitive using .ilike(f'%{search_term}%').
    outcome = db.session.query(Venue).filter(
        Venue.name.ilike(f'%{search_term}%')).all()
# The for will return id, name, and num_upcoming_shows for the venues and append it to the data.
    for venue in outcome:
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all())
        })
# Assignments count and data results in the response.
        response = {
            # Will return number if venues names using len().
            "count": len(outcome),
            "data": data
        }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# Will return the specific venue.


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # Assignments.
    past_shows = []
    upcoming_shows = []
# Will return venue using .get(venue_id).
    venue = db.session.query(Venue).get(venue_id)
# Will return the Shows depending on venue_id using join Show and Artist tables.
    outcome = db.session.query(Show).join(
        Artist).filter(Show.venue_id == venue_id).all()
# Will return the time for right now.
    present_time = datetime.now()

    error = False
# To check first using try clause.
    try:
        # The for will return depending on venue_id.
        for show in outcome:
            # Check if start_time greater than present_time.
            if show.start_time > present_time:
                # Will append results in upcoming_shows.
                upcoming_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": show.start_time.strftime('%y-%m-%d  %H:%M:%S')
                })
# start_time smaller than present_time the append results in past_shows.
            else:
                past_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": show.start_time.strftime('%y-%m-%d  %H:%M:%S')
                })
# Assignments all the results to the data.
        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows)
        }
# If there is an exception.
    except:
        error = True
# If there is an error.
    if error:
        abort(500)
    else:
        return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

#  Will create Venue


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)

    error = False
# To check first using try clause and if form.validate():
    try:
        if form.validate():
            # Will create a new venue object to be successfully stored using db.session.add(venue).
            venue = Venue()
            form.populate_obj(venue)
            db.session.add(venue)
# Will commit all the changes in the session.
            db.session.commit()
        else:
            print(form.errors)
# If there is an exception it will be rollback().
    except():
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
# If there is an error.
    if error:
        abort(500)
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
# else it is a success.
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')
# Delete the venues using methods=['DELETE'].


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
# To check first using try clause.
    try:
        # Will delete the venue and show depending on venue_id using delete() .
        Venue.query.filter_by(id=venue_id).delete()
     #  venue = Venue.query.filter_by(id=venue_id)
     #   db.session.delete(venue)
# Will commit all the changes in the session.
        db.session.commit()
# If there is an exception it will be rollback().
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        # If there is an error.
        abort(500)
        flash('An error occurred. Venue could not be deleted.')
# else it is a success.
    else:
        flash('Venue was successfully deleted!')
        return render_template('pages/home.html')

    return None

#  Artists Controllers.
#  ----------------------------------------------------------------
# Will return all the artists.


@app.route('/artists')
def artists():
    # Will return all the artists and save them in data.
    data = db.session.query(Artist).all()

    return render_template('pages/artists.html', artists=data)

# Will search in the artists.


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # Assignments.
    data = []
# Return what the user typed using get.
    search_term = request.form.get('search_term', '')
# Will return artists names and it is case-insensitive using .ilike(f'%{search_term}%').
    artist = db.session.query(Artist).filter(
        Artist.name.ilike(f'%{search_term}%')).all()
# The for will return id, name, and num_upcoming_shows for the artists and append it to the data.
    for art in artist:
        data.append({
            "id": art.id,
            "name": art.name,
            "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == art.id).filter(Show.start_time > datetime.now()).all())
        })
# Assignments count and data results in the response.
    response = {
        # Will return number if artists names using len().
        "count": len(artist),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# Will return the specific artist.


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # Assignments.
    past_shows = []
    upcoming_shows = []
# Will return venue using .get(artist_id).
    artist = db.session.query(Artist).get(artist_id)
# Will return the Shows depending on artist_id using join Show and Venue tables.
    show = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).all()
# Will return the time for right now.
    present_time = datetime.now()

    error = False
# To check first using try clause.
    try:
        # The for will return depending on artist_id.
        for show in show:
            # Check if start_time greater than present_time.
            if show.start_time > present_time:
                # Will append results in upcoming_shows.
                upcoming_shows.append({
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "start_time": show.start_time.strftime('%y-%m-%d  %H:%M:%S')
                })
# start_time smaller than present_time the append results in past_shows.
            else:
                past_shows.append({
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "start_time": show.start_time.strftime('%y-%m-%d  %H:%M:%S')
                })
# Assignments all the results to the data.
        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows)
        }
# If there is an exception.
    except():
        error = True
# If there is an error.
    if error:
        abort(500)
    else:
        return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
# Display data using methods=['GET'] to Edit artist.


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
# Will return Venue depending on artist_id.
    artist = db.session.query(Artist).get(artist_id)
# Will display and edit artist in the form that comes from the dataBase.
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)

# Will post the artists data using methods=['POST'].


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    form = ArtistForm(request.form)
# Will return artist depending on artist_id.
    artist = db.session.query(Artist).get(artist_id)

    error = False
# To check first using try clause and if form.validate():
    try:
        if form.validate():
            # Will commit all the changes in the session.
            form.populate_obj(artist)
            db.session.add(artist)
            db.session.commit()
        else:
            print(form.errors)
# If there is an exception it will be rollback().
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
# If there is an error.
    if error:
        abort(500)
# else it is a success.
    else:
        return redirect(url_for('show_artist', artist_id=artist_id))

# Display data using methods=['GET'] to Edit venue.


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
# Will return Venue depending on venue_id.
    venue = db.session.query(Venue).get(venue_id)
# Will display and edit venues in the form that comes from the dataBase.
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)

# Will post the venues data using methods=['POST'].


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    form = VenueForm(request.form)
# Will return Venue depending on venue_id.
    venue = db.session.query(Venue).get(venue_id)

    error = False
# To check first using try clause and if form.validate():
    try:
        if form.validate():
            form.populate_obj(venue)
            db.session.add(venue)
# Will commit all the changes in the session.
            db.session.commit()
        else:
            print(form.errors)
# If there is an exception it will be rollback().
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
# If there is an error.
    if error:
        abort(500)
# else it is a success.
    else:
        return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

#  Will create Arist


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    form = ArtistForm(request.form)

    error = False
# To check first using try clause and if form.validate():
    try:
        if form.validate():
            # Will create a new artist object to be successfully stored using db.session.add(artist).
            artist = Artist()
            form.populate_obj(artist)
            db.session.add(artist)
# Will commit all the changes in the session.
            db.session.commit()
        else:
            print(form.errors)
# If there is an exception it will be rollback().
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
# If there is an error.
    if error:
        abort(500)
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
# else it is a success.
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

        return render_template('pages/home.html')


#  Shows Controllers
#  ----------------------------------------------------------------
# Will return all the shows.

@app.route('/shows')
def shows():
    # Assignments.
    data = []
# Will return all the show results after joining the tables.
    outcome = db.session.query(Show).join(Artist).join(Venue).all()
# The for will return shows attributes.
    for out in outcome:
        # Will append results in the data.
        data.append({
            "venue_id": out.venue_id,
            "venue_name": out.venue.name,
            "artist_id": out.artist_id,
            "artist_name": out.artist.name,
            "artist_image_link": out.artist.image_link,
            "start_time": out.start_time.strftime('%y-%m-%d  %H:%M:%S')
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

#  Create shows.


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

    form = ShowForm(request.form)
    error = False
# To check first using try clause and if form.validate():
    try:
        if form.validate():
            show = Show()
            form.populate_obj(show)
            db.session.add(show)
            db.session.commit()
        else:
            print(form.errors)
# If there is an exception.
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
# If there is an error.
    if error:
       # abort(500)
        flash('An error occurred. Show could not be listed.')
    else:
        flash('Show was successfully listed!')

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
#----------------------------------------------------------------------------#
#----------------------------------------------------------------------------#
# references
#----------------------------------------------------------------------------#
#----------------------------------------------------------------------------#

# https://docs.sqlalchemy.org/en/13/orm/relationship_api.html#sqlalchemy.orm.relationship
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#simple-relationships
# https://code.tutsplus.com/articles/sql-for-beginners-part-3-database-relationships--net-8561
# https://flask.palletsprojects.com/en/1.1.x/patterns/wtforms/
# https://www.javatpoint.com/python-list-append-method
# https://www.jquery-az.com/5-examples-get-python-list-length-array-tuple-dictionary-also/
# https://stackoverflow.com/questions/20363836/postgresql-ilike-query-with-sqlalchemy
# https://stackoverflow.com/questions/57287415/how-to-use-stringfield-to-validate-phone-number-in-flask-form-defining-min-max
# https://docs.python.org/3/library/datetime.html
# https://www.programiz.com/python-programming/datetime/strftime
# https://wtforms.readthedocs.io/en/2.3.x/forms/
# https://wtforms.readthedocs.io/en/2.3.x/validators/
