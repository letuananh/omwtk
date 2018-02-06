#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
WN Lemma to ERG predicates
Latest version can be found at https://github.com/letuananh/omwtk

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
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
import re
import logging
import json
import random
import codecs
import csv
from collections import OrderedDict
from collections import namedtuple
from collections import defaultdict as dd
from lxml import etree

from puchikarui import Schema, with_ctx
from coolisf import GrammarHub
from chirptext.leutile import grouper
from chirptext.io import CSV
from chirptext import TextReport, FileHelper, Counter, FileHub
from chirptext.cli import CLIApp, setup_logging
from yawlib.helpers import get_gwn
from yawlib.helpers import get_wn, get_omw

# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

DATA_FOLDER = os.path.abspath(os.path.expanduser('./data'))
omw = get_omw()
gwn = get_gwn()
wn = get_wn()
setup_logging('logging.json', 'logs')
ghub = GrammarHub()
MY_DIR = os.path.dirname(__file__)
SETUP_FILE = os.path.join(MY_DIR, 'scripts', 'ewdb.sql')
ROOTS = {'n': 'root_wn_n',
         'v': 'root_wn_v',
         'a': 'root_wn_adj',
         'r': ''}
DEFAULT_DB_PATH = FileHelper.abspath('data/ewmap.db')


class EWDB(Schema):

    class Flags:
        PROCESSED = 1
        NO_PARSE = 2
        MWE = 3
        MWE_PURE = 100
        MWE_NOSPACE = 101
        MWE_OF = 102
        MWE_APOS_S = 103
        MWE_EXTRA = 199
        GOLD_CARG = 998
        GOLD = 999

    def __init__(self, data_source=":memory:", setup_script=None, setup_file=None):
        super().__init__(data_source, setup_script=setup_script, setup_file=setup_file)
        self.add_file(SETUP_FILE)
        # tables
        self.add_table('sense', ['ID', 'synsetid', 'lemma', 'pos', 'definition', 'flag', 'mwe'], id_cols=('ID',))
        self.add_table('pred', ['senseID', 'pred'], id_cols=('senseID', 'pred'))
        self.add_table('flag', ['ID', 'text', 'description'], id_cols=('ID',))

    @with_ctx
    def add_sense(self, synsetid, lemma, pos, definition, flag=None, ctx=None):
        if ctx.sense.select_single("synsetid=? AND lemma=?", (synsetid, lemma)):
            getLogger().warning("Sense {}-{} exists.".format(synsetid, lemma))
            return None
        else:
            return ctx.sense.insert(synsetid, lemma, pos, definition, flag)

    @with_ctx
    def flag_sense(self, ID, flag, ctx=None):
        ctx.sense.update(columns=('flag',), new_values=(flag,), where="ID=?", where_values=(ID,))

    @with_ctx
    def mwe(self, ID, mwe_flag, ctx=None):
        ctx.sense.update(columns=('mwe',), new_values=(mwe_flag,), where="ID=?", where_values=(ID,))

    @with_ctx
    def flag_many(self, flag, *IDs, ctx=None):
        batches = grouper(IDs, 900)
        for batch in batches:
            current_ids = tuple(i for i in batch if i)
            query = "ID in ({})".format(', '.join(["?"] * len(current_ids)))
            ctx.sense.update(columns=('flag',), new_values=(flag,), where=query, where_values=current_ids)

    @with_ctx
    def mwe_many(self, mwe_flag, *IDs, ctx=None):
        batches = grouper(IDs, 900)
        for batch in batches:
            current_ids = tuple(i for i in batch if i)
            query = "ID in ({})".format(', '.join(["?"] * len(current_ids)))
            ctx.sense.update(columns=('mwe',), new_values=(mwe_flag,), where=query, where_values=current_ids)

    @with_ctx
    def add_map(self, senseID, pred, ctx=None):
        if ctx.pred.select_single('senseID=? AND pred=?', (senseID, pred)):
            getLogger().debug("Mapping exists {} => {}".format(senseID, pred))
        else:
            ctx.pred.insert(senseID, pred)


