#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Japanese text preprocessor
Latest version can be found at https://github.com/letuananh/omwtk

References:
    Python documentation:
        https://docs.python.org/
    argparse module:
        https://docs.python.org/3/howto/argparse.html
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2016, Le Tuan Anh <tuananh.ke@gmail.com>
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

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2016, omwtk"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import sys
import os
import argparse
from jinja2 import Template

from chirptext import FileHelper
from chirptext.deko import analyse

MY_DIR = os.path.dirname(os.path.realpath(__file__))
RUBY_TEMPLATE_FILE = os.path.join(MY_DIR, 'templates', 'ruby.htm')
with open(RUBY_TEMPLATE_FILE, 'r') as tfile:
    RUBY_TEMPLATE = Template(tfile.read())


def analyse_text(content, title, args, outpath=None):
    output = analyse(content, splitlines=not args.notsplit, format=args.format)
    if args.format == 'html':
        output = RUBY_TEMPLATE.render(title=title.replace('\n', ' '), doc=output)
    # write output
    outpath = outpath if outpath else args.output
    if not outpath:
        print(output)
    else:
        with open(outpath, 'w') as outfile:
            outfile.write(output)
            print("Converted data was written to {}".format(args.output))
    pass


def process_dir(args):
    if not os.path.isdir(args.indir):
        print("Not a directory (provided: {})".format(args.indir))
    # get children
    children = [x for x in FileHelper.get_child_files(args.indir) if x.endswith(".ja.txt")]
    for child in children:
        infile = os.path.join(args.indir, child)
        outfile = os.path.join(args.outdir, child[:-7] + ".furigana." + args.format)
        print("Process: {} => {}".format(child, outfile))
        if os.path.isfile(outfile):
            print("File {} exists. SKIPPED".format(outfile))
        else:
            content = FileHelper.read(infile)
            analyse_text(content, child, args, outpath=outfile)


def process_text(args):
    content = args.text
    title = args.text
    analyse_text(content, title, args)
    pass


def process_file(args):
    # Load content
    if not os.path.isfile(args.infile):
        print("File does not exist (%s)" % (args.infile,))
        return False
    content = FileHelper.read(args.infile)
    title = args.infile
    analyse_text(content, title, args)


########################################################################

def main():
    ''' Japanese text preprocessor
    '''

    # It's easier to create a user-friendly console application by using argparse
    # See reference at the top of this script
    parser = argparse.ArgumentParser(description="Japanese text preprocessor.")

    tasks = parser.add_subparsers(help='Task to be done')

    file_task = tasks.add_parser('file', help='Text file to be processed')
    file_task.add_argument('infile', help='Path to your text file', nargs='?', default='')
    file_task.set_defaults(func=process_file)

    parse_task = tasks.add_parser('text', help='Text string to be processed')
    parse_task.add_argument("text", help="Text string to be processed")
    parse_task.set_defaults(func=process_text)

    batch_task = tasks.add_parser('dir', help='Directory to be processed')
    batch_task.add_argument("indir", help="Path to directory")
    batch_task.add_argument("outdir", help="Output directory")
    batch_task.set_defaults(func=process_dir)

    parser.add_argument('-o', '--output', help='Output file (defaulted to input_name.out.txt)')
    parser.add_argument('-d', '--debug', help='Enable debug mode', action='store_true')
    parser.add_argument('-p', '--parse', help='Parse a single sentence')
    parser.add_argument('-x', '--notsplit', help="Don't Split lines before content is analysed", action='store_true')
    parser.add_argument('-F', '--format', help='Output format (txt/html/csv)', default='html')

    # Optional argument(s)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")

    # Main script
    if len(sys.argv) == 1:
        # User didn't pass any value in, show help
        parser.print_help()
    else:
        # Parse input arguments
        args = parser.parse_args()
        if args.format not in ("txt", "html", "csv"):
            print("Invalid format chosen")
            return
        args.func(args)
    pass


if __name__ == "__main__":
    main()
