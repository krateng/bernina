### PACKAGE DATA

__name__ = "bernina"
__desc__ = "A minimalist self-hosted media server"
__version__ = 0,0,1
__versionstr__ = ".".join(str(n) for n in __version__)
__author__ = {
	"name":"Johannes Krattenmacher",
	"email":"python@krateng.dev",
	"github":"krateng"
}

__requires__ = [
	"bottle>=0.12.16",
	"waitress>=1.3",
	"doreah>=1.4.2",
	"nimrodel>=0.6.1",
	"pyyaml>=5.1",
	"lesscpy>=0.13"
]
__resources__ = [
	"web/*/*",
	"web/*",
	"static/*/*",
	"data_files/*/*"
]

__commands__ = {
	"bernina":"control:main"
}



### DOREAH CONFIGURATION

from doreah import config
import pkg_resources

config(
	packageutils={
		"packagename": __name__,
		"populate": pkg_resources.resource_filename(__name__,"data_files")
	}
)
from doreah.packageutils import pkgdata, init_datafolder
init_datafolder()
config(
	logging={
		"logfolder": pkgdata("logs")
	},
	settings={
		"files":[
			pkgdata("settings","default.ini"),
			pkgdata("settings","settings.ini")
		]
	},
	auth={
		"multiuser": False,
		"cookieprefix": "bernina",
		"dbfile": pkgdata("authdb.ddb")
	}
)