def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Data structures
# -------------------------------------------------------------------------------

def iter_tsv(file_path):
    with open(file_path, 'r') as infile:
        reader = csv.reader(infile, dialect='excel-tab')
        for row in reader:
            yield row


# -------------------------------------------------------------------------------
# Application logic
# -------------------------------------------------------------------------------


def create_ewdb(cli, args):
    db = EWDB(args.db)
    c = Counter()
    rp = TextReport()
    rp.header("DB location: {}".format(db.ds.path))
    with db.ctx() as ctx:
        for pos in 'nvar':
            file_name = 'data/tsdb/skeletons/omw_{}.txt'.format(pos)
            rp.print("Reading file: {}".format(file_name))
            for idx, row in enumerate(iter_tsv(file_name)):
                lemma, sid, sdef = row
                db.add_sense(sid, lemma, pos, sdef, ctx=ctx)
                c.count("Added")
    c.summarise()
    pass


def show_stats(cli, args):
    db = EWDB(args.db)
    rp = TextReport()
    rp.header("DB location: {}".format(db.ds.path))
    with db.ctx() as ctx:
        for pos in 'nvar':
            senses = ctx.sense.select("pos=?", (pos,))
            print("pos={}: {}".format(pos, len(senses)))
            senses = ctx.sense.select("pos=? AND flag=?", (pos, EWDB.Flags.GOLD))
            print("GOLD pos={}: {}".format(pos, len(senses)))
    pass


def get_lexicon(ctx):
    lexicon = set(s.lemma for s in ctx.sense.select(columns=('lemma',)))
    capitalized = set(l.capitalize() for l in lexicon)
    return lexicon.union(capitalized)


def mine_mwe(db, ctx):
    lexicon = get_lexicon(ctx)
    potentials = ctx.sense.select("""(lemma like '%-%') or (lemma like '% %')""")
    mwe = list()
    for potential in potentials:
        is_mwe = True
        parts = potential.lemma.split()
        for part in parts:
            if part not in lexicon:
                is_mwe = False
        if is_mwe:
            mwe.append(potential)
    return mwe


OF_PARTS = ('of', 'the', 'a')


def mine_mwe_of(db, ctx):
    lexicon = get_lexicon(ctx)
    potentials = ctx.sense.select("""(lemma like '%-%') or (lemma like '% %')""")
    mwe = list()
    for potential in potentials:
        is_mwe = True
        parts = potential.lemma.split()
        if 'of' not in parts:
            continue
        for part in parts:
            if part not in OF_PARTS and part not in lexicon:
                is_mwe = False
        if is_mwe:
            mwe.append(potential)
    return mwe


def mine_mwe_apos_s(db, ctx):
    lexicon = get_lexicon(ctx)
    potentials = ctx.sense.select("""((lemma like '%-%') or (lemma like '% %')) AND (lemma like'%''s ' OR lemma like '%s'' %')""")
    mwe = list()
    for potential in potentials:
        is_mwe = True
        parts = potential.lemma.split()
        for part in parts:
            if part != 'the' and not part.endswith("'s") and not part.endswith("s'") and part not in lexicon:
                is_mwe = False
        if is_mwe:
            mwe.append(potential)
    return mwe


def mine_mwe_extra(db, ctx):
    lexicon = get_lexicon(ctx)
    potentials = ctx.sense.select("""(lemma like '%-%') or (lemma like '% %')""")
    mwe = list()
    for potential in potentials:
        is_mwe = True
        parts = potential.lemma.split()
        for part in parts:
            if part not in OF_PARTS and part not in lexicon:
                is_mwe = False
        # another type of MWE
        if not is_mwe:
            mwe.append(potential)
    return mwe


def mine_mwe_nospace(db, ctx, senses=None):
    if not senses:
        senses = mine_mwe(db, ctx)
    no_spaces = set()
    for sense in senses:
        lemma_nospace = sense.lemma.replace(' ', '').replace('-', '')
        no_spaces.update(ctx.sense.select('lemma = ?', (lemma_nospace,)))
    return no_spaces


