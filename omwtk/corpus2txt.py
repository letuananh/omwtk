#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script to convert a corpus to text file
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

########################################################################
# Configuration
########################################################################

DATA_DIR=os.path.expanduser('./data')
NTUMC_DB_PATH=os.path.join(DATA_DIR, 'eng.db')
OUTPUT_FILE=os.path.join(DATA_DIR, 'speckled_raw.txt')
OUTPUT_FILE_WITH_SID=os.path.join(DATA_DIR, 'speckled.txt')
OUTPUT_TOKEN_FILE=os.path.join(DATA_DIR, 'speckled_tokens.txt')
# Sense=namedtuple('SenseInfo', 'POS SenseID PosScore NegScore SynsetTerms Gloss'.split())

class NTUMCSchema(Schema):
	def __init__(self, data_source=None):
		Schema.__init__(self, data_source)
		self.add_table('sent', 'sid docID pid sent comment usrname'.split())
		self.add_table('word', 'sid wid word pos lemma cfrom cto comment usrname'.split())

########################################################################

def main():
	print("Script to convert NTU-MC to text file")
	try:
		db = NTUMCSchema.connect(NTUMC_DB_PATH)
	except Exception as err:
		print("Error: I need access to NTU-MC DB at: %s" % NTUMC_DB_PATH)
		return
	sents = db.sent.select(where='sid >= ? and sid <= ?', values=[10000, 10999])
	words = db.word.select(where='sid >= ? and sid <= ?', orderby='sid, wid', values=[10000, 10999])
	with open(OUTPUT_FILE, 'w') as outfile: 
		for sent in sents:
			outfile.write(sent.sent)
			outfile.write('\n')
	with open(OUTPUT_FILE_WITH_SID, 'w') as outfile:
		for sent in sents:
			outfile.write('%s\t%s\n' % (sent.sid, sent.sent))
	with open(OUTPUT_TOKEN_FILE, 'w') as outfile:
		for word in words:
			outfile.write("%s\t%s\n" % (word.sid, word.lemma))
	print("Extracted data has been written to:")
	print("\tRaw sentence         : %s" % (OUTPUT_FILE,))
	print("\tRaw sentence with SID: %s" % (OUTPUT_FILE_WITH_SID,))
	print("\tTokenization info    : %s" % (OUTPUT_TOKEN_FILE,))
	print("Done!")
	pass

if __name__ == "__main__":
	main()
