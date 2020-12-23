# Import db

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# Venue Model


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String()))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
# On delete we need to use cascade=" all, delete-orphan" because of the dependence between venue and show.
    show = db.relationship('Show', backref='venue',
                           lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}'

# Artist Model


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String()))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    show = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}>'

# Show Model


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
# On delete we need to use ondelete="CASCADE" because of the dependence between venue and show.
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id', ondelete="CASCADE"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Show ID: {self.id}>'
