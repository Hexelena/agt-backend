#! /usr/bin/env python3
"""
Module that parses the file operone_fixes.txt and generates a dictionary out of it
"""

ALL_FIX_DICT = {}
VOCAB_FIX_DICT = {}

STATES = ['ALL', 'VOCAB']
SECTION = ''

with open('operone_fixes.txt', 'r') as f:
	for line in f.readlines():

		line = line.strip() # strip whitespaces
		line = line.strip(',') # strip commas at end of line
		if line.startswith('#'):
			continue
		if line.strip('[]') in STATES:
			SECTION = line.strip('[]')

		middle = line.find('->') # determine middle
		key = line[:middle]
		key = key.strip("' ")
		value = line[middle + len('->'):]
		value = value.strip("' ")
		# add key - value pair to dict
		if SECTION == 'ALL':
			ALL_FIX_DICT[key] = value
		elif SECTION == 'VOCAB':
			VOCAB_FIX_DICT[key] = value

if __name__ == '__main__':
	print('This is a module that is meant to be imported.')
	print('It does not really serve any purpose on its own!')