def task_mine_mwe(cli, args, db=None):
    if db is None:
        db = EWDB(args.db)
    with db.ctx() as ctx:
        with TextReport('data/mwe_extra.txt') as outfile_extra:
            senses_extra = mine_mwe_extra(db, ctx)
            for sense in senses_extra:
                outfile_extra.print(sense.lemma)
        with TextReport('data/mwe.txt', 'w') as outfile:
            senses = mine_mwe(db, ctx)
            for sense in senses:
                outfile.print(sense.lemma)
        with TextReport('data/mwe_nospace.txt', 'w') as outfile_nospace:
            nospaces = mine_mwe_nospace(db, ctx, senses)
            for sense in nospaces:
                outfile_nospace.print(sense.lemma)
        with TextReport('data/mwe_of.txt') as outfile_of:
            senses_of = mine_mwe_of(db, ctx)
            for sense in senses_of:
                outfile_of.print(sense.lemma)
        with TextReport('data/mwe_apos_s.txt') as outfile_apos_s:
            senses_apos_s = mine_mwe_apos_s(db, ctx)
            for sense in senses_apos_s:
                outfile_apos_s.print(sense.lemma)
        # report
        getLogger().debug("Found MWE: {}".format(len(senses)))
        getLogger().debug("Found MWE-of: {}".format(len(senses_of)))
        getLogger().debug("No space: {}".format(len(nospaces)))
        getLogger().debug("Extra: {}".format(len(senses_extra)))


def flag_mwe(cli, args, db=None):
    if db is None:
        db = EWDB(args.db)
    with db.ctx() as ctx:
        # flag best MWE
        getLogger().info("Processing MWE_PURE")
        senses = mine_mwe(db, ctx)
        not_gold = [s.ID for s in senses if s.flag != EWDB.Flags.GOLD]
        db.flag_many(EWDB.Flags.MWE, *not_gold, ctx=ctx)
        not_pure = [s.ID for s in senses if s.mwe != EWDB.Flags.MWE_PURE]
        db.mwe_many(EWDB.Flags.MWE_PURE, *not_pure, ctx=ctx)

        # flag MWE nospace
        getLogger().info("Processing MWE_NOSPACE")
        senses_nospace = mine_mwe_nospace(db, ctx, senses)
        not_gold = [s.ID for s in senses_nospace if s.flag != EWDB.Flags.GOLD]
        db.flag_many(EWDB.Flags.MWE, *not_gold, ctx=ctx)
        not_nospace = [s.ID for s in senses_nospace if s.mwe != EWDB.Flags.MWE_NOSPACE]
        db.mwe_many(EWDB.Flags.MWE_NOSPACE, *not_nospace, ctx=ctx)

        # flag extra
        getLogger().info("Processing MWE_EXTRA")
        senses_extra = mine_mwe_extra(db, ctx)
        not_gold = [s.ID for s in senses_extra if s.flag != EWDB.Flags.GOLD]
        db.flag_many(EWDB.Flags.MWE, *not_gold, ctx=ctx)
        not_extra = [s.ID for s in senses_extra if s.mwe != EWDB.Flags.MWE_EXTRA]
        db.mwe_many(EWDB.Flags.MWE_EXTRA, *not_extra, ctx=ctx)

        # flag MWE of
        getLogger().info("Processing MWE_OF")
        senses_of = mine_mwe_of(db, ctx)
        not_gold = [s.ID for s in senses_of if s.flag != EWDB.Flags.GOLD]
        db.flag_many(EWDB.Flags.MWE, *not_gold, ctx=ctx)
        not_of = [s.ID for s in senses_of if s.mwe != EWDB.Flags.MWE_OF]
        db.mwe_many(EWDB.Flags.MWE_OF, *not_of, ctx=ctx)

        # flag MWE apos_s
        getLogger().info("Processing MWE_APOS_S")
        senses_apos_s = mine_mwe_apos_s(db, ctx)
        not_gold = [s.ID for s in senses_apos_s if s.flag != EWDB.Flags.GOLD]
        db.flag_many(EWDB.Flags.MWE, *not_gold, ctx=ctx)
        not_apos_s = [s.ID for s in senses_apos_s if s.mwe != EWDB.Flags.MWE_APOS_S]
        db.mwe_many(EWDB.Flags.MWE_APOS_S, *not_apos_s, ctx=ctx)
        print(len(senses_apos_s))


