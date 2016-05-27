#! /usr/bin/env python3
"""
Module that parses the file operone_fixes.txt and generates a dictionary out of it
"""

OPERONE_FIX_DICT = {}

with open('operone_fixes.txt', 'r') as f:
	for line in f.readlines():

		line = line.strip() # strip whitespaces
		line = line.strip(',') # strip commas at end of line

		middle = line.find('->') # determine middle
		key = line[:middle]
		key = key.strip("' ")
		value = line[middle + len('->'):]
		value = value.strip("' ")
		# add key - value pair to dict
		OPERONE_FIX_DICT[key] = value

#for el in OPERONE_FIX_DICT:
#	print(el.ljust(50), ' | -> | ', OPERONE_FIX_DICT[el])

if __name__ == '__main__':
	print('This is a module that is meant to be imported.')
	print('It does not really serve any purpose on its own!')