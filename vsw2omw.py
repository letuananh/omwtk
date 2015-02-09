#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script to convert Viet SentiWordnet to Open Multilingual Wordnet format
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
from collections import namedtuple
from chirptext.leutile import Counter

########################################################################
# Configuration
########################################################################

VSW_DATA=os.path.expanduser('./data/VietSentiWordnet_ver1.0.txt')
VSW_FIXED=os.path.expanduser('./data/VietSentiWordnet_ver1.0.1.txt')
OMW_DATA=os.path.expanduser('./data/VietSentiWordnet_ver1.0-OMW_Format.txt')
Sense=namedtuple('SenseInfo', 'POS SenseID PosScore NegScore SynsetTerms Gloss'.split())

########################################################################

def main():
	print("Script to convert Viet SentiWordnet to Open Multilingual Wordnet format")

	c = Counter()

	# Fix VSW format
	with open(VSW_DATA, 'r') as vsw_input:
		with open(VSW_FIXED, 'w') as vsw_fixed:
			for line in vsw_input.readlines():
				if line.startswith('#'):
					vsw_fixed.write(line)
					if line.startswith('# Web: https://sourceforge.net/projects/vietsentiwordne/'):
						vsw_fixed.write('#\n# Minor bugs fixed by Le Tuan Anh <tuananh.ke@gmail.com>\n')
						vsw_fixed.write('# Latest version is available at: https://github.com/letuananh/omwtk\n#\n')
				else:
					c.count('processed')
					sense = Sense(*line.split('\t'))
					if sense.Gloss.find(';') < 0:
						c.count("error")
						print(sense.Gloss.strip())
						fixedline = line
						if line.find(', "') > 0:
							fixedline = line.replace(', "', '; "', 1)
						elif line.find('"') < 0:
							c.count("No example")
						elif line.find(',"') > 0:
							fixedline = line.replace(',"', '; "', 1)
						elif line.find('như: "') > 0:
							fixedline = line.replace('như: "', '; "', 1)
						vsw_fixed.write(fixedline)
					else:
						c.count("ok")
						vsw_fixed.write(line)
	c.summarise()
	#exit()
	
	# Read file
	with open(VSW_FIXED, 'r') as vsw_input:
		lines = [ x for x in vsw_input.readlines() if not x.startswith('#') ]
	senses = [ Sense(*line.split('\t')) for line in lines ]
	
	# Write file
	with open(OMW_DATA, 'w') as omw_output:
		omw_output.write('# Prepared by Le Tuan Anh <tuananh.ke@gmail.com>\n')
		omw_output.write('# Based on Viet SentiWordnet 1.0\n')
		omw_output.write('# Latest version is available at: https://github.com/letuananh/omwtk\n')
		for sense in senses:
			# 001937986-a    vie:lemma    giỏ
			# 001937986-a    vie:def    có trình độ cao, đáng được khâm phục, khen ngợi
			# 001937986-a    vie:exe    giáo viên dạy giỏi
			synset_id = '%s-%s' % (sense.SenseID , sense.POS)
			lemma = sense.SynsetTerms.split('#')[0]
			definition = ''
			example = ''
			if sense.Gloss.find(';') > 0:
				definition = sense.Gloss[:sense.Gloss.find(';')].strip()
				example = sense.Gloss[sense.Gloss.find(';')+1:].strip()
			omw_output.write('%s\tvie:lemma\t%s\n' % (synset_id,lemma))
			if definition:
				omw_output.write('%s\tvie:def\t%s\n' % (synset_id,definition))
			if example:
				omw_output.write('%s\tvie:exe\t%s\n' % (synset_id,example))
	pass

if __name__ == "__main__":
	main()
