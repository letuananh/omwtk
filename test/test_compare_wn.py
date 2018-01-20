#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test script for compare_wn
Latest version can be found at https://github.com/letuananh/omwtk

References:
    Python unittest documentation:
        https://docs.python.org/3/library/unittest.html
    Python documentation:
        https://docs.python.org/
    PEP 0008 - Style Guide for Python Code
        https://www.python.org/dev/peps/pep-0008/
    PEP 0257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2017, Le Tuan Anh <tuananh.ke@gmail.com>
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
__email__ = "<tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2017, omwtk"
__license__ = "MIT"
__maintainer__ = "Le Tuan Anh"
__version__ = "0.1"
__status__ = "Prototype"
__credits__ = []

########################################################################

import os
import unittest
from chirptext import header, TextReport
from omwtk.compare_wn import omw, gwn, wn30
from omwtk.compare_wn import SCIENTIFIC_NAME, remove_sciname, has_sciname, TAGS
from omwtk.compare_wn import read_diff_ssids, compare_synset, join_definitions
from omwtk.compare_wn import get_omw_synsets, get_gwn_synsets, get_wn30_synsets
from yawlib import SynsetID

# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(TEST_DIR, 'data')


# -------------------------------------------------------------------------------
# Test cases
# -------------------------------------------------------------------------------

