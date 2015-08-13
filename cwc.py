#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Text corpus statistics

References:
	Python documentation:
		https://docs.python.org/
	argparse module:
		https://docs.python.org/3/howto/argparse.html
	PEP 257 - Python Docstring Conventions:
		https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
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

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2015, omwtk"
__credits__ = [ "Le Tuan Anh" ]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import sys
import os
import argparse
from chirptext.leutile import TextReport, Counter

########################################################################

SPECIAL_CHARS = [ ' ', '!', ',', '.', ':', ';', '?', '“', '”' ]
TOP_K         = 10

def gen_stats(corpus_file, report_path=None):
	''' Generate statistics for a text corpus (word count, most frequent words, etc.)
	'''
	report = TextReport(report_path)
	report.header("Stat for %s" % corpus_file)
	line_count = -1
	word_count = 0
	c = Counter()
	with open(corpus_file, 'r', encoding='utf8') as infile:
		lines = infile.readlines()
		line_count = len(lines)
		for line in lines:
			tokens = line.split()
			for token in tokens:
				parts = token.split("/")
				if len(parts) == 2:
					word = parts[0]
					POS  = parts[1]
				else:
					word = parts[0]
					POS  = None
				for spechar in SPECIAL_CHARS:
					word = word.replace(spechar, '')
				word = word.lower().replace("_", " ") # original word form
				if word == '':
					print(token)
				c.count(word)
				word_count += 1
	
	report.writeline("Line count: %s" % line_count)
	report.writeline("Word count: %s" % word_count)
	report.writeline("Word class: %s" % len(c.sorted_by_count()))
	report.writeline("Top %d    :" % TOP_K)
	for item in c.sorted_by_count()[:TOP_K]:
		report.writeline("%s: %s" % (item[0], item[1]), level=1)
	report.writeline("Bottom %d :" % TOP_K)
	for item in c.sorted_by_count()[-TOP_K:]:
		report.writeline("%s: %s" % (item[0], item[1]), level=1)


########################################################################

def main():
	''' Main entry
	'''

	# It's easier to create a user-friendly console application by using argparse
	# See reference at the top of this script
	parser = argparse.ArgumentParser(description="Generate statistics for a text corpus.")
	
	# Positional argument(s)
	parser.add_argument('input', help='Path to text corpus file')

	# Optional argument(s)
	parser.add_argument('-o', '--output', help='Path to report file')
	
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-v", "--verbose", action="store_true")
	group.add_argument("-q", "--quiet", action="store_true")

	# Main script
	if len(sys.argv) == 1:
		# User didn't pass any value in, show help
		parser.print_help()
	else:
		# Parse input arguments
		args = parser.parse_args()
		# Now do something ...
		if args.input:
			gen_stats(args.input, args.output)
	pass

if __name__ == "__main__":
	main()
