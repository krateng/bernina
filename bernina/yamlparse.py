import yaml
import re


def get_first_existing_key(d,keys,default=None):
	for k in keys:
		try:
			return d[k]
		except:
			pass
	#raise KeyError
	return default

def parse(filename):
	info = {}
	with open(filename,"r") as f:
		res = yaml.safe_load(f)


	info["title"] = get_first_existing_key(res,("title","name"))
	info["sorttitle"] = get_first_existing_key(res,("sorttitle"),info["title"])

	cast = get_first_existing_key(res,("cast","actors"),[])
	info["cast"] = parse_cast(cast)



	# tv
	if "episodes" in res or "seasons" in res:
		if "episodes" in res: seasons = res["episodes"]
		elif "seasons" in res: seasons = res["seasons"]
		info["seasons"] = {}

		for key in seasons:

			# full episode specified, e.g. 1x03
			if isinstance(key,str):
				try:
					s,e = re.match(r"([0-9]+)x([0-9]+)$",key).groups()
					s,e = int(s),int(e)
				except:
					raise
					print(key,"is not a valid episode identifier!")
					continue

				if not s in info["seasons"]:
					info["seasons"][s] = {"episodes":{}}
				info["seasons"][s]["episodes"][e] = parse_episode(seasons[key])



			elif isinstance(key,int):

				# season, then episode, e.g. 1: 3: or 1: episodes: 3:
				if isinstance(seasons[key],dict) and (any(isinstance(k,int) for k in seasons[key]) or ("episodes" in seasons[key])):
					info["seasons"][key] = parse_season(seasons[key])

				# only one season, episode specified directly, e.g. 3:
				else:
					if not 1 in info["seasons"]:
						info["seasons"][1] = {"episodes":{}}
					info["seasons"][1]["episodes"][key] = parse_episode(seasons[key])


	return info


def parse_cast(info):
	result = []
	if isinstance(info,list):
		for entry in info:
			if isinstance(entry,str):
				role, actor = entry, entry #someone playing themselves
			else:
				role = get_first_existing_key(entry,("role","character"))
				actor = get_first_existing_key(entry,("name","actor","actress"))
			if actor is not None:
				result.append({"role":role,"actor":actor})
	elif isinstance(info,dict):
		for r in info:
			result.append({"role":r,"actor":info[r]})

	return result

def parse_episode(info):
	if isinstance(info,str): return {"title":info}
	elif isinstance(info,dict):
		return {
			"title":get_first_existing_key(info,("title","name")),
			"cast":parse_cast(get_first_existing_key(info,("cast","actors"),[]))
		}
	else:
		print("Could not parse data type",type(info),"to episode.")


def parse_season(info):
	episodes = info.get("episodes",{}) #explicit episodes key
	episodes.update({k:info[k] for k in info if isinstance(k,int)}) #all direct int keys are also episodes

	return {
		"episodes": {k:parse_episode(episodes[k]) for k in episodes},
		"cast":parse_cast(get_first_existing_key(info,("cast","actors"),[]))
	}


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

	else:
		# movie
		Movie(title=infodict['title'])

		for c in infodict['cast']:
			 Cast(actor=Artist(name=c['actor']),role=c['role'],media=movie)






if __name__ == "__main__":
	import sys

	print(parse(sys.argv[1]))
