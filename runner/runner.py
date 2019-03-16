import os
import errno
import re
import sys

rootdir = '/home/ale/Programacion/ConcuVoley'
C_EXTENSIONS = ['.c', '.h', '.cpp']


"""
RUNNER_DEST_PATH = rootdir + '/runner.d'

try:
	os.mkdir(RUNNER_DEST_PATH, 0755);
except OSError as exc:
	if exc.errno == errno.EEXIST and os.path.isdir(RUNNER_DEST_PATH):
		pass
	else:
		raise

"""

for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        ext = os.path.splitext(file)[-1].lower()
        if ext in C_EXTENSIONS:
			file_path = os.path.join(subdir, file)
			os.system("sed -i '/^.*\/\/.*longstrider*/s/^.*\/\///' " + file_path)
		

os.system("cp longstrider* " + rootdir + "/")
os.system("cp runner_lock* " + rootdir + "/")
