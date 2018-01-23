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
import logging
from puchikarui import Schema
from chirptext.leutile import FileHelper, Counter, TextReport
from chirptext.texttaglib import TaggedDoc, Token
from yawlib.helpers import get_wn

########################################################################
# Configuration
########################################################################

DATA_DIR = FileHelper.abspath('./data')
NTUMC_DB_PATH = os.path.join(DATA_DIR, 'eng.db')
OUTPUT_FILE = os.path.join(DATA_DIR, 'speckled_raw.txt')
test_sids = [10315, 10591, 10598]
testdoc = TaggedDoc(DATA_DIR, 'test')


def getLogger():
    return logging.getLogger(__name__)


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
        db = NTUMCSchema(NTUMC_DB_PATH)
    except Exception as err:
        getLogger().exception("Error: I need access to NTU-MC DB at: %s" % NTUMC_DB_PATH)
        return

    wn = get_wn()
    with db.ctx() as ctx, wn.ctx() as wnctx:
        sents = ctx.sent.select(where='sid >= ? and sid <= ?', values=[10000, 10999])
        # convert to texttaglib
        doc = TaggedDoc(DATA_DIR, "speckled")
        ignored_concepts = set()
        omwextra = set()
        synsets = set()
        stats = Counter()
        # import sents to tagged doc
        for sent in sents:
            tsent = doc.add_sent(sent.sent, sent.sid)  # tagged-sentence
            # import tokens
            # sid, wid, word, lemma, pos
            words = ctx.word.select(where='sid = ?', values=(sent.sid,), orderby='sid, wid')
            tsent.import_tokens(w.word for w in words)
            word_token_map = {}
            for token, word in zip(tsent.tokens, words):
                token.tag(tagtype=Token.POS, label=word.pos)
                token.tag(tagtype=Token.LEMMA, label=word.lemma)
                token.tag(tagtype='orig_wid', label=word.wid)
                word_token_map[word.wid] = token
                stats.count("Word")
            concepts = ctx.concept.select(where='sid = ?', values=(sent.sid,), orderby='sid, cid')
            # import concept
            # c.sid, c.cid, c.clemma, c.tag
            for c in concepts:
                if c.tag in ('e', 'x', 'w', 'org', 'loc', 'per', 'dat', 'oth', 'num', 'dat:year'):
                    ignored_concepts.add((c.sid, c.cid))
                    stats.count("Tag-ignored")
                    continue
                elif c.tag.startswith('!'):
                    getLogger().warning("Invalid synset format {}".format(c.tag))
                    ignored_concepts.add((c.sid, c.cid))
                    stats.count("Tag-error")
                    continue
                else:
                    ctag = c.tag.replace('=', '').strip()
                    tconcept = tsent.add_concept(c.cid, c.clemma, ctag)
                    # ensure that the concept is in PW30
                    if ctag in omwextra:
                        tconcept.comment = 'EXTRA'
                        stats.count("Tag-OMW")
                    elif ctag not in synsets:
                        ssinfo = wnctx.ss.by_id(wn.ensure_sid(ctag))
                        if not ssinfo:
                            getLogger().info("Synset not found: {} {}".format(c.tag, c.clemma))
                            omwextra.add(ctag)
                            tconcept.comment = 'EXTRA'
                            stats.count("Tag-OMW")
                        else:
                            synsets.add(ctag)
                            stats.count("Tag-PWN30")
                    else:
                        stats.count("Tag-PWN30")
            links = ctx.cwl.select(where='sid = ?', values=(sent.sid,), orderby='sid, cid, wid')
            # link concepts to words
            for link in links:
                if (link.sid, link.cid) in ignored_concepts:
                    continue
                token = word_token_map[link.wid]
                tsent.concept_map[link.cid].words.append(token)
            # write tags
            for c in tsent.concepts:
                cfrom = min(t.cfrom for t in c.words)
                cto = max(t.cto for t in c.words)
                tagtype = 'OMW' if c.comment == "EXTRA" else 'WN'
                tsent.add_tag(c.tag, cfrom, cto, tagtype=tagtype)
    doc.write_ttl()
    # raw text file
    with open(OUTPUT_FILE, 'w') as outfile:
        for sent in sents:
            outfile.write(sent.sent)
            outfile.write('\n')
    # generate test doc
    for sid in test_sids:
        sent = doc.sent_map[sid]
        testdoc.sents.append(sent)
        testdoc.sent_map[sid] = sent
    testdoc.write_ttl()
    report = TextReport()
    report.header("Extracted data has been written to:")
    report.print("Raw sentence         : %s" % (OUTPUT_FILE,))
    report.print("Raw sentence with SID: %s" % (doc.sent_path,))
    report.print("Words                : %s" % (doc.word_path,))
    report.print("Concepts             : %s" % (doc.concept_path,))
    report.print("Links                : %s" % (doc.link_path,))
    report.print("Tags                 : %s" % (doc.tag_path,))
    report.print("PWN30 concepts       : %s" % (len(synsets),))
    report.print("OMW-x concepts       : %s" % (len(omwextra),))
    report.print("MWE                  : %s" % (sum(len(s.mwe) for s in doc),))
    stats.summarise(report)
    report.print("OMW-x synsets        : {}".format(omwextra))
    report.print("Done!")
    pass


if __name__ == "__main__":
    main()
