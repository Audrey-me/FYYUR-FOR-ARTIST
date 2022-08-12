#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from sqlite3 import dbapi2
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from models import db,Venue, Artist, Show
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import collections


#----------------------------------------------------------------------------#
# App Config.
#--------------------------------------------------------------------[--------#
 
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)
collections.Callable = collections.abc.Callable
#----------------------------------------------------------------------------#
# Models.

# imported from the model.py

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  venues= []
  distinct_venue = Venue.query.distinct(Venue.city, Venue.state).all()
  for x in distinct_venue:
    city_state = Venue.query.filter(Venue.city == x.city, Venue.state == x.state).all()
    for y in city_state:
      venues += [{
        "id": y.id,
        "name": y.name,
      }]
    data +=[{
    "city": x.city,
    "state": x.state,
    "venues": venues
    }]
    venues=[]
  return render_template('pages/venues.html', areas=data)


# Venue Search

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  # gets the searches and provide results based on name
  # it also counts number of similar items
  # return empty object for no response

  search_venue= request.form['search_term']
  query_search =  db.session.query(Venue).filter(Venue.name.ilike(f'%{search_venue}%')).all()
  if query_search:
    id_name = []
    for i in query_search:
      id_name +=[{
      "id": i.id,
      "name": i.name,
      }]
    response={
      "count": len(query_search),
      "data": id_name
    }
  else:
    response={}
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# Get more details about a particular venue using it's id
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # query where the primary key matches with it's foreign key
  # display the other properties of that venue
  match = Venue.query.filter(Venue.id == venue_id).first()
  data={
    "id":match.id,
    "name": match.name,
    "genres": [match.genres],
    "address": match.address,
    "city":match.city,
    "state": match.state,
    "phone": match.phone,
    "website": match.website,
    "facebook_link": match.facebook_link,
    # "seeking_talent": match.seeking_talent,
    "seeking_description": match.seeking_description,
    "image_link": match.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  try:
      # getting users response
      new_venue = Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.city.data,
        address = form.address.data,
        phone = form.phone.data,
        # get the particular chosen genres from the array and converting to string
        genres=[form.genres.data],  
        image_link =form.image_link.data,
        facebook_link = form.facebook_link.data,
        website = form.website_link.data,
        seeking_description = form.seeking_description.data
     )
     # insert form data as a new Venue record in the db, instead and flash success
      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except Exception:
     db.session.rollback()
     flash('An error occurred. Venue ' + request.form['name'] + ' was not successfully listed')
     raise
  finally:
      db.session.close()

  
  return render_template('pages/home.html')

# Delete Venue

# @app.route('/venues/<venue_id>', methods=['DELETE'])
# def delete_venue(venue_id):
 # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
   # try:
   #   Item = Venue.query.get(venue_id)
   #   Item.query.filter_by(id=venue_id).delete()
   #   db.session.commit()
   # except:
   #   db.session.rollback()
   # finally:
   #   db.session.close()
   # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
   # clicking that button delete it from the db then redirect the user to the homepage
  # return None
  

   
#  Artists

@app.route('/artists')
def artists():
  # query the Artist table and return id and name for every artist
 artists= Artist.query.all()
 data=[]
 for artist in artists:
      data += [{
      "id":artist.id,
      "name": artist.name
     }]

 return render_template('pages/artists.html', artists=data)


# Search Artist
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # similar to what we did previously for venues
 artist_search = request.form['search_term']
 query_artist =  db.session.query(Artist).filter(Artist.name.ilike(f'%{artist_search}%')).all()
 if query_artist:
    artist_data = []
    for i in query_artist:
      artist_data +=[{
      "id": i.id,
      "name": i.name,
      }]
    response={
      "count": len(query_artist),
      "data":artist_data
    }
 else:
    response={}
  
 return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

  
  
# Search for a particular Artist
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # query where the primary key matches with it's foreign key
  # display the other properties of that artist
  match = Artist.query.filter(Artist.id == artist_id).first()
  data={
    "id":match.id,
    "name": match.name,
    "genres": [match.genres],
    "city":match.city,
    "state": match.state,
    "phone": match.phone,
    "website": match.website,
    "facebook_link": match.facebook_link,
    # "seeking_talent": match.seeking_talent,
    "seeking_description": match.seeking_description,
    "image_link": match.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
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
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  try:
      # getting users response
      new_artist = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.city.data,
        phone = form.phone.data,
        # get the particular chosen genres from the array and converting to string
        genres=[form.genres.data],  
        image_link =form.image_link.data,
        facebook_link = form.facebook_link.data,
        website = form.website_link.data,
        seeking_description = form.seeking_description.data
     )
     # insert form data as a new Venue record in the db, instead and flash success
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except Exception:
     db.session.rollback()
     flash('An error occurred. Artist ' + request.form['name'] + ' was not successfully listed')
     raise
  finally:
      db.session.close()


  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # shows has relationship with both artists and venues, so we query based on the relationship,we use select_from when we are querying multiple tables
  query_show = db.session.query(Venue, Show, Artist).select_from(Venue).join(Show).join(Artist).all()
  data=[]
  for ve,sh,ar in query_show:
    data += [{
    "venue_id": ve.id,
    "venue_name": ve.name,
    "artist_id": ar.id,
    "artist_name": ar.name,
    "artist_image_link": ar.image_link ,
    "start_time": sh.start_time
   }]


  app.logger.info(data)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  create_show = request.form
  try:
    new_show = Show(venue_id = create_show ['venue_id'],
                artist_id = create_show ['artist_id'],
                start_time = create_show ['start_time'] )
    db.session.add(new_show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
 
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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