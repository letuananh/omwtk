#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script to convert a corpus to text file
@author: Le Tuan Anh
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

__author__ = "Le Tuan Anh"
__copyright__ = "Copyright 2015, OMWTK"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################

import os
from puchikarui import Schema
from collections import namedtuple
from collections import defaultdict as dd
from chirptext.leutile import Counter
from chirptext.texttaglib import TaggedDoc


########################################################################
# Configuration
########################################################################

DATA_DIR = os.path.expanduser('./data')
NTUMC_DB_PATH = os.path.join(DATA_DIR, 'eng.db')
OUTPUT_FILE = os.path.join(DATA_DIR, 'speckled_raw.txt')
OUTPUT_FILE_WITH_SID = os.path.join(DATA_DIR, 'speckled.txt')
OUTPUT_TOKEN_FILE = os.path.join(DATA_DIR, 'speckled_tokens.txt')
OUTPUT_WORDS = os.path.join(DATA_DIR, 'speckled_words.txt')
OUTPUT_CONCEPTS = os.path.join(DATA_DIR, 'speckled_concepts.txt')
OUTPUT_LINKS = os.path.join(DATA_DIR, 'speckled_cwlinks.txt')


test_sids = [10315, 10591, 10598]
testdoc = TaggedDoc(DATA_DIR, 'test')


class NTUMCSchema(Schema):
    def __init__(self, data_source=None):
        Schema.__init__(self, data_source)
        self.add_table('sent', 'sid docID pid sent comment usrname'.split())
        self.add_table('word', 'sid wid word pos lemma cfrom cto comment usrname'.split())
        self.add_table('concept', 'sid cid clemma tag tags comment ntag usrname'.split())
        self.add_table('cwl', 'sid wid cid'.split())


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
    # ignored_tags = "('e', 'x', 'w', 'org', 'loc', 'per', 'dat', 'oth', 'num', 'dat:year')"
    # concepts
    cquery = 'sid >= ? and sid <= ?'
    concepts = db.concept.select(where=cquery, orderby='sid, cid', values=[10000, 10999])
    # concept-words links
    lquery = 'sid >= ? and sid <= ?'
    links = db.cwl.select(where=lquery, orderby='sid, cid, wid', values=[10000, 10999])
    with open(OUTPUT_FILE, 'w') as outfile:
        for sent in sents:
            outfile.write(sent.sent)
            outfile.write('\n')
    with open(OUTPUT_FILE_WITH_SID, 'w') as outfile, open(testdoc.sent_path, 'w') as test_sent:
        for sent in sents:
            outfile.write('%s\t%s\n' % (sent.sid, sent.sent))
            if sent.sid in test_sids:
                test_sent.write('%s\t%s\n' % (sent.sid, sent.sent))
    with open(OUTPUT_TOKEN_FILE, 'w') as outfile, open(OUTPUT_WORDS, 'w') as wordfile, open(testdoc.word_path, 'w') as test_words:
        for word in words:
            outfile.write("%s\t%s\n" % (word.sid, word.lemma))
            word_tup = (word.sid, word.wid, word.word, word.lemma, word.pos)
            wordfile.write(('\t'.join(("%s",) * len(word_tup)) + '\n') % word_tup)
            if word.sid in test_sids:
                test_words.write(('\t'.join(("%s",) * len(word_tup)) + '\n') % word_tup)
    ignored_concepts = list()
    with open(OUTPUT_CONCEPTS, 'w') as confile, open(testdoc.concept_path, 'w') as test_concepts:
        for c in concepts:
            con_tup = (c.sid, c.cid, c.clemma, c.tag)
            if c.tag in ('e', 'x', 'w', 'org', 'loc', 'per', 'dat', 'oth', 'num', 'dat:year'):
                ignored_concepts.append((c.sid, c.cid))
                continue
            else:
                confile.write(('\t'.join(("%s",) * len(con_tup)) + '\n') % con_tup)
                if c.sid in test_sids:
                    test_concepts.write(('\t'.join(("%s",) * len(con_tup)) + '\n') % con_tup)
    with open(OUTPUT_LINKS, 'w') as lnkfile, open(testdoc.link_path, 'w') as test_links:
        for lnk in links:
            if (lnk.sid, lnk.cid) in ignored_concepts:
                continue
            else:
                if lnk.sid in test_sids:
                    test_links.write('{}\t{}\t{}\n'.format(lnk.sid, lnk.cid, lnk.wid))
            lnkfile.write('{}\t{}\t{}\n'.format(lnk.sid, lnk.cid, lnk.wid))
    print("Extracted data has been written to:")
    print("\tRaw sentence         : %s" % (OUTPUT_FILE,))
    print("\tRaw sentence with SID: %s" % (OUTPUT_FILE_WITH_SID,))
    print("\tTokenization info    : %s" % (OUTPUT_TOKEN_FILE,))
    print("\tWords                : %s" % (OUTPUT_WORDS,))
    print("\tConcepts             : %s" % (OUTPUT_CONCEPTS,))
    print("Done!")
    pass


if __name__ == "__main__":
    main()
