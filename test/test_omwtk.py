#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script for testing omwtk library
Latest version can be found at https://github.com/letuananh/omwtk

References:
    Python documentation:
        https://docs.python.org/
    Python unittest
        https://docs.python.org/3/library/unittest.html
    --
    argparse module:
        https://docs.python.org/3/howto/argparse.html
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
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

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2015, omwtk"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import logging
import unittest
from chirptext import TextReport
from omwtk.prejp import romanize, gen_interlinear
from omwtk.lex2pred import EWDB, parse_lemma, is_gold
from omwtk.lex2pred import task_mine_mwe, mine_mwe, mine_mwe_nospace, mine_mwe_of, mine_mwe_extra, flag_mwe, mine_mwe_apos_s

########################################################################


def getLogger():
    return logging.getLogger(__name__)


class TestOMWTK(unittest.TestCase):

    def test_null_args(self):
        print("Dummy test")
        self.assertTrue(True)


class TestPreJP(unittest.TestCase):

    def test_romanize(self):
        print(romanize('猫がすきです。'))

    def test_gen_interlinear(self):
        print(gen_interlinear('猫がすきです。'))


class TestLex2Pred(unittest.TestCase):

    def test_ewdb(self):
        db = EWDB()
        with db.ctx() as ctx:
            senseid = db.add_sense('00001740-n', 'thing', 'n', 'something', ctx=ctx)
            self.assertIsNone(db.add_sense('00001740-n', 'thing', 'n', 'something', ctx=ctx))
            self.assertEqual(len(ctx.sense.select('flag=?', (EWDB.Flags.GOLD,))), 0)
            db.flag(senseid, EWDB.Flags.GOLD, ctx=ctx)
            db.add_map(1, '_thing_n_of', ctx=ctx)
            self.assertEqual(len(ctx.sense.select()), 1)
            self.assertEqual(len(ctx.sense.select('flag=?', (EWDB.Flags.GOLD,))), 1)

    def test_parsing(self):
        s = parse_lemma('clothes', 'n')
        getLogger().debug(s)
        for r in s:
            print(r.dmrs().layout.head())
            getLogger().debug(r.dmrs().preds())
        self.assertTrue(len(s))

    def test_is_gold(self):
        db = EWDB('data/ewmap.db')
        god = db.sense.select('lower(lemma)=?', ('god',))
        for g in god:
            print(g.lemma, g.synsetid, is_gold(g))

    def test_unique(self):
        db = EWDB('data/ewmap.db')
        with db.ctx() as ctx:
            sense = ctx.sense.by_id(2)
            sense2 = ctx.sense.by_id(2)
            self.assertEqual(sense, sense2)
            self.assertEqual(len({sense, sense2}), 1)

    def test_apos_s(self):
        db = EWDB('data/ewmap.db')
        with db.ctx() as ctx:
            mwe = mine_mwe_apos_s(db, ctx)
            print(len(mwe))

    def test_mwe(self):
        db = EWDB('data/ewmap.db')
        # task_mine_mwe(None, None, db)
        flag_mwe(None, None, db)

    def test_lexicon(self):
        db = EWDB('data/ewmap.db')
        with db.ctx() as ctx:
            lexicon = set(s.lemma for s in ctx.sense.select())
        print(len(lexicon))
        print(list(lexicon)[:5])


########################################################################

if __name__ == "__main__":
    unittest.main()