def find_mwe(lemma, db, ctx):
    ptn1 = '{}%'.format(lemma)
    ptn2 = '%{}'.format(lemma)
    return ctx.sense.select('(lemma like ? OR lemma like ?) AND lemma != ?', (ptn1, ptn2, lemma))


def parse_lemma(lemma, pos):
    if pos and ROOTS[pos]:
            extra_args = ['-r', ROOTS[pos]]
    else:
        extra_args = None
    s = ghub.ERG.parse(lemma, extra_args=extra_args)
    return s


def match_lemma(node, lemma):
    if node is not None:
        if node.pred.lemma == lemma:
            return EWDB.Flags.GOLD
        elif node.carg == lemma:
            return EWDB.Flags.GOLD_CARG
    return 0


def is_gold(sense, db=None, ctx=None):
    s = parse_lemma(sense.lemma, sense.pos)
    is_gold = 0
    if not len(s):
        if db is not None:
            # mark as 2
            db.flag_sense(sense.ID, EWDB.Flags.NO_PARSE, ctx=ctx)
            return False
    for r in s:
        head = r.dmrs().layout.head()
        if not head:
            preds = [node for node in r.dmrs().layout.nodes if not node.is_udef()]
            if len(preds) == 1:
                head = preds[0]
        local_match = match_lemma(head, sense.lemma)
        if local_match:
            # add pred
            if db is not None:
                # map this sense to a pred
                db.add_map(sense.ID, str(head.pred), ctx=ctx)
            is_gold = local_match
    return is_gold


def process_lemma(cli, args):
    limit = int(args.topk) if args.topk and int(args.topk) > 0 else None
    pos = args.pos
    db = EWDB(args.db)
    rp = TextReport()
    rp.header("DB location: {}".format(db.ds.path))
    with db.ctx() as ctx:
        if args.flag:
            query = ['(flag IS NULL OR flag = ?)']
            params = [args.flag]
        else:
            query = ['flag IS NULL']
            params = []
        if pos:
            query.append('pos=?')
            params.append(pos)
        senses = ctx.sense.select(' AND '.join(query), params, limit=limit)
        print("Found {} senses for {}".format(len(senses), pos))
        for idx, sense in enumerate(senses):
            if idx % 50 == 0:
                print("Processed {} / {}".format(idx, len(senses)))
            found_gold = is_gold(sense, db, ctx)  # non zero = True
            if found_gold:
                # flag this sense as gold
                db.flag_sense(sense.ID, found_gold, ctx=ctx)
            elif sense.flag != EWDB.Flags.PROCESSED:
                db.flag_sense(sense.ID, EWDB.Flags.PROCESSED, ctx=ctx)
    pass


# -------------------------------------------------------------------------------
# Main method
# -------------------------------------------------------------------------------

def main():
    ''' Various tools for extracting Wordnets '''
    app = CLIApp(desc='OMW patching tools', logger=__name__)
    # omw2txt
    task = app.add_task('makedb', func=create_ewdb)
    task.add_argument('db', help='Path to DB file', nargs="?", default=DEFAULT_DB_PATH)

    task = app.add_task('stat', func=show_stats)
    task.add_argument('db', help='Path to DB file', nargs="?", default=DEFAULT_DB_PATH)

    task = app.add_task('proc', func=process_lemma)
    task.add_argument('db', help='Path to DB file', nargs="?", default=DEFAULT_DB_PATH)
    task.add_argument('-n', '--topk', help='Limit top n')
    task.add_argument('-p', '--pos', help='POS', default=None)
    task.add_argument('-f', '--flag', help='Flag to be processed', default=None)

    task = app.add_task('mwe', func=flag_mwe)
    task.add_argument('db', help='Path to DB file', nargs="?", default=DEFAULT_DB_PATH)
    # run app
    app.run()


if __name__ == "__main__":
    main()
