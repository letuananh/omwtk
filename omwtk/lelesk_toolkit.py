#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Create a test profile for lelesk from extracted corpus
@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2015, Le Tuan Anh <tuananh.ke@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2015, OMWTK"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################

import os
import random
from collections import namedtuple
from collections import defaultdict as dd
from chirptext.leutile import Counter

########################################################################

NTUMC_DB_PATH = os.path.expanduser('./data/eng.db')
RAW_FILE = os.path.expanduser('./data/speckled.txt')
TAG_FILE = os.path.expanduser('./data/speckled_tags_gold.txt')
TOKEN_FILE = os.path.expanduser('./data/speckled_tokens.txt')
TEST_PROFILE_OUTPUT = os.path.expanduser('./data/speckled_llall.txt')
TEST_PROFILE_OUTPUT_DEV = os.path.expanduser('./data/speckled_lldev.txt')
# Sense=namedtuple('SenseInfo', 'POS SenseID PosScore NegScore SynsetTerms Gloss'.split())

########################################################################

def pos2wnpos(pos, lemma=None):
    ''' Convert NTUMC's pos to WN's pos
    '''
    if  pos == 'VAX':  #local tag for auxiliaries
        return 'x'
    elif pos in ['CD', 'NN', 'NNS', 'NNP', 'NNPS', 'WP', 'PRP']: 
        # include proper nouns and pronouns
        ## fixme flag for proper nouns
        return 'n'
    elif pos.startswith('V'):
        return('v')
    elif pos.startswith('J') or pos in ['WDT',  'WP$', 'PRP$', 'PDT', 'PRP'] or \
        (pos=='DT' and not lemma in ['a', 'an', 'the']):  ### most determiners
        return('a')
    elif pos.startswith('RB') or pos == 'WRB':
        return('r')
    else:
        return 'x'


def generate_lelesk_test_profile():
    '''Generate test profile for lelesk (new format 31st Mar 2015)
    '''
    # Read all tags
    tagmap = dd(list)  # sentence ID > tags list
    # a sample line: 10000  4   13  00796315-n  adventure   NN
    TagInfo = namedtuple('TagInfo', 'sentid cfrom cto synsetid word pos'.split())
    c = Counter()
    with open(TAG_FILE, 'r') as tags:
        for tag in tags:
            # br-k22-1  8   11  not%4:02:00::   not
            parts = [x.strip() for x in tag.split('\t')]
            if len(parts) == 6:
                tag = TagInfo(*parts)
                tagmap[tag.sentid].append(tag)

    # read in words
    wordmap = dd(list)
    with open(TOKEN_FILE, 'r') as wordfile:
        for line in wordfile:
            if line.startswith('#') or len(line.strip()) == 0:
                continue
            # sid word
            parts = [x.strip() for x in line.split('\t')]
            if len(parts) == 2:
                (sid, word) = parts
                wordmap[sid].append(word)

    # build test profile
    sentences = []
    line_count = 0
    with open(RAW_FILE, 'r') as lines:
        for line in lines:
            line_count += 1
            if line.startswith('#'):
                continue
            else:
                parts = [x.strip() for x in line.split('\t')]
                if len(parts) == 2:
                    sid, sent = parts
                    tokens = ''
                    if sid in wordmap:
                        tokens = '|'.join(wordmap[sid])
                    if sid in tagmap:
                        print(sent)
                        # found tags
                        pos = pos2wnpos(tag.pos, tag.word)
                        c.count(pos)
                        for tag in tagmap[sid]:
                            sentences.append((tag.word, tag.synsetid, pos, sent, tokens))
    # write to file
    with open(TEST_PROFILE_OUTPUT, 'w') as outputfile:
        for k, v in c.sorted_by_count():
            outputfile.write("# %s: %s\n" % (k, v))
        for sentence in sentences:
            outputfile.write("%s\t%s\t%s\t%s\t%s\n" % sentence)

    # write dev profile
    random.seed(31032015)
    itemids = sorted(random.sample(range(line_count), 500))
    with open(TEST_PROFILE_OUTPUT_DEV, 'w') as outputfile:
        for itemid in itemids:
            outputfile.write("%s\t%s\t%s\t%s\t%s\n" % sentences[itemid])
    pass


def main():
    generate_lelesk_test_profile()


if __name__ == "__main__":
    main()
