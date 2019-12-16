import os
import math



FORMATS = {
	"video":["mp4","webm","mkv"],
	"image":["jpeg","jpg","png","webp"],
	"metadata":["yml","yaml","info"]
}

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
from .yamlparse import build

from .db import Artist,Image,Movie,Show,Season,Episode,Cast

def parsedir(dir,prefix=()):

	thispath = prefix + (dir.name,)

	media = dir.get_files("video")

	if len(media) == 0:
		print(dir.name,"is not a movie / show folder")
	else:
		metadata = dir.get_files("metadata")
		info = {}
		for f in metadata:
			info.update(yamlparse(os.path.join(*thispath,f)))
		build(info)

	for d in dir.subdirs:
		parsedir(d,thispath)

def parsepath(pth):
	dir = scandir(pth)
	parsedir(dir)
