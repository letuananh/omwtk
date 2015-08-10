#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Raw cleaner
@author: Le Tuan Anh
'''

# Copyright (c) 2015, Le Tuan Anh <tuananh.ke@gmail.com>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

__author__ = "Le Tuan Anh"
__copyright__ = "Copyright 2015, OMWTK"
__credits__ = [ "Le Tuan Anh" ]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################

import os
from puchikarui.puchikarui import Schema
from collections import namedtuple
from collections import defaultdict as dd
from chirptext.leutile import Counter
import re

########################################################################
# Configuration
########################################################################

INPUT_FILE     = os.path.expanduser('./data/input.txt')
OUTPUT_FILE    = os.path.expanduser('./data/input_cleaned.txt')
OUTPUT_NUM_FILE= os.path.expanduser('./data/input_numbered.txt')

########################################################################

def remove_numbering(line):
	cleaned_line = line
	match_results = re.match( '^\d+', line)
	if match_results:
		if not re.match( r'^\d+[.,]*', line):
			print ( "WARNING: %s" % line )
		cleaned_line = re.sub( r'^\d+[.,]*', '', line)
	return cleaned_line.strip()
	
def remove_special_chars(line):
	if line.endswith(' .'):
		# print(line)
		pass
	line = line.replace('\\', '').replace(' ?', '?')
	line = re.sub( r'\ *\.$', '.', line)
	line = re.sub( r'\ *!$', '!', line)
	line = re.sub( r'\ *,$', '!', line)
	# print ("   => %s" % line) 
	return line

def main():
	print("Script for cleaning raw text input")
	c = Counter()
	all_chars = set()
	with open(INPUT_FILE, 'r') as infile, open(OUTPUT_FILE, 'w') as outfile, open(OUTPUT_NUM_FILE, 'w') as outnumfile: 
		for linenum, line in enumerate(infile):
			c.count("Line")
			cleaned_line = remove_numbering(line)
			cleaned_line = remove_special_chars(cleaned_line)
			for a_char in cleaned_line:
				all_chars.add(a_char)
			outfile.write("%s\n" % cleaned_line)
			outnumfile.write("%s\t%s\n" % (linenum+1, cleaned_line))
		c.summarise()
	print("-" * 80)
	print("All characters: %s" % sorted(list(all_chars)))
	print("Done!")
	pass

if __name__ == "__main__":
	main()
