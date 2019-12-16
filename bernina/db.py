# non-relational db

from nimrodel import EAPI
import requests
import os
import re

import random


#from db_oo_helper import Ref, MultiRef, DBObject, db, save_database, load_database
from doreah.database import Database, Ref, MultiRef
from doreah.settings import get_settings
from doreah.io import ProgressBar
from doreah.packageutils import pkgdata

db = Database(file=pkgdata("database.ddb"))

class Image(db.DBObject):
	__primary__ = "path",
	path: str

	def read(self):
		if self.path.lower().endswith(".jpeg") or self.path.lower().endswith(".jpg"):
			mime = 'image/jpeg'
		elif self.path.lower().endswith(".png"):
			mime = 'image/png'
		elif self.path.lower().endswith(".webp"):
			mime = 'image/webp'
		with open(self.path,"rb") as imagefile:
			stream = imagefile.read()

		return mime,stream

	def link(self):
		return "/artwork/" + str(self.uid)

class Artist(db.DBObject):
	__primary__ = "name",
	name: str
	picture: Image = Ref(Image,exclusive=True,backref="entity")
#class Character(db.DBObject):
#	name: str


class Media:

	def get_artwork_cover(self):
		try:
			return self.artwork_cover_options[self.artwork_cover_index].link()
		except:
			return ""

class Cast(db.DBObject):
	__primary__ = "actor","role","media"
	actor: Artist =  Ref(Artist,exclusive=False,backref="castings")
	role: str
	media: Media = Ref(Media,exclusive=False,backref="cast")
	specific_picture: Image = Ref(Image,exclusive=True,backref="entity")

	def __db_repr__(self):
		return self.actor.name + " as " + self.role

	def get_specific_picture(self):
		return self.specific_picture or self.actor.picture or None



class Movie(db.DBObject,Media):
	title: str
	artwork_cover_options: list = MultiRef(Image,exclusive=True,backref="entity")
	artwork_cover_index: int
	artwork_background_options: list = MultiRef(Image,exclusive=True,backref="entity")
	artwork_background_index: int
	#cast: list = MultiRef(Cast,exclusive=True,backref="media")

	def get_full_cast(self):
		return self.cast

class Show(db.DBObject,Media):
	__primary__ = "title",
	title: str
	artwork_cover_options: list = MultiRef(Image,exclusive=True,backref="entity")
	artwork_cover_index: int
	artwork_background_options: list = MultiRef(Image,exclusive=True,backref="entity")
	artwork_background_index: int
	#cast: list = MultiRef(Cast,exclusive=True,backref="media")

	#seasons: list = MultiRef(Season,exclusive=True,backref="show")

	def get_full_cast(self):
		return list(set(self.cast + [c for s in self.seasons for c in s.cast] + [c for s in self.seasons for e in s.episodes for c in e.cast]))

class Season(db.DBObject,Media):
	__primary__ = "show","number"
	number: int
	show: Show = Ref(Show,exclusive=False,backref="seasons")
	artwork_cover_options: list = MultiRef(Image,exclusive=True,backref="entity")
	artwork_cover_index: int
	artwork_background_options: list = MultiRef(Image,exclusive=True,backref="entity")
	artwork_background_index: int
	#cast: list = MultiRef(Cast,exclusive=True,backref="media")

	#episodes: list = MultiRef(Episode,exclusive=True,backref="season")

	def __db_repr__(self):
		return self.show.title + " Season " + str(self.number)

	def get_full_cast(self):
		return list(set(self.cast + self.show.cast + [c for e in self.episodes for c in e.cast]))

class Episode(db.DBObject,Media):
	__primary__ = "season","number"
	title: str
	number: int
	season: Season = Ref(Season,exclusive=False,backref="episodes")
	#cast: list = MultiRef(Cast,exclusive=True,backref="media")

	def get_full_cast(self):
		return list(set(self.cast + self.season.cast + self.season.show.cast))

	def __db_repr__(self):
		return self.season.show.title + " S" + str(self.season.number) + " E" + str(self.number) + " " + self.title






from doreah import auth

api = EAPI(path="api",delay=True,auth=auth.check)


@api.get("movies")
def list_movies():
	return db.getall(Movie)

@api.get("shows")
def list_shows():
	return db.getall(Show)

@api.get("artists")
def list_artists():
	return db.getall(Artist)

def get_artwork(uid):
	return db.get(uid)


def save_database():
	db.save()
