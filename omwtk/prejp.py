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

from chirptext.deko import analyse

with open('data/ruby.htm', 'r') as tfile:
    RUBY_TEMPLATE = Template(tfile.read())


def process(args):
    # Load content
    if args.input:
        infilepath = args.input
        if not os.path.isfile(infilepath):
            print("File does not exist (%s)" % (infilepath,))
            return False
        # Read input file
        with open(infilepath, 'r') as infile:
            content = infile.read()
            title = infilepath
    else:
        content = args.parse
        title = args.parse

    # process content using chirptext/deko
    output = analyse(content, splitlines=not args.notsplit, format=args.format)
    if args.format == 'html':
        output = RUBY_TEMPLATE.render(title=title.replace('\n', ' '), doc=output)
    # write to file if needed
    if not args.output:
        print(output)
    else:
        with open(args.output, 'w') as outfile:
            outfile.write(output)
            print("Converted data was written to {}".format(args.output))
    # done!


########################################################################

def main():
    ''' Japanese text preprocessor
    '''

    # It's easier to create a user-friendly console application by using argparse
    # See reference at the top of this script
    parser = argparse.ArgumentParser(description="Japanese text preprocessor.")

    # Positional argument(s)
    parser.add_argument('input', help='Input file', nargs='?', default='')
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
        if args.input or args.parse:
            process(args)
        else:
            print("Invalid input filename")
    pass


if __name__ == "__main__":
    main()
