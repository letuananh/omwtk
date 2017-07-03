#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Japanese text preprocessor
Latest version can be found at https://github.com/letuananh/pydemo

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
import re
# from collections import namedtuple

import MeCab
import jaconv
from jinja2 import Template

# reference: https://en.wikipedia.org/wiki/Hiragana_%28Unicode_block%29
# U+304x 		ぁ 	あ 	ぃ 	い 	ぅ 	う 	ぇ 	え 	ぉ 	お 	か 	が 	き 	ぎ 	く
# U+305x 	ぐ 	け 	げ 	こ 	ご 	さ 	ざ 	し 	じ 	す 	ず 	せ 	ぜ 	そ 	ぞ 	た
# U+306x 	だ 	ち 	ぢ 	っ 	つ 	づ 	て 	で 	と 	ど 	な 	に 	ぬ 	ね 	の 	は
# U+307x 	ば 	ぱ 	ひ 	び 	ぴ 	ふ 	ぶ 	ぷ 	へ 	べ 	ぺ 	ほ 	ぼ 	ぽ 	ま 	み
# U+308x 	む 	め 	も 	ゃ 	や 	ゅ 	ゆ 	ょ 	よ 	ら 	り 	る 	れ 	ろ 	ゎ 	わ
# U+309x 	ゐ 	ゑ 	を 	ん 	ゔ 	ゕ 	ゖ 			゙ 	゚ 	゛ 	゜ 	ゝ 	ゞ 	ゟ

hiragana = 'ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖ゙゚゛゜ゝゞゟ'

# reference: https://en.wikipedia.org/wiki/Katakana_%28Unicode_block%29
# U+30Ax 	゠ 	ァ 	ア 	ィ 	イ 	ゥ 	ウ 	ェ 	エ 	ォ 	オ 	カ 	ガ 	キ 	ギ 	ク
# U+30Bx 	グ 	ケ 	ゲ 	コ 	ゴ 	サ 	ザ 	シ 	ジ 	ス 	ズ 	セ 	ゼ 	ソ 	ゾ 	タ
# U+30Cx 	ダ 	チ 	ヂ 	ッ 	ツ 	ヅ 	テ 	デ 	ト 	ド 	ナ 	ニ 	ヌ 	ネ 	ノ 	ハ
# U+30Dx 	バ 	パ 	ヒ 	ビ 	ピ 	フ 	ブ 	プ 	ヘ 	ベ 	ペ 	ホ 	ボ 	ポ 	マ 	ミ
# U+30Ex 	ム 	メ 	モ 	ャ 	ヤ 	ュ 	ユ 	ョ 	ヨ 	ラ 	リ 	ル 	レ 	ロ 	ヮ 	ワ
# U+30Fx 	ヰ 	ヱ 	ヲ 	ン 	ヴ 	ヵ 	ヶ 	ヷ 	ヸ 	ヹ 	ヺ 	・ 	ー 	ヽ 	ヾ 	ヿ
all_katakana = '゠ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヷヸヹヺ・ーヽヾヿ'


########################################################################

# Reference: http://taku910.github.io/mecab/#parse
# MeCabToken = namedtuple('MeCabToken', 'surface pos sc1 sc2 sc3 inf conj root reading pron'.split())
class MeCabToken:
    def __init__(self, surface, pos=None, sc1=None, sc2=None, sc3=None, inf=None, conj=None, root=None, reading=None, pron=None):
        self.surface = surface
        self.pos = pos
        self.sc1 = sc1
        self.sc2 = sc2
        self.sc3 = sc3
        self.inf = inf
        self.conj = conj
        self.root = root
        self.reading = reading
        self.pron = pron

    def __str__(self):
        return '[{sur}({pos}-{s1}/{s2}/{s3}|{ro}|{re}|{pr})]'.format(sur=self.surface, pos=self.pos, s1=self.sc1, s2=self.sc2, s3=self.sc3, ro=self.root, re=self.reading, pr=self.pron)

    def __repr__(self):
        return str(self)

    def reading_hira(self):
        return jaconv.kata2hira(self.reading)

    def need_ruby(self):
        return self.reading and self.reading != self.surface and self.reading_hira() != self.surface

    @staticmethod
    def parse(raw):
        parts = re.split('\t|,', raw)
        if len(parts) < 10:
            parts += [''] * (10 - len(parts))
        (surface, pos, sc1, sc2, sc3, inf, conj, root, reading, pron) = parts
        return MeCabToken(surface, pos, sc1, sc2, sc3, inf, conj, root, reading, pron)

    def to_csv(self):
        return '{sur}\t{pos}\t{s1}\t{s2}\t{s3}\t{inf}\t{conj}\t{ro}\t{re}\t{pr}'.format(sur=self.surface, pos=self.pos, s1=self.sc1, s2=self.sc2, s3=self.sc3, inf=self.inf, conj=self.conj, ro=self.root, re=self.reading, pr=self.pron)


def txt2mecab(text):
    ''' Use mecab to parse one sentence '''
    mecab = MeCab.Tagger()
    mecab_out = mecab.parse(text).splitlines()
    tokens = [MeCabToken.parse(x) for x in mecab_out]
    return tokens


def lines2mecab(lines):
    ''' Use mecab to parse many lines '''
    sents = []
    for line in lines:
        sent = txt2mecab(line)
        sents.append(sent)
    return sents


def tokenize_sent(mtokens):
    sents = []
    bucket = []
    for t in mtokens:
        if t.surface != 'EOS':
            bucket.append(t)
        if t.pos == '記号' and t.sc1 == '句点':
            sents.append(bucket)
            bucket = []
    if bucket:
        sents.append(bucket)
    return sents


def rubyize(token):
    ''' Convert one MeCabToken into HTML '''
    if token.need_ruby():
        surface = token.surface
        reading = token.reading_hira()
        return '<ruby><rb>{sur}</rb><rt>{read}</rt></ruby>'.format(sur=surface, read=reading)
    if token.surface == 'EOS' and token.pos == '':
        return ''
    else:
        return token.surface


def rubyize_sent(sent):
    ''' Convert one MeCab sentence into HTML '''
    s = []
    for x in sent:
        s.append(rubyize(x))
    stext = ' '.join(s)
    # clean sentence a bit ...
    stext = stext.replace(' 。', '。').replace('「 ', '「').replace(' 」', '」').replace(' 、 ', '、').replace('（ ', '（').replace(' ）', '）')
    return stext


def analyse(content, title='', splitlines=True, format='html'):
    # Read ruby template
    with open('data/ruby.htm', 'r') as tfile:
        template = Template(tfile.read())
    # Process content using mecab
    if not splitlines:
        tokens = txt2mecab(content)
        sents = tokenize_sent(tokens)
    else:
        lines = content.splitlines()
        sents = lines2mecab(lines)
        tokens = []
        for sent in sents:
            tokens += sent
    doc = []
    # Generate output
    if format == 'html':
        for sent in sents:
            if format == 'html':
                doc.append(rubyize_sent(sent))
        # generate HTML content
        final = template.render(title=title.replace('\n', ' '), doc=doc)
    else:
        for sent in sents:
            doc.append('\n'.join([x.to_csv() for x in sent]) + '\n')
        final = '\n'.join(doc)
    return final


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
    # process content using mecab
    final = analyse(content, title=title, splitlines=not args.notsplit, format=args.format)
    # write to file if needed
    if not args.output:
        print(final)
    else:
        with open(args.output, 'w') as outfile:
            outfile.write(final)
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
    parser.add_argument('-F', '--format', help='Output format (txt/html)', default='html')

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
