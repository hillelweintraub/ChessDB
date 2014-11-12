#A script to create corresponding FEN files for each of the twic.pg files

import os
import sys
import time
from glob import glob

base = os.path.join('..','data')
pgn_dir = os.path.join(base,os.path.join('NewTWIC','PGN'))
fen_dir = os.path.join(base,os.path.join('NewTWIC','FEN'))
pgn2fen = './pgn2fen.exe'

if len(sys.argv) == 1: start_file = 0
else: start_file = int(sys.argv[1])

for pgn_file in glob(os.path.join(pgn_dir,'*.pgn')):
	file_num = int(pgn_file[-9:-4])
	if file_num < start_file: continue
	print "Processing file: %s"%pgn_file
	with open(pgn_file,'r') as f:
		s = f.read().strip()
	time.sleep(.001)
	with open(pgn_file,'w') as f:
		f.write(s)
	fen_file = 'twic%05d'%file_num + '.fen'
	fen_file = os.path.join(fen_dir,fen_file)
	exit_status = os.system(pgn2fen + ' ' + pgn_file + '>' + fen_file)
	if exit_status != 0: break
	print "Successfully created file: %s"%fen_file
