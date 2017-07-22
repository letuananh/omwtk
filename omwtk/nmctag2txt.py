#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
NTU-MC annotation extraction
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
__credits__ = []
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
from yawlib import SynsetID

########################################################################


NTUMC_DB_PATH = os.path.expanduser('./data/eng.db')
OUTPUT_FILE = os.path.expanduser('./data/speckled_tags_gold.txt')

########################################################################


class NTUMCSchema(Schema):
    def __init__(self, data_source=None):
        Schema.__init__(self, data_source)
        self.add_table('sent', 'sid docID pid sent comment usrname'.split())
        self.add_table('word', 'sid wid word pos lemma cfrom cto comment usrname'.split())
        self.add_table('concept', 'sid  wid word pos lemma cfrom cto comment usrname'.split())


def main():
    print("NTU-MC annotation extraction")
    # Reading concepts
    try:
        print("Reading NTU-MC data from: %s" % (NTUMC_DB_PATH,))
        db = NTUMCSchema.connect(NTUMC_DB_PATH)
    except Exception as err:
        print("Error: I need access to NTU-MC DB at: %s" % NTUMC_DB_PATH)
        return

    query = """
SELECT cwl.sid, cwl.wid, cwl.cid, concept.tag, word.cfrom, word.cto, concept.clemma, word.pos 
FROM cwl 
        LEFT JOIN concept on cwl.sid = concept.sid and cwl.cid = concept.cid 
        LEFT JOIN word on cwl.sid = word.sid and cwl.wid = word.wid 
WHERE
cwl.sid >= ? and cwl.sid < ?
and concept.tag NOT IN ('e', 'x', 'w', 'org', 'loc', 'per', 'dat', 'oth', 'num', 'dat:year')
;
    """
    results = [x for x in db.ds().execute(query, params=(10000, 11000))]
    print("Found %s tags" % (len(results),))

    # select mwe
    mwe_query = """SELECT c.sid, c.cid, count(*)
FROM concept as c LEFT JOIN cwl ON c.sid = cwl.sid AND c.cid = cwl.cid
WHERE c.sid >= ? and c.sid < ?
GROUP BY c.sid, c.cid
HAVING count(*) > 1;"""
    mwe = [x for x in db.ds().execute(mwe_query, params=(10000, 11000))]
    mwe_map = {}
    for sid, cid, wc in mwe:
        mwe_map[(sid, cid)] = wc
    # write down tag
    with open(OUTPUT_FILE, 'w') as tag_file:
        sids = []
        sid_map = dd(list)
        sid_cid_map = {}
        for (sid, wid, cid, tag, cfrom, cto, clemma, pos) in results:
            if tag[0] in '=!':
                tag = tag[1:]
            tag = str(SynsetID.from_string(tag))
            if sid not in sids:
                sids.append(sid)
            concept = [sid, cfrom, cto, tag, clemma, pos]
            # not seen
            if (sid, cid) not in sid_cid_map:
                # add concept
                sid_map[sid].append(concept)
                sid_cid_map[(sid, cid)] = concept
            else:
                # mwe
                sid_cid_map[(sid, cid)][1] = min(sid_cid_map[(sid, cid)][1], cfrom)
                sid_cid_map[(sid, cid)][2] = max(sid_cid_map[(sid, cid)][2], cto)
        # write tags to file
        for sid in sids:
            for c in sid_map[sid]:
                tag_file.write('\t'.join([str(x) for x in c]) + '\n')
    print("Annotation data has been saved to %s" % (OUTPUT_FILE,))
    print("All done!")


if __name__ == "__main__":
    main()
