#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Create a test profile for lelesk from extracted corpus
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
__copyright__ = "Copyright 2015, OMWTK"
__credits__ = [ "Le Tuan Anh" ]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################

import os
import random
from puchikarui.puchikarui import Schema
from collections import namedtuple
from collections import defaultdict as dd
from chirptext.leutile import Counter

########################################################################

NTUMC_DB_PATH=os.path.expanduser('./data/eng.db')
RAW_FILE=os.path.expanduser('./data/speckled.txt')
TAG_FILE=os.path.expanduser('./data/speckled_synset.human')
TEST_PROFILE_OUTPUT=os.path.expanduser('./data/speckled_lelesk.txt')
TEST_PROFILE_OUTPUT_DEV=os.path.expanduser('./data/speckled_lelesk_dev.txt')
# Sense=namedtuple('SenseInfo', 'POS SenseID PosScore NegScore SynsetTerms Gloss'.split())

########################################################################

def generate_lelesk_test_profile():
	'''Generate test profile for lelesk (new format 31st Mar 2015)
	'''
	# Read all tags
	tagmap = {} # sentence ID > tags list
	# a sample line: 10000	4	13	00796315-n	adventure
	TagInfo = namedtuple('TagInfo', 'sentid cfrom cto synsetid word'.split())
	with open(TAG_FILE, 'r') as tags:
		for tag in tags:
			# br-k22-1	8	11	not%4:02:00::	not
			parts = [ x.strip() for x in tag.split('\t') ]
			if len(parts) == 5:
				tag = TagInfo(*parts)
				if tag.sentid in tagmap:
					tagmap[tag.sentid].append(tag)
				else:
					tagmap[tag.sentid] = [tag]

	# build test profile
	sentences = []
	line_count = 0
	with open(RAW_FILE, 'r') as lines:
		for line in lines:
			line_count += 1
			if line.startswith('#'):
				continue
			else:
				parts = [ x.strip() for x in line.split('\t') ]
				if len(parts) == 2:
					sid, sent = parts
					if sid in tagmap:
						print(sent)
						# found tags
						for tag in tagmap[sid]:
							sentences.append((tag.word,tag.synsetid, sent))
	# write to file
	with open(TEST_PROFILE_OUTPUT, 'w') as outputfile:
		for sentence in sentences:
			outputfile.write("%s\t%s\t%s\n" % sentence)

	# write dev profile
	random.seed(31032015)
	itemids = sorted(random.sample(range(line_count), 500))
	with open(TEST_PROFILE_OUTPUT_DEV, 'w') as outputfile:
		for itemid in itemids:  
			outputfile.write("%s\t%s\t%s\n" % sentences[itemid])	
	pass



def main():
	generate_lelesk_test_profile()

if __name__ == "__main__":
	main()
