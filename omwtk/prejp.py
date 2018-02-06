#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Japanese text preprocessor
Latest version can be found at https://github.com/letuananh/omwtk

Usage:
    ./prejp.py 

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
__copyright__ = "Copyright 2016, omwtk"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import os
from jinja2 import Template

from chirptext import FileHelper
from chirptext.cli import CLIApp
from chirptext.deko import analyse, DekoText, jaconv

MY_DIR = os.path.dirname(os.path.realpath(__file__))
RUBY_TEMPLATE_FILE = os.path.join(MY_DIR, 'templates', 'ruby.htm')
with open(RUBY_TEMPLATE_FILE, 'r') as tfile:
    RUBY_TEMPLATE = Template(tfile.read())


def gen_interlinear(content, title='', splitlines=False, add_surface=True):
    sents = DekoText.parse(content, splitlines=splitlines)
    doc = []
    final = sents
    for sent in sents:
        if add_surface:
            doc.append(sent.surface if sent.surface else str(sent))
        doc.append(' '.join(tk.reading_hira() for tk in sent))
        doc.append(jaconv.kana2alphabet(' '.join(tk.reading_hira() for tk in sent)))
        doc.append(' ')
    final = '\n'.join(doc)
    return final


def romanize(content, title='', splitlines=False):
    sents = DekoText.parse(content, splitlines=splitlines)
    doc = []
    final = sents
    for sent in sents:
        doc.append(jaconv.kana2alphabet(' '.join(tk.reading_hira() for tk in sent)))
    final = '\n'.join(doc)
    return final


def analyse_text(content, title, args, outpath=None):
    output = analyse(content, splitlines=not args.notsplit, format=args.format)
    if args.format == 'html':
        output = RUBY_TEMPLATE.render(title=title.replace('\n', ' '), doc=output)
    elif args.format == 'roumaji':
        output = romanize(content, splitlines=not args.notsplit)
    elif args.format == 'interlinear':
        output = gen_interlinear(content, splitlines=not args.notsplit)
    # write output
    outpath = outpath if outpath else args.output
    if not outpath:
        print(output)
    else:
        with open(outpath, 'w') as outfile:
            outfile.write(output)
            print("Converted data was written to {}".format(outpath))
    pass


def process_dir(cli, args):
    '''Directory to be processed'''
    if not os.path.isdir(args.indir):
        print("Not a directory (provided: {})".format(args.indir))
    # get children
    children = [x for x in FileHelper.get_child_files(args.indir) if x.endswith(".ja.txt")]
    for child in children:
        infile = os.path.join(args.indir, child)
        name, ext = os.path.splitext(child)
        suffix = '.furigana' if args.format in ('html',) else ''
        suffix += "." + args.format
        outfile = os.path.join(args.outdir, child[:-7] + suffix + ext)
        print("Process: {} => {}".format(child, outfile))
        if os.path.isfile(outfile):
            print("File {} exists. SKIPPED".format(outfile))
        else:
            content = FileHelper.read(infile)
            analyse_text(content, child, args, outpath=outfile)


def process_text(cli, args):
    '''Text string to be processed'''
    content = args.text
    title = args.text
    analyse_text(content, title, args)
    pass


def process_file(cli, args):
    '''Text file to be processed'''
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
    app = CLIApp(desc='Japanese text preprocessor', logger=__name__)

    task = app.add_task('file', func=process_file)
    task.add_argument('infile', help='Path to your text file', nargs='?', default='')
    task.add_argument('-o', '--output', help='Output file (defaulted to input_name.out.txt)')
    task.add_argument('-x', '--notsplit', help="Don't Split lines before content is analysed", action='store_true')
    task.add_argument('-F', '--format', help='Output format (txt/html/csv)', default='html')

    task = app.add_task('text', func=process_text)
    task.add_argument("text", help="Text string to be processed")
    task.add_argument('-o', '--output', help='Output file (defaulted to input_name.out.txt)')
    task.add_argument('-x', '--notsplit', help="Don't Split lines before content is analysed", action='store_true')
    task.add_argument('-F', '--format', help='Output format (txt/html/csv)', default='html')

    task = app.add_task('dir', func=process_dir)
    task.add_argument("indir", help="Path to directory")
    task.add_argument("outdir", help="Output directory")
    task.add_argument('-p', '--parse', help='Parse a single sentence')
    task.add_argument('-x', '--notsplit', help="Don't Split lines before content is analysed", action='store_true')
    task.add_argument('-F', '--format', help='Output format (txt/html/csv/roumaji/interlinear)', default='html')
    app.run()


if __name__ == "__main__":
    main()
