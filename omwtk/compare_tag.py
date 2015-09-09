#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script to compare annotations
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
from chirptext.leutile import Counter
from chirptext.texttaglib import writelines
from operator import itemgetter

########################################################################
# Configuration
########################################################################

NTUMC_DB_PATH=os.path.expanduser('./data/eng.db')
TAG_ISF=os.path.expanduser('./data/speckled_synset.isf')
TAG_HUMAN=os.path.expanduser('./data/speckled_synset.human')
TAG_MATCH = os.path.expanduser('./data/speckled_synset.match')
TAG_MISSING = os.path.expanduser('./data/speckled_synset.miss')
TAG_MISSING_BY_LEMMA = os.path.expanduser('./data/speckled_synset.miss_by_lemma')
# Sense=namedtuple('SenseInfo', 'POS SenseID PosScore NegScore SynsetTerms Gloss'.split())

class NTUMCSchema(Schema):
	def __init__(self, data_source=None):
		Schema.__init__(self, data_source)
		self.add_table('sent', 'sid docID pid sent comment usrname'.split())

########################################################################

def read_data(file_path):
	data = []
	with open(file_path, 'r') as input_file:
		for line in input_file:
			data.append(tuple(line.split()))
	return data

def same_synsetid(sid1, sid2):
	if sid1[:-1] == sid2[:-1] and set((sid1[-1], sid2[-1])) == set(('r', 'a')):
		print(sid1 + '\t' + sid2)
		return True
	else:
		return sid1 == sid2

def main():
	print("Script to compare annotations")
	tag_isf = read_data(TAG_ISF)
	tag_human = read_data(TAG_HUMAN)
	tag_match = []
	tag_missing = []
	tag_missing_by_lemma = []
	for tagh in tag_human:
		found = None
		for tagi in tag_isf:
			if tagi[:-2] == tagh[:-2] and same_synsetid(tagi[-2], tagh[-2]):
				tag_match.append(tagh)
				found = tagi
				break
		if found is None:
			tag_missing.append(tagh)
	c = Counter()
	for missing in tag_missing:
		c.count(missing[-1])
	c.summarise()
	for k in c.count_map:
		tag_missing_by_lemma.append((k, c[k]))
	tag_missing_by_lemma.sort(key=itemgetter(1))
	print("Match: %s" % (len(tag_match),))
	writelines([ '\t'.join(x) for x in tag_match ], TAG_MATCH)
	writelines([ '\t'.join(x) for x in tag_missing ], TAG_MISSING)
	writelines([ '\t'.join([str(c) for c in x]) for x in reversed(tag_missing_by_lemma) ], TAG_MISSING_BY_LEMMA)
	print("Done!")
	pass

if __name__ == "__main__":
	main()
