import os
import math

pthj = os.path.join

FORMATS = {
	"video":["mp4","webm","mkv"],
	"image":["jpeg","jpg","png","webp"],
	"metadata":["yml","yaml","info"]
}

FOLDERS = {
	"cast":["cast","actors","casting","castimages","characters"]
}

FILES = {
	"cover":["cover","artwork","front","poster"],
	"background":["background","bg"]
}


def search_folder(dir):
	imgs = dir.files["image"]
	subfolders = dir.subdirs

	result = {**{t:[] for t in FILES}, **{t:{} for t in FOLDERS}}

	for i in imgs:
		rawname = ".".join(i.split(".")[:-1])
		for type in FILES:
			if rawname in FILES[type]:
				print(i,"is a",type)
				result[type].append(i)

	for sf in subfolders:
		for type in FOLDERS:
			if sf.name in FOLDERS[type]:
				print("found",type,":",sf.files)
				for f in sf.files["image"]:
					name = ".".join(f.split(".")[:-1])
					result[type][name] = pthj(sf.name,f)

	return result

class Directory:
	def __init__(self,name):
		self.name = name
		self.files = {}
		self.subdirs = []
		for type in FORMATS:
			self.files[type] = []

	def add_file(self,name):
		ext = name.split(".")[-1].lower()
		for type in self.files:
			if ext in FORMATS[type]:
				self.files[type].append(name)
				break
	def add_directory(self,dir):
		self.subdirs.append(dir)
		dir.parent = self

	def get_files(self,type=None):
		if type is None: return [f for type in self.files for f in self.files[type]]
		else: return self.files.get(type,[])

	def print(self,depth=math.inf,indent=0):
		pre = indent * " "
		print(pre,self.name)
		for dir in self.subdirs:
			dir.print(depth-1,indent+1)
		for fil in [f for type in self.files for f in self.files[type]]:
			print(pre+" ",fil)


def scandir(path):
	dir = Directory(path.split("/")[-1])

	for entry in os.scandir(path):
		if entry.is_file():
			dir.add_file(entry.name)
		else:
			dir.add_directory(scandir(os.path.join(path,entry.name)))

	return dir

from .yamlparse import parse as yamlparse
from .db import Artist,Image,Movie,Show,Season,Episode,Cast

def parsedir(dir,prefix=(),force_show=None):

	thispath = prefix + (dir.name,)

	media = dir.get_files("video")
	infofiles = dir.get_files("metadata")
	art = dir.get_files("image")

	# find out what kind of folder this is
	if len(media) + len(infofiles) + len(art) == 0:
		print(dir.name,"is not a movie / show folder")
		# category folder / user structure, just check subfolders
		for d in dir.subdirs:
			parsedir(d,thispath)
	else:
		# check what kind of media this folder is for
		info = {}
		for f in infofiles:
			info.update(yamlparse(os.path.join(*thispath,f)))
		media = build(info)

		artwork = search_folder(dir)
		print(media,"has artwork",artwork)
		for img in artwork["cover"]:
			media.artwork_cover_options.append(Image(path=pthj(*thispath,img)))
		for img in artwork["background"]:
			media.artwork_background_options.append(Image(path=pthj(*thispath,img)))
		for name in artwork["cast"]:
			print("Checking if",name,"appears in the cast of",media)
			img = artwork["cast"][name]
			print("Cast:",media.cast)
			for c in media.get_full_cast():
				print("check",c)
				artistname = c.actor.name
				rolename = c.role
				if name.lower() == artistname.lower() or name.lower() == rolename.lower():
					c.specific_picture = Image(path=pthj(*thispath,img))


		# if this folder is for a show, check subfolders (they could be seasons)
		if isinstance(media,Show):
			for d in dir.subdirs:
				if d.name in [f for type in FOLDERS for f in FOLDERS[type]]:
					print(d.name,"is a special folder, not parsing for new seasons")
				else:
					try:
						seasonnum = int(filter(str.isdigit,d.name))
						parsedir(d,thispath,force_show=(show,seasonnum))
						# parse the subfolder, tell the function that we already know the show
						# and can guess the season number
					except:
						print(d.name,"does not seem to be a season folder.")






def parsepath(pth):
	dir = scandir(pth)
	parsedir(dir)








from .db import Artist,Image,Movie,Show,Season,Episode,Cast
def build(infodict):
	if "seasons" in infodict:
		# show
		show = Show(title=infodict['title'])
		#seasons = [None] * (max(infodict["seasons"].keys())+1) # keep first element empty just so list indices == season nums
		for seasonnum in infodict["seasons"]:
			season_info = infodict["seasons"][seasonnum]
			season = Season(show=show,number=seasonnum)
			#episodes = [None] * (max(season_info["episodes"].keys())+1)
			for episodenum in season_info["episodes"]:
				episode_info = season_info["episodes"][episodenum]
				episode = Episode(season=season,number=episodenum,title=episode_info['title'])
				#episodes[episodenum] = Episode(title=episode_info['title'])

				for c in episode_info.get('cast',[]):
					 Cast(actor=Artist(name=c['actor']),role=c['role'],media=episode)

			for c in season_info.get('cast',[]):
				 Cast(actor=Artist(name=c['actor']),role=c['role'],media=season)
			#seasons[seasonnum] = Season(episodes=episodes)
		#Show(seasons=seasons,title=infodict['title'],cast=[Cast(actor=Artist(name=c['actor']),role=c['role']) for c in infodict['cast']])

		for c in infodict['cast']:
			 Cast(actor=Artist(name=c['actor']),role=c['role'],media=show)

		return show

	else:
		# movie
		movie = Movie(title=infodict['title'])

		for c in infodict['cast']:
			 Cast(actor=Artist(name=c['actor']),role=c['role'],media=movie)

		return movie
