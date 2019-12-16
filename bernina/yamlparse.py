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

	if "name" in res: info["title"] = res["name"]
	elif "title" in res: info["title"] = res["title"]
	if "sorttitle" in res: info["sorttitle"] = res["sorttitle"]
	elif "title" in info: info["sorttitle"] = info["title"]

	cast = []
	info["cast"] = []
	if "cast" in res:
		cast = res["cast"]
	elif "actors" in res:
		cast = res["actors"]

	if isinstance(cast,list):
		for entry in cast:
			role, actor = None, None
			if "role" in entry: role = entry["role"]
			elif "character" in entry: role = entry["character"]
			if "name" in entry: actor = entry["name"]
			elif "actor" in entry: actor = entry["name"]
			elif "actress" in entry: actor = entry["actress"]
			if actor is not None and role is not None:
				info["cast"].append({"role":role,"actor":actor})
	elif isinstance(cast,dict):
		for r in cast:
			info["cast"].append({"role":r,"actor":cast[r]})



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
						info["seasons"][1] = {}
					info["seasons"][1][key] = parse_episode(seasons[key])


	return info

def parse_episode(info):
	if isinstance(info,str): return {"title":info}
	elif isinstance(info,dict):
		return {
			"title":get_first_existing_key(info,("title","name"))
			# other episode info to parse?
		}
	else:
		print("Could not parse data type",type(info),"to episode.")


def parse_season(info):
	episodes = info.get("episodes",{}) #explicit episodes key
	episodes.update({k:info[k] for k in info if isinstance(k,int)}) #all direct int keys are also episodes

	return {
		"episodes": {k:parse_episode(episodes[k]) for k in episodes}
		# other season info to parse?
	}



if __name__ == "__main__":
	import sys

	print(parse(sys.argv[1]))
