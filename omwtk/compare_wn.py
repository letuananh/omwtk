#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script to compare different WordNet database
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
import re
from operator import itemgetter
from collections import namedtuple

from chirptext.leutile import Counter, TextReport, StringTool
from chirptext.leutile import header

from yawlib import YLConfig, SynsetID
from yawlib import GWordnetSQLite
from yawlib import WordnetSQL
from yawlib.omwsql import OMWSQL

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

omw = OMWSQL(YLConfig.OMW_DB)
gwn = GWordnetSQLite(YLConfig.GWN30_DB)
wn30 = WordnetSQL(YLConfig.WNSQL30_PATH)


# ---------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------

def get_omw_synsets():
    omw_ss = omw.sense.select()
    omw_ssids = set()
    for x in omw_ss:
        try:
            omw_ssids.add(SynsetID.from_string(x.synset))
        except:
            print(x)
    return list(omw_ssids)


def get_gwn_synsets():
    gwn_ss = gwn.all_synsets(deep_select=False)
    return [SynsetID.from_string(x.ID) for x in gwn_ss]


def get_wn30_synsets():
    wn_ss = wn30.schema.ss.select()
    wn_ssids = [SynsetID.from_string(x.synsetid) for x in wn_ss]
    return wn_ssids


def count_synsets():
    # OMW
    omw_ssids = get_omw_synsets()
    print("OMW synsets: {}".format(len(omw_ssids)))
    print(omw_ssids[:5])

    # Glosstag corpus
    gwn_ssids = get_gwn_synsets()
    print("GWN synsets: {}".format(len(gwn_ssids)))
    print(gwn_ssids[:5])

    # Princeton WN 3.0
    wn_ssids = get_wn30_synsets()
    print("WN synsets: {}".format(len(wn_ssids)))
    print(wn_ssids[:5])


def omw_vs_gwn():
    rp = TextReport("data/omw_new.txt")
    omw_ssids = set(get_omw_synsets())
    gwn_ssids = set(get_gwn_synsets())
    omw_new = omw_ssids - gwn_ssids
    for ss in omw_new:
        s = omw.get_synset(ss)
        lemma = s.lemma if s.lemma else "** no lex **"
        if len(s.definitions) == 0:
            rp.print(join("\t", s.ID, lemma, "** no def **"))
        elif len(s.definitions) == 1:
            rp.print(join("\t", s.ID, lemma, s.definition))
        else:
            rp.print(join("\t", s.ID, lemma, s.definitions[0]))
            for d in s.definitions[1:]:
                rp.print("\t\t" + d)


SCIENTIFIC_NAME = re.compile('❲.+❳')


def remove_sciname(a_def):
    return SCIENTIFIC_NAME.sub('', a_def).strip()


def omw_vs_gwn_def():
    rp = TextReport("data/omw_gwn_defs.txt")
    rpdiff = TextReport("data/omw_gwn_defs_diff.txt")
    rpsn = TextReport("data/omw_gwn_defs_sciname.txt")
    omw_ssids = set(get_omw_synsets())
    gwn_ssids = set(get_gwn_synsets())
    omw_old = omw_ssids.intersection(gwn_ssids)
    c = Counter()
    for ss in list(omw_old):
        c.count("total")
        omwss = omw.get_synset(ss)
        gwnss = gwn.get_synset(ss)
        odef = "; ".join(omwss.definitions)
        try:
            gwnss.match_surface()
        except:
            pass
        gdef = gwnss.get_def().surface.replace('  ', ' ')
        if gdef.endswith(";"):
            gdef = gdef[:-1].strip()
        if odef != gdef:
            # try to remove scientific name ...
            odef_nosn = remove_sciname(odef)
            if odef_nosn == gdef:
                c.count("sciname")
                rp.header("[SCINAME] {}".format(ss))
                rp.print("OMW: {}".format(odef))
                rp.print("GWN: {}".format(gdef))
                rpsn.header("[SCINAME] {}".format(ss))
                rpsn.print("OMW: {}".format(odef))
                rpsn.print("GWN: {}".format(gdef))
            else:
                c.count("different")
                rp.header("[DIFF] {}".format(ss))
                rp.print("OMW: {}".format(odef))
                rp.print("GWN: {}".format(gdef))
                rpdiff.header("[DIFF] {}".format(ss))
                rpdiff.print("OMW: {}".format(odef))
                rpdiff.print("GWN: {}".format(gdef))
        else:
            c.count("same")
    # done
    c.summarise(report=rp)


def join(token, *items):
    return token.join((StringTool.to_str(x) for x in items))


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    print("Script to compare WNSQL30 to OMW")
    omw_vs_gwn_def()


if __name__ == "__main__":
    main()
