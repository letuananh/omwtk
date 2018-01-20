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
from chirptext.leutile import TextReport, StringTool
from chirptext.leutile import Counter, Timer

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
ssid_filepath = 'data/ssids.txt'


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
    gwn_ss = gwn.synset.select(columns=('ID',))
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


def has_sciname(a_def):
    s = SCIENTIFIC_NAME.search(a_def)
    return s is not None


def remove_sciname(a_def):
    return SCIENTIFIC_NAME.sub('', a_def).strip()


def read_diff_ssids(filepath=ssid_filepath):
    if not os.path.isfile(filepath):
        return None
    with open(filepath) as ssid_file:
        return [x.strip() for x in ssid_file.readlines()]


def fix_typo(a_def):
    return a_def.replace(' ,', ',').replace(' )', ')')


def join_definitions(ss):
    ''' Join definitions and detect any duplication '''
    if len(ss.definitions) == 0:
        return '', []
    duplicated_entries = []
    longest = ss.definitions[0]
    for d in ss.definitions[1:]:
        if len(d) > len(longest):
            longest = d
    # remove duplicated entries
    final = []
    for d in ss.definitions:
        if d != longest and d + ';' in longest:
            duplicated_entries.append(d)
        else:
            final.append(d)
    # join definitions and return
    definition = '; '.join(final)
    return definition, duplicated_entries


def compare_synset(omw, gwn, ss, omw_ctx=None, gwn_ctx=None):
    omwss = omw.get_synset(ss, ctx=omw_ctx)
    gwnss = gwn.get_synset(ss, ctx=gwn_ctx)
    tags = set()
    # normalize GWN definition
    try:
        gwnss.match_surface()
    except:
        pass
    gdef = gwnss.get_def().surface.replace('  ', ' ')
    if gdef.endswith(";"):
        gdef = gdef[:-1].strip()
    # join OMW definitions into one
    odef, dup_defs = join_definitions(omwss)
    if dup_defs:
        tags.add(TAGS.REP)
    if odef != gdef:
        if has_sciname(odef):
            tags.add(TAGS.SCINAME)
            # remove scientific name before continue
            odef = remove_sciname(odef)
        # FIX typo
        fixed = fix_typo(odef)
        if odef != fixed:
            tags.add(TAGS.TYPO)
            odef = fixed
        # final check
        if gdef != odef:
            tags.add(TAGS.DIFF)
        else:
            tags.add(TAGS.SAME)
    return tags, odef, gdef


class TAGS:
    '''** Tags
    - DUP :: Synsets with non-unique definitions
    - REP :: Duplicated definitions that were inserted by a Python script
    - SCINAME :: Synsets with scientific names in definitions
    - TYPO :: Extra spaces or something like that, apparently this must be zero.
    - OMW :: Changed by OMW team for some unknown reason
    - DIFF :: Synsets that are changed by NTU
    - SAME :: Synsets that are not changed (but typo/sciname may still be inserted)
    - IDENT :: Identical to PWN
    '''
    DUP = "dup"
    REP = "rep"
    SCINAME = "sciname"
    TYPO = "typo"
    OMW = "omw"
    DIFF = "diff"
    SAME = "same"
    IDENT = "ident"

    ORDER = [OMW, DUP, REP, SCINAME, TYPO, DIFF, SAME, IDENT]


def omw_vs_gwn_def():
    rp = TextReport("data/omw_gwn_report.txt")
    rpdiff = TextReport("data/omw_gwn_diff.txt")
    rptypo = TextReport("data/omw_gwn_typo.txt")
    rpsn = TextReport("data/omw_gwn_sciname.txt")
    c = Counter(TAGS.ORDER)

    # ssids to compare
    diff_ssids = []
    ssids = read_diff_ssids()
    if not ssids:
        print("Generating synset ID list")
        omw_ssids = set(get_omw_synsets())
        gwn_ssids = set(get_gwn_synsets())
        # only care about old GWN synsets
        ssids = omw_ssids.intersection(gwn_ssids)
    else:
        print("Comparing {} synsets loaded from {}".format(len(ssids), ssid_filepath))
    lang = 'eng'
    with omw.ctx() as omw_ctx, gwn.ctx() as gwn_ctx:
        print("Comparing {} synsets".format(len(ssids)))
        for ss in list(ssids):
            ss = str(ss)
            c.count("total")
            tags, odef, gdef = compare_synset(omw, gwn, ss, omw_ctx, gwn_ctx)
            omwss = omw.get_synset(ss, ctx=omw_ctx)
            tags_str = ' '.join('[{}]'.format(t.upper()) for t in tags)
            if TAGS.DIFF in tags:
                diff_ssids.append(ss)
                # [FCB] why did we change?
                gwnss = gwn.get_synset(ss, ctx=gwn_ctx)
                glosses = gwn_ctx.gloss.select('surface = ?', (gwnss.definition,))
                if glosses and len(glosses) > 1:
                    tags.add(TAGS.DUP)
                    ssids = [str(SynsetID.from_string(g.sid)) for g in glosses]
                    reason = "Not unique (Shared among {}) so OMW team changed it".format(' '.join(ssids))
                else:
                    tags.add(TAGS.OMW)
                    defs = omw.sdef.select('synset=? and lang=?', (ss, lang))
                    usrs = {d.usr for d in defs if d.usr}
                    usrs_str = ', '.join(usrs) if usrs else "someone in NTU"
                    reason = "{} made this change.".format(usrs_str)
                tags_str = ' '.join('[{}]'.format(t.upper()) for t in tags)
                rpdiff.header("{} {}".format(tags_str, ss))
                rpdiff.print("OMW: {}".format(omwss.definition))
                rpdiff.print("GWN: {}".format(gdef))
                rpdiff.print("Reason: {}".format(reason))
            if TAGS.SCINAME in tags:
                rpsn.header("{} {}".format(tags_str, ss))
                rpsn.print("OMW: {}".format(omwss.definition))
                rpsn.print("GWN: {}".format(gdef))
            if TAGS.REP in tags or TAGS.TYPO in tags:
                rptypo.header("{} {}".format(tags_str, ss))
                rptypo.print("OMW: {}".format(omwss.definition))
                rptypo.print("GWN: {}".format(gdef))
            # master report
            for tag in tags:
                c.count(tag)
            if not tags:
                c.count(TAGS.IDENT)
            rp.header("{} {}".format(tags_str, ss))
            rp.print("OMW: {}".format(omwss.definition))
            rp.print("GWN: {}".format(gdef))

    # done
    c.summarise(report=rp)
    with open('data/omw_gwn_diff_ssids.txt', 'wt') as diff_ssid_file:
        for ss in diff_ssids:
            diff_ssid_file.write('{}\n'.format(ss))


def join(token, *items):
    return token.join((StringTool.to_str(x) for x in items))


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    print("Script to compare WNSQL30 to OMW")
    t = Timer()
    t.start("Compare OMW to GWN")
    omw_vs_gwn_def()
    t.end()


if __name__ == "__main__":
    main()
