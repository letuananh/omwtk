#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Wordnet extracting tools
Latest version can be found at https://github.com/letuananh/omwtk

References:
    Python documentation:
        https://docs.python.org/
    PEP 0008 - Style Guide for Python Code
        https://www.python.org/dev/peps/pep-0008/
    PEP 257 - Python Docstring Conventions:
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
import re
import logging
import yaml
import random
from collections import OrderedDict
from collections import namedtuple
from lxml import etree

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


def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Data structures
# -------------------------------------------------------------------------------

# -------------------------------------------------------------------------------
# Application logic
# -------------------------------------------------------------------------------

def topk_mfs(k=3000):
    with omw.ctx() as ctx:
        query = '''SELECT sense.synset FROM sense
        LEFT JOIN synset_def
        ON sense.synset = synset_def.synset
        AND sense.lang = synset_def.lang
        WHERE sense.lang = 'eng'
        ORDER BY freq DESC
        LIMIT ?'''
        result = ctx.execute(query, params=(k,))
        topk_synsets = set(x['synset'] for x in result)
    return topk_synsets


def verify_mfs(cli, args):
        top3000 = topk_mfs(3000)
        from omwtk.wn_ntumc_top3000 import WN_NTUMC_TOP3000
        first_round = set(x['synset'] for x in WN_NTUMC_TOP3000)
        print(top3000 == first_round)


def gen_mfs_5000(cli, args):
    rp = TextReport(args.output)
    from omwtk.wn_ntumc_top3000 import WN_NTUMC_TOP3000
    first_round = set(x['synset'] for x in WN_NTUMC_TOP3000)
    top5000 = topk_mfs(5000)
    round2 = list(top5000.difference(first_round))
    random.shuffle(round2)
    with FileHub(working_dir='data', default_mode='w') as hub, omw.ctx() as ctx:
        filename = 'omw5000A'
        for idx, sid in enumerate(round2):
            ss = omw.get_synset(sid, ctx=ctx)
            if idx > 200:
                filename = 'omw5000B'
            hub['omw5000'].header(ss.ID, 'lemmas: {}'.format(", ".join(ss.lemmas)))
            for d in ss.definitions:
                hub[filename].writeline(d)
                hub['omw5000'].print(d, level=1)
        rp.header("Generated files")
        for f in hub.files.keys():
            rp.print(hub[f].path)


def read_lines(file_path):
    with open(file_path) as infile:
        return infile.read().splitlines()


def gen_mfs_5500(cli, args):
    ''' Generate 3rd round tree banking '''
    rp = TextReport(args.output)
    topk_synsets = topk_mfs(5500)
    # finished treebanking
    first_round = read_lines('data/omw3000_synsets.txt')
    second_round = read_lines('data/omw5000_synsets.txt')
    done_synsets = set(first_round + second_round)
    # new
    third_round = topk_synsets.difference(done_synsets)
    # report
    print("All     :", len(topk_synsets))
    print("Done    :", len(done_synsets))
    print("New     :", len(third_round))
    # write to a synset file
    with open('data/omw5300_synsets.txt', 'w') as outfile:
        outfile.write('\n'.join(third_round))
    with FileHub(working_dir='data', default_mode='w') as hub, omw.ctx() as ctx:
        profile = 'omw5300'
        filename = 'omw5300A'
        for idx, sid in enumerate(third_round):
            ss = omw.get_synset(sid, ctx=ctx)
            hub[profile].header(ss.ID, 'lemmas: {}'.format(", ".join(ss.lemmas)))
            for d in ss.definitions:
                hub[filename].writeline(d)
                hub[profile].print(d, level=1)
        rp.header("Generated files")
        for f in hub.files.keys():
            rp.print(hub[f].path)


def gen_mfs_3000(cli, args):
    rp = TextReport(args.output)
    ssids = list(topk_mfs(3000))
    random.shuffle(ssids)
    with FileHub(working_dir='data', default_mode='w') as hub, omw.ctx() as ctx:
        filename = 'omw3000A'
        for idx, sid in enumerate(ssids):
            ss = omw.get_synset(sid, ctx=ctx)
            if idx > len(ssids) / 2:
                filename = 'omw3000B'
            hub['omw3000'].header(ss.ID, 'lemmas: {}'.format(", ".join(ss.lemmas)))
            for d in ss.definitions:
                hub[filename].writeline(d)
                hub['omw3000'].print(d, level=1)
        rp.header("Generated files")
        for f in hub.files.keys():
            rp.print(hub[f].path)


