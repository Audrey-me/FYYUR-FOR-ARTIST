#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from operator import le
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
  if isinstance(value, str):
        date = dateutil.parser.parse(value)
  else:
        date = value
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

  # upcoming shows
  upcoming_shows_query = db.session.query(Show,Artist).join(Artist).filter(Show.venue_id == match.id).filter(Show.start_time > datetime.now()).all()
  upcoming =[] 
  for sh,ar in upcoming_shows_query:
    upcoming +=[{
      "artist_id" : ar.id,
      "artist_name": ar.name,
      "artist_image_link": ar.image_link,
      "start_time" : sh.start_time
    }]

    # past shows
  past_shows_query = db.session.query(Show,Artist).join(Artist).filter(Show.venue_id == match.id).filter(Show.start_time < datetime.now()).all()# Venue Search
  past =[] 
  for sh,ar in past_shows_query:
    past +=[{
      "artist_id" : ar.id,
      "artist_name": ar.name,
      "artist_image_link": ar.image_link,
      "start_time" : sh.start_time
    }]

    # the general data

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
    "seeking_talent": match.seeking_talent,
    "seeking_description": match.seeking_description,
    "image_link": match.image_link,
    "past_shows": past,
    "upcoming_shows": upcoming,
    "past_shows_count": len(past),
    "upcoming_shows_count": len(upcoming),
  }
  return render_template('pages/show_venue.html', venue=data)


#  CREATE VENUE

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  resp = request.form
  try:
      # getting users response
      new_venue = Venue(
        name = resp['name'],
        city = resp['city'],
        state =  resp['state'],
        address =  resp['address'],
        phone =  resp['phone'],
        # get the particular chosen genres from the array and converting to string
        genres=resp.getlist('genres'),  
        image_link = resp['image_link'],
        facebook_link =  resp['facebook_link'],
        website = resp['website_link'],
        seeking_description =  resp['seeking_description'],
        seeking_talent = bool(resp.get('seeking_talent'))
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



  # EDIT VENUES
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
 
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
   venue = Venue.query.get(venue_id)
   resp = request.form
   try:
       
        venue.name = resp['name'],
        venue.city = resp['city'],
        venue.state = resp['state'],
        venue.phone = resp['phone'],
        # get the particular chosen genres from the array and converting to string
        venue.genres= resp.getlist('genres'),  
        venue.image_link =resp['image_link'],
        venue.facebook_link = resp['facebook_link'],
        venue.website = resp['website_link'],
        venue.seeking_talent = bool(resp.get('seeking_talent')),
        venue.seeking_description = resp['seeking_description']
   # insert form data as a new Artist record in the db, instead and flash success   
        db.session.add(venue)
        db.session.commit()
        flash("Venue " + request.form['name'] + ' was successfully edited!')

   except Exception:
    db.session.rollback()
    flash("Venue " + request.form["name"] + " was not edited successfully")
    raise
   finally:
    db.session.close()

   return redirect(url_for('show_venue', venue_id=venue_id))



# DELETE VENUE
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
#  get a particular venue list by id and delete it from the list and database
  try:
    venue= Venue.query.filter(Venue.id == venue_id).first()
    db.session.delete(venue)
    db.session.commit()
    flash('venue was successfully deleted')
  except: 
   db.session.rollback()
   flash('An error occurred. Venue ' + ' unable to delete venue')

  finally:
    db.session.close()
  return render_template('pages/home.html') 
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
  upcoming_shows_query = db.session.query(Show,Artist).join(Artist).filter(Show.venue_id == match.id).filter(Show.start_time > datetime.now()).all()
  upcoming =[] 
  for sh,ar in upcoming_shows_query:
    upcoming +=[{
      "artist_id" : ar.id,
      "artist_name": ar.name,
      "artist_image_link": ar.image_link,
      "start_time" : sh.start_time
    }]

    # past shows
  past_shows_query = db.session.query(Show,Artist).join(Artist).filter(Show.venue_id == match.id).filter(Show.start_time < datetime.now()).all()# Venue Search
  past =[] 
  for sh,ar in past_shows_query:
    past +=[{
      "artist_id" : ar.id,
      "artist_name": ar.name,
      "artist_image_link": ar.image_link,
      "start_time" : sh.start_time
    }]
# general data
  data={
    "id":match.id,
    "name": match.name,
    "genres": [match.genres],
    "city":match.city,
    "state": match.state,
    "phone": match.phone,
    "website": match.website,
    "facebook_link": match.facebook_link,
    "seeking_venue": match.seeking_venue,
    "seeking_description": match.seeking_description,
    "image_link": match.image_link,
    "past_shows": past,
    "upcoming_shows": upcoming,
    "past_shows_count": len(past),
    "upcoming_shows_count": len(upcoming),
  }

  return render_template('pages/show_artist.html', artist=data)

#  UPDATE
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # get the particular artist you want to edit
  artist = Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  resp=request.form
  try:
        
        artist.name = resp['name'],
        artist.city =  resp['city'],
        artist.state =  resp['state'],
        artist.phone =  resp['phone'],
        # get the particular chosen genres from the array and converting to string
        artist.genres=resp.getlist('genres'),  
        artist.image_link = resp['image_link'],
        artist.facebook_link =  resp['facebook_link'],
        artist.website = resp['website_link'],
        artist.seeking_venue = bool(resp.get('seeking_venue'))
        artist.seeking_description =  resp['seeking_description']
   # insert form data as a new Artist record in the db, instead and flash success   
        db.session.add(artist)
        db.session.commit()
        flash("Artist " + request.form['name'] + ' was successfully edited!')

  except Exception:
    db.session.rollback()
    flash(" Artist " + request.form["name"] + "  was not edited successfully")
    raise
  
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))



#  CREATE ARTIST
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  resp= request.form
  try:
      # getting users response
      new_artist = Artist(
        name = resp['name'],
        city = resp['city'],
        state = resp['state'],
        phone = resp['phone'],
        # get the particular chosen genres from the array and converting to string
        genres= resp.getlist('genres'),  
        image_link =resp['image_link'],
        facebook_link = resp['facebook_link'],
        website = resp['website_link'],
        seeking_description = resp['seeking_description'],
        seeking_venue  = bool(resp.get('seeking_venue'))
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


# DELETE ARTIST
@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
#  get a particular venue list by id and delete it from the list and database
  try:
    artist_delete = Artist.query.filter_by(id=artist_id).first()
    db.session.delete(artist_delete)
    db.session.commit()
    flash('artist was successfully deleted')
  except: 
   db.session.rollback()
   flash('An error occurred. Artist ' + ' unable to delete artist')

  finally:
    db.session.close()
  return render_template('pages/home.html')
   # BONUS CHALLENGE: Implement a button to delete a Artist on a Artist Page, have it so that
   # clicking that button delete it from the db then redirect the user to the homepage
  # return None
  



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