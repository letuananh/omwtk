#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script to compare different WordNet database
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
from operator import itemgetter
from collections import namedtuple

from chirptext.leutile import Counter
from chirptext.leutile import header
from chirptext.texttaglib import writelines

from lelesk import LLConfig
from lelesk.glosswordnet import XMLGWordNet, SQLiteGWordNet
from lelesk.wordnetsql import WordNetNTUMC, WordNetSQL

########################################################################
# Configuration
########################################################################

WN_NTUMC_FILE     = os.path.abspath(os.path.expanduser('~/wordnet/wn-ntumc.db'))
WORDNET_30_PATH   = LLConfig.WORDNET_30_PATH
NTUMC_NEW_SYNSETS = os.path.abspath(os.path.expanduser('./data/ntumc_synsets.txt'))
WN30_NEW_SYNSETS  = os.path.abspath(os.path.expanduser('./data/wn30_synsets.txt'))


########################################################################


def main():
    print("Script to compare WNSQL30 to WN-NTUMC")
    wnntu = WordNetNTUMC(WN_NTUMC_FILE)
    wn30 = WordNetSQL(WORDNET_30_PATH)
    
    header("WordNet-NTUMC")
    ssntu = wnntu.get_all_synsets()
    print("Synset count: %s " % (len(ssntu),))
    for ss in ssntu[:5]:
        print(ss)
    sidntu = set([ ss.synset if not ss.synset.endswith('r') else ss.synset[:-1] + 'a' for ss in ssntu ])
    
    
    header("WordNet SQL 3.0")
    sensemap = wn30.all_senses()
    sswn30 = []
    wn30sensemap = {}
    for sses in sensemap.values():
        for ss in sses:
            sswn30.append(ss)
            wn30sensemap[ss.get_canonical_synsetid()] = ss
    print("Synset count: %s " % (len(sswn30),))
    for ss in sswn30[:5]:
        print( "%s: %s" % (ss.get_canonical_synsetid(), wn30.get_senseinfo_by_sid(ss.sid),) )
    sidwn30 = set([ ss.get_canonical_synsetid() for ss in sswn30 ])
    
    header("synsets in WNNTUMC but not in WNSQL30")
    sids = sidntu.difference(sidwn30)
    print(len(sids))
    with open(NTUMC_NEW_SYNSETS, 'w') as ntuout:
        for sid in sids:
            ntuout.write("%s: %s\n" % (sid, ' | '.join([ x._2 for x in wnntu.get_synset_def(sid) ])))
    
    header("synsets in WNSQL30 but not in WNNTUMC")
    sids = sidwn30.difference(sidntu)
    print(len(sids))
    with open(WN30_NEW_SYNSETS, 'w') as wn30out:
        for sid in sids:
            wn30out.write("%s: %s\n" % (sid, wn30sensemap[sid].gloss))
    pass

if __name__ == "__main__":
    main()
