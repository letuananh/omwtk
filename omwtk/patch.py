#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script to patch OMW
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
import json
from collections import OrderedDict

from chirptext import TextReport, FileHelper, Counter
from chirptext.cli import CLIApp, setup_logging
from chirptext.anhxa import to_obj
from yawlib import SynsetID
from yawlib.helpers import get_gwn
from yawlib.helpers import get_wn, get_omw

from omwtk.compare_wn import join_definitions

# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

DATA_FOLDER = os.path.abspath(os.path.expanduser('./data'))
setup_logging('logging.json', 'logs')


def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Data structure
# -------------------------------------------------------------------------------

class DefPatch(object):

    def __init__(self, sensekey='', orig_def='', new_def='', source='', comment='', informant=''):
        self.sensekey = sensekey.strip()
        self.orig_def = orig_def
        self.new_def = new_def
        self.source = source
        self.comment = comment
        self.informant = informant

    def to_json(self):
        return OrderedDict([("sensekey", self.sensekey),
                            ("orig_def", self.orig_def),
                            ("new_def", self.new_def),
                            ("comment", self.comment),
                            ("source", self.source),
                            ("informant", self.informant)])

    JOHN_MCCRAE_FIELD_MAP = {"sensekey": "sensekey",
                             "original_def": "orig_def",
                             "patched_def": "new_def",
                             "source": "source",
                             "comment": "comment",
                             "informat": "informant"}

    @staticmethod
    def from_string(patch_string):
        lines = [l.split("\t") for l in patch_string.splitlines()]
        patch_dict = {k: v for k, v in lines}
        return to_obj(DefPatch, patch_dict, **DefPatch.JOHN_MCCRAE_FIELD_MAP)

    @staticmethod
    def from_dict(yaml_dict):
        return DefPatch(**yaml_dict)


# -------------------------------------------------------------------------------
# Application logic
# -------------------------------------------------------------------------------

# Represent an OrderedDict preserving order
def _represent_dict_in_order(dumper, odict):
    return dumper.represent_mapping(u'tag:yaml.org,2002:map', odict.items())


# Use a safe dictionary representer for OrderectDict
yaml.add_representer(OrderedDict, _represent_dict_in_order)


def read_csv(patch_path):
    # John McCrae <john@mccr.ae> format
    with open(patch_path) as infile:
        content = infile.read()
        raw_patches = content.split("\t\n")
        patches = [DefPatch.from_string(p) for p in raw_patches]
        return patches


def convert(cli, args):
    ''' Convert patches from CSV format to YAML '''
    rp = TextReport()
    # validate input file
    if not args.input:
        patch_path = os.path.join(DATA_FOLDER, 'patches', '20171112_Wn31_glitches_def.csv')
    else:
        patch_path = args.input
    if not os.path.isfile(patch_path):
        raise Exception("File {} does not exist.".format(patch_path))
    # validate output file
    out_path = args.output if args.output else None
    if out_path == '*.yaml':
        out_path = FileHelper.replace_ext(patch_path, 'yaml')
    rp.print("Input:", patch_path)
    rp.print("Output:", out_path if out_path else '*stdout*')
    # convert patches
    patches = read_csv(patch_path)
    json_patches = [p.to_json() for p in patches]
    yaml_str = yaml.dump(json_patches, default_flow_style=False)
    # dump output
    if out_path:
        with open(out_path, 'w') as outfile:
            outfile.write(yaml_str)
        if args.echo:
            print(yaml_str)
    else:
        print(yaml_str)


def fix_gwn_def(a_def):
    return a_def[:-1] if a_def.endswith(';') else a_def


def verify_patch(cli, args):
    rp = TextReport()
    c = Counter()
    if not args.input or not os.path.isfile(args.input):
        raise Exception("Patch file not found")
    # load patches
    with open(args.input) as infile:
        patches = [DefPatch.from_dict(p) for p in yaml.safe_load(infile)]
    rp.print("Found {} patches.".format(len(patches)))
    # Validate against GWN-30
    # gwn = get_gwn()  # don't use GWN, for now
    omw = get_omw()
    wn = get_wn()
    with omw.ctx() as ctx, wn.ctx() as wnctx:
        for patch in patches:
            try:
                sid = wn.sk2sid(patch.sensekey, ctx=wnctx)
                if not sid:
                    raise Exception("sensekey `{}' does not exist.".format(patch.sensekey))
                ss = omw.get_synset(sid, ctx=ctx)
                ssdef = ss.definition[:-1] if ss.definition.endswith(';') else ss.definition
                if patch.orig_def == ssdef:
                    c.count("Found")
                    rp.print("-", "{} [{}]".format(patch.orig_def, patch.sensekey))
                    rp.print(" ", patch.new_def)
                    if patch.comment:
                        rp.print("C", patch.comment)
                else:
                    c.count("Found - diff")
                    rp.print("[DIFF]", "{} [{}]".format(patch.orig_def, patch.sensekey))
                    rp.print("New:  ", "{} [{}]".format(patch.new_def, patch.sensekey))
                    rp.print("      ", ssdef)
                    rp.print("Note: ", patch.comment)
            except:
                getLogger().warn("sensekey `{}' couldn't be found".format(patch.sensekey))
                c.count("Not found")
                continue
        c.summarise(report=rp)


def fix_typo(a_def):
    if a_def.endswith(' e.g.'):
        a_def = a_def[:-5]
    if a_def.endswith(':'):
        a_def = a_def[:-1]
    return a_def.replace('  ', ' ').replace(' )', ')').replace(' ,', ',')


