import os

pypath=r"D:\usr\github\cocogame\py\py"

for dirpath,dirnames,filenames in os.walk(pypath):
	if "site-packages" in dirpath:
		continue
	for fn in filenames:
		if not fn.endswith(".py"):
			continue
		if not os.path.isfile(dirpath+"\\"+fn[:-3]+".pyc"):
			fullname=dirpath+"\\"+fn
			print "delete",fullname
			os.system("del %s"%fullname)


for dirpath,dirnames,filenames in os.walk(pypath):
	if not dirnames and not filenames:
		print "rmdir ",dirpath
		os.system("rmdir %s"%dirpath)
	
os.system("pause")

