#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Raw cleaner
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
import sys
from puchikarui.puchikarui import Schema
from collections import namedtuple
from collections import defaultdict as dd
from chirptext.leutile import Counter, FileTool, TextReport
import re
import argparse

########################################################################
# Configuration
########################################################################

OUT_DIR = os.path.expanduser('./data/')
INPUT_FILE = os.path.join(OUT_DIR, 'input.txt')


########################################################################

def remove_numbering(line):
    cleaned_line = line
    match_results = re.match( '^\d+', line)
    if match_results:
        if not re.match( r'^\d+[.,]*', line):
            print ( "WARNING: %s" % line )
        cleaned_line = re.sub( r'^\d+[.,]*', '', line)
    return cleaned_line.strip()

def remove_special_chars(line):
    if line.endswith(' .'):
        # print(line)
        pass
    line = line.replace('\\', '').replace(' ?', '?')
    line = re.sub( r'\ *\.$', '.', line)
    line = re.sub( r'\ *!$', '!', line)
    line = re.sub( r'\ *,$', '!', line)
    # print ("   => %s" % line) 
    return line

def clean_corpus(inputfile):
    print("Script for cleaning raw text input")
    c = Counter()
    all_chars = set()
    
    output_file    = os.path.join(OUT_DIR, FileTool.getfilename(inputfile) + '.cleaned.txt')
    output_numfile = os.path.join(OUT_DIR, FileTool.getfilename(inputfile) + '.num.txt')
    print("Input file            : %s" % (inputfile))
    print("Output file           : %s" % (output_file))
    print("Output (numbered) file: %s" % (output_numfile))
    
    with open(inputfile, 'r', encoding='utf8') as infile, open(output_file, 'w', encoding='utf8') as outfile, open(output_numfile, 'w', encoding='utf8') as outnumfile: 
        for linenum, line in enumerate(infile):
            c.count("Line")
            cleaned_line = remove_numbering(line)
            cleaned_line = remove_special_chars(cleaned_line)
            for a_char in cleaned_line:
                all_chars.add(a_char)
            outfile.write("%s\n" % cleaned_line)
            outnumfile.write("%s\t%s\n" % (linenum+1, cleaned_line))
        c.summarise()
    print("-" * 80)
    try:
        print("All characters: %s" % str(sorted(list(all_chars))))
    except:
        pass
    print("Done!")

########################################################################
    
def main():
    ''' This program starts here
    '''
    parser = argparse.ArgumentParser(description="Clean a text corpus.")
    
    # Positional argument(s)
    parser.add_argument('input', help='Path to corpus file.')

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
        # Now do something ...
        if args.input:
            inputfile = INPUT_FILE
            if not os.path.isfile(inputfile):
                print("File [%s] cannot be found, attempting to use [%s] instead ..." % (inputfile, INPUT_FILE))
                inputfile = INPUT_FILE
            clean_corpus(args.input)
    pass

if __name__ == "__main__":
    main()
