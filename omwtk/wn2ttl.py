#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Convert GWN to TTL format
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
import logging
import argparse
import json

from chirptext import header, FileHelper, TextReport
from coolisf.model import Document
from yawlib.glosswordnet import GWordnetXML

# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
DATA_FOLDER = os.path.abspath(os.path.expanduser('./data'))

# -------------------------------------------------------------------------------
# Application logic
# -------------------------------------------------------------------------------


def convert_json(synsets, outfile):
    print("Exporting to JSON")
    for ss in synsets:
        for g in ss:
            j = g.to_ttl().to_json()
            outfile.write(json.dumps(j))
            outfile.write('\n')
        outfile.write('\n')


def convert_xml(synsets, outfile):
    print("Exporting to JSON")
    doc = Document(name=outfile.name)
    for ss in synsets:
        for g in ss:
            tsent = g.to_ttl()
            sent = doc.new(text=tsent.text, ident=tsent.ID)
            sent.shallow = tsent
    # write doc
    outfile.write(doc.to_xml_str())


def wn2ttl(args):
    inpath = FileHelper.abspath(args.inpath)
    header("WN to TTL format")
    wn = GWordnetXML()
    wn.read(inpath)
    print("Found senses: {}".format(len(wn.synsets)))
    outpath = FileHelper.abspath(args.outpath) if args.outpath else None
    with TextReport(outpath, 'w') as outfile:
        if args.format == 'json':
            convert_json(wn.synsets, outfile)
        elif args.format == 'xml':
            convert_xml(wn.synsets, outfile)
    print("Done!")


def config_logging(args):
    ''' Override root logger's level '''
    if args.quiet:
        logging.getLogger().setLevel(logging.CRITICAL)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)


# -------------------------------------------------------------------------------
# Main method
# -------------------------------------------------------------------------------

def main():
    '''Main entry of wn2ttl
    '''

    # It's easier to create a user-friendly console application by using argparse
    # See reference at the top of this script
    parser = argparse.ArgumentParser(description="WN to TTL", add_help=False)
    parser.set_defaults(func=None)

    # Optional argument(s)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")

    tasks = parser.add_subparsers(help="Task to be done")

    wn2ttl_task = tasks.add_parser('convert', help='Convert GWN to TTL format')
    wn2ttl_task.add_argument('inpath', help='Path to glosstag XML file')
    wn2ttl_task.add_argument('outpath', nargs="?", default=None)
    wn2ttl_task.add_argument('-f', '--format', choices=['xml', 'json'], default='json')
    wn2ttl_task.set_defaults(func=wn2ttl)

    # Main script
    args = parser.parse_args()
    config_logging(args)
    if args.func is not None:
        args.func(args)
    else:
        parser.print_help()
    pass


if __name__ == "__main__":
    main()
