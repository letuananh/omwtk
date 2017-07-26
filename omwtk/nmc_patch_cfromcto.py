#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
NTU-MC Patch: Insert cfrom-cto to [word] table
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
from puchikarui.puchikarui import Schema
from collections import namedtuple
from collections import defaultdict as dd
from chirptext.leutile import Counter

########################################################################

NTUMC_DB_PATH=os.path.expanduser('./data/eng.db')
OUTPUT_FILE=os.path.expanduser('./data/eng-update.sql')
# Sense=namedtuple('SenseInfo', 'POS SenseID PosScore NegScore SynsetTerms Gloss'.split())

########################################################################

class NTUMCSchema(Schema):
    def __init__(self, data_source=None):
        Schema.__init__(self, data_source)
        self.add_table('sent', 'sid docID pid sent comment usrname'.split())
        self.add_table('word', 'sid wid word pos lemma cfrom cto comment usrname'.split())


def main():
    print("NTU-MC Patch: Insert cfrom-cto to [word] table")
    
    # Read sent & word data
    
    db = NTUMCSchema.connect(NTUMC_DB_PATH)
    sents = db.sent.select(where='sid >= ? and sid <= ?', values=[10000, 10999])
    words = db.word.select(where='sid >= ? and sid <= ?', values=[10000, 10999])
    words_by_sid = dd(list)
    
    for word in words:
        words_by_sid[word.sid].append(word)
    insert_statements = []
    
    print("Found %s sentences." % (len(words_by_sid),))
    print("Found %s words." % (len(words),))

    # verify patch:
    for sent in sents:
        words = words_by_sid[sent.sid]
        for word in words:
            found_word = sent.sent[word.cfrom:word.cto]
            if found_word != word.word:
                # print("WARNING: expecting [%s] but found [%s]" % (word.word, found_word))
                        # print(' '.join([str(x) in [tag[1], tag[2], node.get('cfrom'), node.get('cto')]]))
                        #print("node.cfrom = %s" % (node.get('cfrom')))
                        #print("node.cto = %s" % (node.get('cto')))
                        #print("tag[1] = %s" % (tag[1]))
                        #print("tag[2] = %s" % (tag[2]))
                        #print("tag    = %s" % (tag,))
                pass
    #exit()

    # Find word's cfrom & cto
    for sent in sents:
        words = words_by_sid[sent.sid]
        cfrom = 0
        for word in words:
            cfrom = smart_search(word.word, sent.sent, sent.sid, cfrom)
            if cfrom < 0:
                print("Cannot find [%s] in sid=%s [%s]" % (word.word, sent.sid, sent.sent))
                exit()
            else:
                found_word = sent.sent[cfrom:cfrom+len(word.word)]
                cto = cfrom + len(found_word)
                if found_word == word.word:
                    insert_statements.append('UPDATE word SET cfrom = %s, cto = %s WHERE sid = %s and wid = %s;' % (cfrom, cto, sent.sid, word.wid))
                else:
                    if (sent.sid, word.wid, found_word, word.word) == (10265, 1, 'Don', 'not'):
                        cto += 2
                    elif (sent.sid, word.wid, found_word, word.word) == (10372, 1, "Won'", "Will"):
                        cto += 1
                    elif (sent.sid, word.wid, found_word, word.word) == (10372, 2, "Won", "not"):
                        cto += 2
                    elif (sent.sid, word.wid, found_word, word.word) == (10392, 0, "you", "You"):
                        cto += 0
                    elif (sent.sid, word.wid, found_word, word.word) == (10395, 3, "isn", "not"):
                        cto += 2
                    elif (sent.sid, word.wid, found_word, word.word) == (10400, 5, "don", "not"):
                        cto += 2
                    elif (sent.sid, word.wid, found_word, word.word) == (10414, 3, "don", "not"):
                        cto += 2
                    else:
                        print("Found [%s] but expecting wid=%s [%s] in %s" % (found_word, word.wid, word.word, sent.sid))
                        exit()
                    insert_statements.append('UPDATE word SET cfrom = %s, cto = %s WHERE sid = %s and wid = %s;' % (cfrom, cto, sent.sid, word.wid))
    with open(OUTPUT_FILE, 'w') as patch_file:
        patch_file.write('BEGIN TRANSACTION;\n')
        for sts in insert_statements:
            patch_file.write(sts)
            patch_file.write('\n')
        patch_file.write('END TRANSACTION;\n')
    print("run the following command to patch the database:")
    print("    sqlite3 eng.db < eng-update.sql")
    pass


def smart_search(word_text, sent_text, sid, cfrom):
    loc = sent_text.find(word_text, cfrom)
    if loc < 0 and word_text == "not":
        if sid == 10265:
            return smart_search("Don't", sent_text, sid, cfrom)
        elif sid == 10372:
            return smart_search("Won't", sent_text, sid, cfrom)
        elif sid == 10395:
            return smart_search("isn't", sent_text, sid, cfrom)
        elif sid in (10400, 10414):
            return smart_search("don't", sent_text, sid, cfrom)
    if loc < 0 and word_text == 'You' and sid == 10392:
        return smart_search("you", sent_text, sid, cfrom)
    if loc < 0 and word_text == "Will":
        return smart_search("Won't", sent_text, sid, cfrom)
    else:
        return loc

def str_insert(string, char, index):
    return string[:index] + char + string[index:]


if __name__ == "__main__":
    main()