def extract_wn31(cli, args):
    c = Counter()
    rp = TextReport()
    entries = []
    infile = FileHelper.abspath(args.input)
    if not os.path.isfile(infile):
        rp.print("File not found")
    else:
        rp.print("Processing {}".format(infile))
        tree = etree.iterparse(infile)
        for event, element in tree:
            if event == 'end' and element.tag == 'Synset':
                for child in element:
                    if child.tag == 'Definition':
                        entries.append((element.get('id'), element.get('ili'), child.text))
                        c.count('Definition')
                c.count("Synset")
                element.clear()
        c.summarise(report=rp)
    # Format: wn31sid ili definition
    CSV.write_tsv(args.output, entries)


def verify_wn31(cli, args):
    wn31 = CSV.read('data/wn31.csv', dialect='excel-tab')
    for sid, iid, sdef in wn31:
        if '"' in sdef and not (sdef.endswith('"') or sdef.endswith(')') or sdef.endswith(';')):
            cli.logger.warning("Invalid definition ({} - {}) {}".format(sid, iid, sdef))
            exit()
    print("Done!")
    pass


def wn31_to_wn30(cli, args):
    csvlines = CSV.read('data/ili-map-pwn30.tab')
    ili_map = {k: v for k, v in csvlines}
    notfound = []
    c = Counter()
    print("ILI-wn30 map: {}".format(len(ili_map)))
    wn31 = CSV.read('data/wn31.csv', dialect='excel-tab')
    with omw.ctx() as ctx, TextReport('data/wn31_diff.txt') as diff_file:
        for sid, iid, sdef in wn31:
            if iid in ili_map:
                c.count("Found")
                wn30_id = ili_map[iid]
                try:
                    if wn30_id.endswith('s'):
                        wn30_id = wn30_id[:-1] + 'a'
                    wn30_ss = omw.get_synset(wn30_id, ctx=ctx)
                except:
                    cli.logger.exception("Cannot find synset {}".format(wn30_id))
                    raise
                # compare def
                if sdef != wn30_ss.definition and not sdef.startswith(wn30_ss.definition + ";"):
                    diff_file.print("synset: {} | Lemmas: {}".format(wn30_id, ', '.join(wn30_ss.lemmas)))
                    diff_file.print("OMW   : {}".format(wn30_ss.definition))
                    diff_file.print("Wn31  : {}".format(sdef))
                    diff_file.print("")
                    c.count("Diff")
            else:
                notfound.append(iid)
                c.count("Not in ILI")
    c.summarise()
    print(notfound)
    pass


# -------------------------------------------------------------------------------
# Main method
# -------------------------------------------------------------------------------

def main():
    ''' Various tools for extracting Wordnets '''
    app = CLIApp(desc='OMW patching tools', logger=__name__)
    # convert
    task = app.add_task('mfs3000', func=gen_mfs_3000)
    task.add_argument('-o', '--output', help='Output file')
    # mfs 5000
    task = app.add_task('mfs5000', func=gen_mfs_5000)
    task.add_argument('-o', '--output', help='Output file')
    # mfs 5250
    task = app.add_task('mfs5500', func=gen_mfs_5500)
    task.add_argument('-o', '--output', help='Output file')
    # verify dataset
    task = app.add_task('verify', func=verify_mfs)
    # wn31 to csv
    task = app.add_task('wn31', func=extract_wn31)
    task.add_argument('-i', '--input', default='data/wn31.xml')
    task.add_argument('-o', '--output', help='Output file', default='data/wn31.csv')
    # verify wn31
    task = app.add_task('check31', func=verify_wn31)
    # wn31 to wn30
    task = app.add_task('31230', func=wn31_to_wn30)
    # run app
    app.run()


if __name__ == "__main__":
    main()
