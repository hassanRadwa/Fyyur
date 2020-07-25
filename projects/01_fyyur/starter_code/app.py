#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime
from sqlalchemy import func
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)


# TODO: connect to a local postgresql database
migrate=Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    genres = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String())
    artists = db.relationship("Artist", secondary="shows",lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    genres = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String())
    venues = db.relationship("Venue", secondary="shows",lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
  start_time = db.Column(db.DateTime, nullable=False)
  artist = db.relationship(Artist, backref=db.backref("shows", cascade="all, delete-orphan"),lazy=True)
  venue = db.relationship(Venue, backref=db.backref("shows", cascade="all, delete-orphan"),lazy=True)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

def convertListToString(txtlist):
  txt=''
  for value in txtlist:
    txt = txt+value+','
  txt = txt[:-1] # remove last char ','
  return txt
def strToBool(x):
  if x.lower() == 'true' :
    out = True
  else:
    out = False
  return out
  
def addValuesFromFormInDb(f,txt):
  #txt ex 'venue-add' or 'venue-edit-venue_id'
  #venue or artist
  modelType=txt.split('-')[0]
  #add or edit
  formType=txt.split('-')[1]
  try:
    if formType == 'add' and modelType == 'venue':
      newModel = Venue()
    elif formType == 'edit' and modelType == 'venue':
      ModelId  = txt.split('-')[2]
      newModel = Venue.query.filter(Venue.id == ModelId).first()
    elif formType == 'add' and modelType == 'artist':
      newModel = Artist()
    elif formType == 'edit' and modelType == 'artist':
      ModelId  = txt.split('-')[2]
      newModel = Artist.query.filter(Artist.id == ModelId).first()
    #get data from form and assign it to model
    for attr in f.keys():
      # print('attr: ',attr)
      # print('newVenue.' + attr + ' = convertListToString(f.getlist(\'' + attr + '\'))')
      exec('newModel.' + attr + ' = convertListToString(f.getlist(\'' + attr + '\'))')
      # exec('print(\'newVenue.' + attr + ' : \' + newVenue.' + attr + ')')
    if modelType == 'venue':
      newModel.seeking_talent  = strToBool(newModel.seeking_talent)
    elif modelType == 'artist':
      newModel.seeking_venue   = strToBool(newModel.seeking_venue)
    if formType == 'add':
      db.session.add(newModel)
    db.session.commit()
    # on successful db insert, flash success
    flash(modelType.capitalize() + ' ' + f['name'] + ' was successfully ' + formType + 'ed!')
  except:# TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    db.session.rollback()
    flash('An error occurred. ' + modelType.capitalize() + ' ' + f['name'] + ' could not be ' + formType + 'ed.')
  finally:
    db.session.close()
  

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
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  data=[]
  #select all veneues city, state, name
  venues=Venue.query.with_entities(Venue.city,Venue.state,Venue.name,Venue.id).all()
  #select venues city and state order by state without repetetion
  citiesStates=set(Venue.query.with_entities(Venue.city,Venue.state).order_by(Venue.state).all())
  for ctystat in citiesStates:
    venuesPerCity=[]
    for v in venues:
      #select veneues in specific city, state
      if v[0] == ctystat[0] and v[1] == ctystat[1]:
        #select no. of upcomping shows per venue
        showsPerVenue=Show.query.with_entities(func.count(Show.id)).filter(Show.start_time > datetime.datetime.now()).group_by(Show.venue_id).having(Show.venue_id==v[3]).all()
        venuesPerCity.append({
          "id":v[3],
          "name":v[2],
          "num_upcoming_shows":showsPerVenue
        })
    data.append({
      "city":ctystat[0],
      "state":ctystat[1],
      "venues":venuesPerCity
    })
      
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
    # get data from search box
  f = request.form
  # for key in f.keys():
  #   for value in f.getlist(key):
  #     print (key,":",value)
  search_term = f.get('search_term')
  resultsCount=Venue.query.with_entities(func.count(Venue.id)).filter(Venue.name.ilike('%' + search_term + '%')).all()
  results = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  data=[]
  for vnu in results:
    upcomingshowsPerVenue = Show.query.with_entities(func.count(Show.id)).filter(Show.start_time > datetime.datetime.now()).group_by(Show.venue_id).having(Show.venue_id==vnu.id).all()
    data.append({
      "id":vnu.id,
      "name":vnu.name,
      "num_upcoming_shows":upcomingshowsPerVenue
    })
  response={
    "count": resultsCount[0][0],
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  
  #select all veneue data
  s_venue = Venue.query.filter(Venue.id == venue_id).first()
  genresVenue = s_venue.genres.split(",")
  pastShowData=[]
  upcomingShowData=[]
  for shw in s_venue.shows:
    if shw.start_time < datetime.datetime.now(): 
      pastShowData.append({
        "artist_id":shw.artist.id,
        "artist_name":shw.artist.name,
        "artist_image_link":shw.artist.image_link,
        "start_time":format_datetime(str(shw.start_time))
      })
    else: 
      upcomingShowData.append({
        "artist_id":shw.artist.id,
        "artist_name":shw.artist.name,
        "artist_image_link":shw.artist.image_link,
        "start_time":format_datetime(str(shw.start_time))
      })
  data = {
    "id":                   s_venue.id,
    "name":                 s_venue.name,
    "genres":               genresVenue,
    "address":              s_venue.address,
    "city":                 s_venue.city,
    "state":                s_venue.state,
    "phone":                s_venue.phone,
    "website":              s_venue.website,
    "facebook_link":        s_venue.facebook_link,
    "seeking_talent":       s_venue.seeking_talent,
    "seeking_description":  s_venue.seeking_description,
    "image_link":           s_venue.image_link,
    "past_shows":           pastShowData,
    "upcoming_shows":       upcomingShowData,
    "past_shows_count":     len(pastShowData),
    "upcoming_shows_count": len(upcomingShowData)
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  #xxx
  
  f = request.form
  addValuesFromFormInDb(f,'venue-add')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  data=Artist.query.with_entities(Artist.id,Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  # get data from search box
  f = request.form
  # for key in f.keys():
  #   for value in f.getlist(key):
  #     print (key,":",value)
  search_term = f.get('search_term')
  resultsCount=Artist.query.with_entities(func.count(Artist.id)).filter(Artist.name.ilike('%' + search_term + '%')).all()
  results = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  data=[]
  for art in results:
    upcomingshowsPerArtist = Show.query.with_entities(func.count(Show.id)).filter(Show.start_time > datetime.datetime.now()).group_by(Show.artist_id).having(Show.artist_id==art.id).all()
    data.append({
      "id":art.id,
      "name":art.name,
      "num_upcoming_shows":upcomingshowsPerArtist
    })
  response={
    "count": resultsCount[0][0],
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }  
  #select all artist data
  s_artist = Artist.query.filter(Artist.id == artist_id).first()
  genresArtist = s_artist.genres.split(",")
  pastShowData=[]
  upcomingShowData=[]
  for shw in s_artist.shows:
    if shw.start_time < datetime.datetime.now(): 
      pastShowData.append({
        "venue_id":shw.venue.id,
        "venue_name":shw.venue.name,
        "venue_image_link":shw.venue.image_link,
        "start_time":format_datetime(str(shw.start_time))
      })
    else: 
      upcomingShowData.append({
        "venue_id":shw.venue.id,
        "venue_name":shw.venue.name,
        "venue_image_link":shw.venue.image_link,
        "start_time":format_datetime(str(shw.start_time))
      })
  data = {
    "id":                   s_artist.id,
    "name":                 s_artist.name,
    "genres":               genresArtist,
    "city":                 s_artist.city,
    "state":                s_artist.state,
    "phone":                s_artist.phone,
    "website":              s_artist.website,
    "facebook_link":        s_artist.facebook_link,
    "seeking_venue":       s_artist.seeking_venue,
    "seeking_description":  s_artist.seeking_description,
    "image_link":           s_artist.image_link,
    "past_shows":           pastShowData,
    "upcoming_shows":       upcomingShowData,
    "past_shows_count":     len(pastShowData),
    "upcoming_shows_count": len(upcomingShowData)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  
  #select all veneue data
  s_artist = Artist.query.filter(Artist.id == artist_id).first()
  genresArtist = s_artist.genres.split(",")
  # glist=[]
  # for g in genresVenue:   
  #   glist.append(('id',g))
  
  artist = {
    "id":                   s_artist.id,
    "name":                 s_artist.name,
    "genres":               genresArtist,
    "city":                 s_artist.city,
    "state":                s_artist.state,
    "phone":                s_artist.phone,
    "website":              s_artist.website,
    "facebook_link":        s_artist.facebook_link,
    "seeking_venue":        s_artist.seeking_venue,
    "seeking_description":  s_artist.seeking_description,
    "image_link":           s_artist.image_link
  }
  
  # members = ['name', 'city', 'phone', 'website', 'facebook_link', 'seeking_description', 'image_link']
  members = [attr for attr in form.data.keys() if not attr.startswith("csrf")]
  print ('members : ', members)
  for attr in members:
    # print('attr: ' + attr)
    # print('s_artist.' + attr + ': ', getattr(s_artist, attr))
    # print('form.' + attr + '.data = getattr(s_artist,\''+ attr + '\')')
    exec('form.' + attr + '.data = getattr(s_artist,\'' + attr + '\')')
    # print('form.' + attr + ': ', getattr(form, attr))
  # print('loop done!')

  # form.name.data                = s_venue.name
  # form.address.data             = s_venue.address
  # form.city.data                = s_venue.city
  # form.phone.data               = s_venue.phone
  # form.website.data             = s_venue.website
  # form.facebook_link.data       = s_venue.facebook_link
  # form.seeking_description.data = s_venue.seeking_description
  # form.image_link.data          = s_venue.image_link

  # form.genres.data         = genresArtist
  # form.state.data          = s_artist.state
  form.seeking_venue.data  = str(s_artist.seeking_venue)
  
  print('form.genres', form.genres)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  f = request.form
  addValuesFromFormInDb(f,'artist-edit-'+str(artist_id))
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  #select all veneue data
  s_venue = Venue.query.filter(Venue.id == venue_id).first()
  genresVenue = s_venue.genres.split(",")
  # glist=[]
  # for g in genresVenue:   
  #   glist.append(('id',g))
  
  venue = {
    "id":                   s_venue.id,
    "name":                 s_venue.name,
    "genres":               genresVenue,
    "address":              s_venue.address,
    "city":                 s_venue.city,
    "state":                s_venue.state,
    "phone":                s_venue.phone,
    "website":              s_venue.website,
    "facebook_link":        s_venue.facebook_link,
    "seeking_talent":       s_venue.seeking_talent,
    "seeking_description":  s_venue.seeking_description,
    "image_link":           s_venue.image_link
  }

  # members = ['name', 'address', 'city', 'phone', 'website', 'facebook_link', 'seeking_description', 'image_link']
  
  members = [attr for attr in form.data.keys() if not attr.startswith("csrf")]
  print ('members : ', members)

  for attr in members:
    # print('attr: ' + attr)
    # print('s_venue.' + attr + ': ', getattr(s_venue, attr))
    # print('form.' + attr + '.data = getattr(s_venue,\'' + attr + '\')')
    exec('form.' + attr + '.data = getattr(s_venue,\'' + attr + '\')')
    # print('form.' + attr + ': ', getattr(form, attr))
  # print('loop done!')

  # form.name.data                = s_venue.name
  # form.address.data             = s_venue.address
  # form.city.data                = s_venue.city
  # form.phone.data               = s_venue.phone
  # form.website.data             = s_venue.website
  # form.facebook_link.data       = s_venue.facebook_link
  # form.seeking_description.data = s_venue.seeking_description
  # form.image_link.data          = s_venue.image_link

  # form.genres.data         = genresVenue
  # form.state.data          = s_venue.state
  form.seeking_talent.data = str(s_venue.seeking_talent)
  
  print('form.genres', form.genres)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  f = request.form
  addValuesFromFormInDb(f,'venue-edit-' + str(venue_id))
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # try:
  #   f = request.form
  #   # for key in f.keys():
  #   #   for value in f.getlist(key):
  #   #     print (key,":",value)
  #   newArtist = Artist()
  #   newArtist.genres              = convertListToString(f.getlist('genres'))
  #   newArtist.name                = f.get('name')
  #   newArtist.city                = f.get('city')
  #   newArtist.state               = f.get('state')
  #   newArtist.phone               = f.get('phone')
  #   newArtist.website             = f.get('website')
  #   newArtist.facebook_link       = f.get('facebook_link')
  #   #convert string to boolean
  #   newArtist.seeking_venue       = strToBool(f.get('seeking_venue'))
  #   newArtist.seeking_description = f.get('seeking_description')
  #   newArtist.image_link          = f.get('image_link')
  #   # attrs = vars(newArtist)
  #   db.session.add(newArtist)
  #   db.session.commit()
  #   # on successful db insert, flash success
  #   flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # except:
  #   # TODO: on unsuccessful db insert, flash an error instead.
  #   # # e.g., flash('An error occurred. Artist ' + artistForm.name.data + ' could not be listed.')
  #   db.session.rollback()
  #   flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  # finally:
  #   db.session.close()
  f = request.form
  addValuesFromFormInDb(f,'artist-add')
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  data=[]
  showsData=Show.query.order_by(db.asc(Show.start_time)).all()
  for showData in showsData:
    data.append({
      "venue_id":showData.venue.id,
      "venue_name":showData.venue.name,
      "artist_id":showData.artist.id,
      "artist_name":showData.artist.name,
      "artist_image_link":showData.artist.image_link,
      "start_time":format_datetime(str(showData.start_time))
    })
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
  try:
    f = request.form
    newShow = Show()
    newShow.artist_id  = f.get('artist_id')
    newShow.venue_id   = f.get('venue_id')
    newShow.start_time = f.get('start_time')
    attrs = vars(newShow)
    db.session.add(newShow)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # # e.g., flash('An error occurred. Artist ' + artistForm.name.data + ' could not be listed.')
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