class TestMainApp(unittest.TestCase):

    def test_omw(self):
        header("Ensure that OMW is working")
        omw_ssids = get_omw_synsets()
        print("OMW synsets: {}".format(len(omw_ssids)))
        print(omw_ssids[:5])

    def test_gwn(self):
        header("Ensure that GWN is working")
        gwn_ssids = get_gwn_synsets()
        print("GWN synsets: {}".format(len(gwn_ssids)))
        print(gwn_ssids[:5])

    def test_wn30(self):
        header("Ensure that PWN-3.0 is working")
        wn_ssids = get_wn30_synsets()
        print("WN synsets: {}".format(len(wn_ssids)))
        print(wn_ssids[:5])

    def test_remove_sciname(self):
        header("Test removing scientific name")
        d = 'triggerfishes ❲Balistidae❳'
        self.assertTrue(has_sciname(d))
        self.assertTrue(SCIENTIFIC_NAME.search(d))
        d_nosn = remove_sciname(d)
        expected = 'triggerfishes'
        self.assertEqual(d_nosn, expected)

    def test_detect_dup(self):
        header("Detect duplication in OMW definition")
        ss = omw.get_synset('01850676-n')
        fixed_def, dup_defs = join_definitions(ss)
        self.assertEqual(ss.definition, 'canvasback; redhead; pochard; canvasback; redhead; pochard; etc. ❲Aythya❳')
        self.assertEqual(fixed_def, 'canvasback; redhead; pochard; etc. ❲Aythya❳')
        self.assertEqual(set(dup_defs), {'canvasback', 'redhead', 'pochard'})

    def compare_gwn_wn30(self):
        header("GWN and WN30 are equal")
        # compare synset IDso
        gwn_ssids = set(get_gwn_synsets())
        wn_ssids = set(get_wn30_synsets())
        self.assertEqual(gwn_ssids, wn_ssids)

    def test_find_surface(self):
        sid = '00445467-v'
        omwss = omw.get_synset(sid)
        gwnss = gwn.get_synset(sid)
        odef_orig = '; '.join(omwss.definitions)
        odef, is_duplicated = join_definitions(omwss)
        gdef = gwnss.get_def().text()
        if gdef.endswith(";"):
            gdef = gdef[:-1].strip()
        if odef != gdef:
            header(sid)
            print("OMW-orig: {} | is_dup: {}".format(odef_orig, is_duplicated))
            print("OMW:", odef)
            print("GWN:", gdef)

    def find_token(self):
        sid = '08097766-n'
        ss = gwn.get_synset(sid)
        tokens = [x.text for x in ss.get_def().items]  # gloss.items is a list of GlossItem
        self.assertEqual(tokens, ['a', 'religious', 'sect', 'founded', 'in', 'the', 'United', 'States', 'in', '1966', ';', 'based', 'on', 'Vedic', 'scriptures', ';', 'groups', 'engage', 'in', 'joyful', 'chanting', 'of', 'Hare', 'Krishna', 'and', 'other', 'mantras', 'based', 'on', 'the', 'name', 'of', 'the', 'Hindu', 'god', 'Krishna', ';', 'devotees', 'usually', 'wear', 'saffron', 'robes', 'and', 'practice', 'vegetarianism', 'and', 'celibacy', ';'])

    def test_read_ssids(self):
        fn = 'data/omw_gwn_diff_ssids.txt'
        if not os.path.isfile(fn):
            with open(fn, 'wt') as outfile:
                outfile.write('01850676-n\n00445467-v')
        ssids = read_diff_ssids(fn)
        self.assertTrue(ssids)

    def test_compare(self):
        o = 'a simplified form of English proposed for use as an auxiliary language for international communication; devised by C. K. Ogden and I. A. Richards'
        g = 'a simplified form of English proposed for use as an auxiliary language for international communication; devised by C. K. Ogden and I. A. Richards'
        print(o == g)

    def test_compare_synset(self):
        header("Test compare synset")
        with omw.ctx() as omw_ctx, gwn.ctx() as gwn_ctx:
            ss = '01850676-n'
            tags, odef, gdef = compare_synset(omw, gwn, ss, omw_ctx, gwn_ctx)
            self.assertEqual(tags, {TAGS.SAME, TAGS.SCINAME, TAGS.REP})
            ss = '00445467-v'
            tags, odef, gdef = compare_synset(omw, gwn, ss, omw_ctx, gwn_ctx)
            self.assertEqual(tags, set())

    def test_def_dup(self):
        header("Check if a definition is not unique")
        sid = '11937102-n'
        omwss = omw.get_synset(sid)
        gwnss = gwn.get_synset(sid)
        self.assertEqual(omwss.definition, 'a variety of aster (Symphyotrichum lateriflorum)')
        self.assertEqual(gwnss.definition, 'a variety of aster;')
        glosses = gwn.gloss.select('surface = ?', (gwnss.definition,))
        ssids = {str(SynsetID.from_string(g.sid)) for g in glosses}
        self.assertEqual(ssids, {'11935627-n', '11935715-n', '11935794-n', '11935877-n', '11935953-n', '11936027-n', '11936113-n', '11936199-n', '11936287-n', '11936369-n', '11936448-n', '11936539-n', '11936624-n', '11936707-n', '11936782-n', '11936864-n', '11936946-n', '11937023-n', '11937102-n', '11937195-n', '11937278-n', '11937360-n', '11937446-n'})

    def test_get_usr(self):
        header("Test get information")
        sid = '02386612-a'
        lang = 'eng'
        defs = omw.sdef.select('synset=? and lang=?', (sid, lang))
        usrs = {d.usr for d in defs if d.usr}
        self.assertTrue(usrs)

    def test_get_mfs(self):
        words = 'we this sing full cat tongue name dry die horn sun with mountain eye belly old big red woman live head animal because cloud louse sleep ear wet know salt walk eat seed green bite say person all child count thin stand father laugh night give stone heavy if bone sister other yellow small work snake smoke kill white swim short grease worm narrow flower neck path drink flesh good sharp ash snow hot fire mouth see dirty hand egg skin cold fly wood mother come I warm where one play foot sea year new earth smooth two water what burn fish vomit bird how long hunt sit rope feather nose dust round wind tooth correct bark root ice not blood tail dull brother man heart lie liver many pig rain claw who day grass knee when leaf wide hair meat black dog star dance breasts wife sand husband You bad hear moon river tree that'.split()
        with omw.ctx() as ctx, TextReport('data/mfs1500.txt') as rp, TextReport("data/wndef.txt") as deffile:
            query = 'wordid in (SELECT wordid FROM word WHERE lemma in {})'.format(repr(tuple(words)))
            rows = ctx.sense.select(query)
            ssids = [SynsetID.from_string(r.synset) for r in rows]
            for ssid in ssids:
                ss = omw.get_synset(ssid, ctx=ctx)
                if ss.lemmas and ss.definition:
                    rp.print("{id} ({lm}): {df}".format(id=ss.ID, lm=", ".join(ss.lemmas), df=ss.definition.strip()))
                    deffile.print(ss.definition.strip())
        print("Done!")


def normalize(txt):
    return txt.strip().replace("'", "").replace('-', ' ')


# -------------------------------------------------------------------------------
# Main method
# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
