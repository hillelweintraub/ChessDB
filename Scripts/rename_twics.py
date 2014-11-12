#script to rename all twic files

from glob import glob
import os
import shutil

base = "NewTWIC"
os.mkdir(base)
for fname in glob("twic*.pgn"):
	fnumber = int(fname[4:-4])
	new_name = os.path.join(base,'twic%05d.pgn'%fnumber)
	shutil.copyfile(fname, new_name)
