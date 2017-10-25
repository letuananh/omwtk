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
from chirptext import header
from omwtk.compare_wn import omw, gwn, wn30
from omwtk.compare_wn import SCIENTIFIC_NAME, remove_sciname
from omwtk.compare_wn import get_omw_synsets, get_gwn_synsets, get_wn30_synsets

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
        omw_ssids = get_omw_synsets()
        print("OMW synsets: {}".format(len(omw_ssids)))
        print(omw_ssids[:5])

    def test_gwn(self):
        gwn_ssids = get_gwn_synsets()
        print("GWN synsets: {}".format(len(gwn_ssids)))
        print(gwn_ssids[:5])

    def test_wn30(self):
        wn_ssids = get_wn30_synsets()
        print("WN synsets: {}".format(len(wn_ssids)))
        print(wn_ssids[:5])

    def test_remove_sciname(self):
        d = 'triggerfishes ❲Balistidae❳'
        self.assertTrue(SCIENTIFIC_NAME.search(d))
        d_nosn = remove_sciname(d)
        expected = 'triggerfishes'
        self.assertEqual(d_nosn, expected)

    def compare_gwn_wn30(self):
        print("Make sure that GWN and WN30 are equal")
        # compare synset IDs
        gwn_ssids = set(get_gwn_synsets())
        wn_ssids = set(get_wn30_synsets())
        self.assertEqual(gwn_ssids, wn_ssids)

    def compare_gwn_omw(self):
        omw_ssids = set(get_omw_synsets())
        gwn_ssids = set(get_gwn_synsets())
        omw_new = omw_ssids - gwn_ssids
        gwn_new = gwn_ssids - omw_ssids
        print("OMW new synsets:", len(omw_new))
        print("GWN new synsets:", len(gwn_new))

    def test_find_surface(self):
        sid = 'a00998674'
        omwss = omw.get_synset(sid)
        gwnss = gwn.get_synset(sid)
        odef = "; ".join(omwss.definitions)
        gdef = gwnss.get_def().text()
        if gdef.endswith(";"):
            gdef = gdef[:-1].strip()
        if odef != gdef:
            header(sid)
            print("OMW:", odef)
            print("GWN:", gdef)

    def find_token(self):
        sid = '08097766-n'
        ss = gwn.get_synset(sid)
        print(ss.get_def().items)


def normalize(txt):
    return txt.strip().replace("'", "").replace('-', ' ')


# -------------------------------------------------------------------------------
# Main method
# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
