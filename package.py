from distutils.core import setup
import os, py2exe, zipfile

def delete(path):
	try:
		os.remove(path)
	except OSError:
		for file in os.listdir(path):
			delete(path + "/" + file)
		os.rmdir(path)

# make exe
setup(script_args=["py2exe"], console=['agave.py'])

# zip up dist folder
print "Zipping up files."
zf = zipfile.ZipFile('distribution.zip', mode='w')
for file in os.listdir("dist"):
	zf.write("dist/" + file, file, zipfile.ZIP_DEFLATED)
zf.close()

# delete unwanted files.
print "Deleting unwanted files."
delete("build")
delete("dist")
print "Done."
