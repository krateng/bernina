import os
from doreah.packageutils import pkgdata

import getpass
from doreah.control import mainfunction


def setpassword():
	print("Input new password")
	pw = getpass.getpass()
	print("Repeat please")
	if pw != getpass.getpass():
		print("Passwords do not match!")
	else:
		from doreah import auth
		auth.defaultuser.setpw(pw)


@mainfunction({},shield=True)
def main(action,**kwargs):
	actions = {
		"setpassword":setpassword
	}

	return actions[action](**kwargs)
