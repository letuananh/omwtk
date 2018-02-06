#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script to convert BB-JSON to TTL
@author: Le Tuan Anh
'''

# Copyright (c) 2018, Le Tuan Anh <tuananh.ke@gmail.com>
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
__copyright__ = "Copyright 2018, OMWTK"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################

import os
import re
import json
import logging
from chirptext.leutile import TextReport, StringTool, FileHelper
from chirptext.leutile import Counter, Timer

from chirptext import texttaglib as ttl

from yawlib import YLConfig, SynsetID
from yawlib import GWordnetSQLite
from yawlib import WordnetSQL
from yawlib.omwsql import OMWSQL

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

omw = OMWSQL(YLConfig.OMW_DB)
wn30 = WordnetSQL(YLConfig.WNSQL30_PATH)
DATA_DIR = os.path.abspath('./data')


def getLogger():
    return logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------

def bb2ttl():
    infile = 'data/speckled_babelfy.json'
    speckled = ttl.Document('speckled', DATA_DIR).read()
    bb_ttl = ttl.Document('speckled_bb', DATA_DIR)
    bb = json.loads(FileHelper.read(infile))
    print("Found {} BB sentences".format(len(bb)))
    for sid, tokens in bb:
        if not speckled.has_id(sid):
            getLogger().warning("Sentence {} not found".format(sid))
        else:
            sent = speckled.get(sid)
            bb_sent = bb_ttl.new_sent(sent.text, sid)
            for t in tokens:
                cfrom = t['charFragment']['start']
                cto = t['charFragment']['end']
                bbsid = t['babelSynsetID']
                dbpedia = t['DBpediaURL']
                if bbsid.startswith('bn:'):
                    bbsid = bbsid[3:]
                bb_sent.new_tag(bbsid, cfrom, cto, tagtype='WN-BB')
                if dbpedia:
                    bb_sent.new_tag(dbpedia, cfrom, cto, tagtype='DBpedia')
    bb_ttl.write_ttl()
    pass


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    t = Timer()
    t.start("Script to convert BB to TTL")
    bb2ttl()
    t.end()


if __name__ == "__main__":
    main()