def to_sqlite_string(a_string):
    return a_string.replace("'", "''")


def find_omw_typo(cli, args):
    omw = get_omw()
    with omw.ctx() as ctx:
        defs = ctx.synset_def.select("lang='eng' and (def like '% )%' or def like '%  %' or def like '% e.g.' or def like '% ,%' or def like '%:')")
        if args.action == 'list':
            print("Found {} definitions with typo".format(len(defs)))
            for d in defs:
                print(d)
                print("Fixed: {}".format(repr(fix_typo(d._2))))
        elif args.action == 'patch':
            patch_script = TextReport(args.output)
            for d in defs:
                fixed_def = fix_typo(d._2)
                patch_script.writeline("-- Orig : {} [{}]".format(d._2, d.synset))
                patch_script.writeline("-- Fixed: {}".format(fixed_def))
                patch_script.writeline("UPDATE synset_def SET def = '{}' WHERE synset='{}' AND def='{}';\n".format(to_sqlite_string(fixed_def), d.synset, to_sqlite_string(d._2)))


def read_nttat(cli, args):
    ''' Convert NTTAT patch to JSON '''
    stdout = TextReport()
    ext = 'json'
    rp = TextReport("{}_1.{}".format(args.output, ext))
    rp2 = TextReport("{}_2.{}".format(args.output, ext))
    gwn = get_gwn()
    data = []
    with open(args.input, 'r') as infile, gwn.ctx() as ctx:
        ssids = re.findall('\d{8}-[nvarx]', infile.read())
        print(len(ssids))
        print(ssids)
        for sid in ssids:
            ss = gwn.get_synset(sid, ctx=ctx)
            sdef = fix_gwn_def(ss.definition)
            stdout.header(sid, "Lemmas: {}".format(", ".join(ss.lemmas)))
            stdout.print(sdef)
            data.append({"synset": sid,
                         "lemmas": ss.lemmas,
                         "definition": sdef})
    cut = int(len(data) / 2)
    # first half
    first_half = json.dumps(data[:cut], indent=2)
    rp.write(first_half)
    # second half
    second_half = json.dumps(data[cut:], indent=2)
    rp2.write(second_half)


def remove_puncs(a_str):
    return a_str.replace(';', '').replace(':', '').replace(',', '')


def manual_patch(cli, args):
    rp = TextReport()
    omw = get_omw()
    if not args.input or not os.path.isfile(args.input):
        raise Exception("Input file could not be found")
    with open(args.input, 'r') as infile, omw.ctx() as ctx:
        synsets = json.loads(infile.read())
        # for ss in synsets:
        #     rp.print(ss['synset'], ss['definition'])
        # rp.print("Found synsets:", len(synsets))
        for sinfo in synsets:
            sid, fixed_def = sinfo['synset'], sinfo['definition']
            ss = omw.get_synset(sid, ctx=ctx)
            orig_def = remove_puncs(ss.definition)
            if remove_puncs(fixed_def) != orig_def:
                rp.header("WARNING:", sid)
                rp.print(ss.definition)
                rp.print(fixed_def)


def omw_fix_dup(cli, args):
    rp = TextReport(args.output)
    omw = get_omw()
    c = Counter()
    with omw.ctx() as ctx:
        senses = ctx.sense.select(limit=args.topk, columns=('synset',))
        synsetids = {s.synset for s in senses}
        rp.print("-- OMW synsets: {}\n".format(len(synsetids)))
        for sid in synsetids:
            try:
                sid = SynsetID.from_string(sid)
            except:
                cli.logger.warning("Ignored synset ID: {}".format(sid))
                continue
            ss = omw.get_synset(sid, ctx=ctx)
            fixed_def, dup_defs = join_definitions(ss)
            if dup_defs:
                c.count("Duplicated")
                rp.print("-- Original {}: {}".format(ss.ID, ss.definition))
                rp.print("-- Fixed    {}: {}".format(ss.ID, fixed_def))
                for dup in dup_defs:
                    rp.print("DELETE FROM synset_def WHERE synset='{}' and def='{}';".format(ss.ID, to_sqlite_string(dup)))
                rp.print()
        c.summarise()
        pass


# -------------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------------

def main():
    ''' Various tools to patch OMW '''
    app = CLIApp(desc='OMW patching tools', logger=__name__)
    # convert
    task = app.add_task('convert', func=convert)
    task.add_argument('-i', '--input', help='Input CSV file')
    task.add_argument('-o', '--output', help='Output YAML file')
    task.add_argument('-e', '--echo', help='Echo output to stdout', action='store_true')
    # verify a patch
    task = app.add_task('verify', func=verify_patch)
    task.add_argument('-i', '--input', help='YAML patch path')
    # find typo
    task = app.add_task('typo', func=find_omw_typo)
    task.add_argument('action', help='Action to be done about typo', choices=['list', 'patch'])
    task.add_argument('-o', '--output', help='Output script')
    # read NTTAT
    task = app.add_task('nttat', func=read_nttat)
    task.add_argument('-i', '--input', help='Input NTTAT file', default='data/NTTAT.txt')
    task.add_argument('-o', '--output', help='Output YAML file')
    # fix NTTAT
    task = app.add_task('manual', func=manual_patch)
    task.add_argument('-i', '--input', help='Input OMW patch (json)')
    # List all duplicated entries
    task = app.add_task('dup', func=omw_fix_dup)
    task.add_argument('-o', '--output', help='Output patch script')
    task.add_argument('-k', '--topk', help='Only process top k synsets')
    # run app
    app.run()


if __name__ == "__main__":
    main()
