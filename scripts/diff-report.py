#!/usr/bin/env python3

# The MIT License (MIT)
# Copyright (c) 2018 Esukhia
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import re
import os
import glob
import unicodedata
from diff_match_patch import diff_match_patch
from urllib.parse import unquote

PAREN_RE = re.compile(r"\(([^\),]*),([^\),]*)\)")
TOH_RE = re.compile(r"\{T(?P<idx>\d+[ab]?)(?:-(?P<subidx>\d+))?\}")

errfile = open("diffs.txt","w", encoding="utf-8")

DMP = diff_match_patch()

def printerror(err):
    errfile.write(err+"\n")

def diff_linesToWords(text1, text2):
    """
    a copy of diff_linesToChars that redefines the linebreak character
    note: all "line"s have been renamed to "word"s
    """
    wordArray = []
    wordHash = {}

    wordArray.append('')

    def diff_wordsToCharsMunge(text):
        chars = []
        wordStart = 0
        wordEnd = -1
        while wordEnd < len(text) - 1:
            wordEnd = text.find('་', wordStart)
            if wordEnd == -1:
                wordEnd = len(text) - 1
            word = text[wordStart:wordEnd + 1]
            wordStart = wordEnd + 1

            if word in wordHash:
                chars.append(chr(wordHash[word]))
            else:
                wordArray.append(word)
                wordHash[word] = len(wordArray) - 1
                chars.append(chr(len(wordArray) - 1))
        return "".join(chars)

    chars1 = diff_wordsToCharsMunge(text1)
    chars2 = diff_wordsToCharsMunge(text2)
    return chars1, chars2, wordArray
    
def diff_wordMode(text1, text2):
    """
    implements what is proposed here:
    See https://github.com/google/diff-match-patch/wiki/Line-or-Word-Diffs#word-mode
    """
    lineText1, lineText2, lineArray = diff_linesToWords(text1, text2)
    diffs = DMP.diff_main(lineText1, lineText2, False)
    DMP.diff_charsToLines(diffs, lineArray)
    return diffs

def format_diffs(diffs):
    formatted = []
    diff = {}
    for op, text in diffs:
        if op == 0:
            if diff:
                formatted.append(diff)
                diff = {}
            formatted.extend(text.split(' '))  # split the text between diffs into syllables
        elif op == -1:
            diff['-'] = text.replace(' ', '')  # delete all spaces added to separate syllables
        elif op == 1:
            diff['+'] = text.replace(' ', '')  # idem
    if diff:
        formatted.append(diff)
    print(formatted)
    return formatted

def fillonelinestr(line, linenum, volnum, pagelinetolinestr):
    endpnumi = line.find(']')
    pagelinestr = line[1:endpnumi]
    line = line[endpnumi+1:]
    if line == "":
        return
    line = line.replace('[','').replace("]","").replace("#", "")
    line = PAREN_RE.sub(r"\1", line)
    line = TOH_RE.sub("", line)
    pagelinetolinestr[pagelinestr] = {'e': line}

def filllinestr(volnum, pagelinetolinestr):
    with open(infilename, 'r', encoding="utf-8") as inf:
        linenum = 1
        for line in inf:
            fillonelinestr(line[:-1], linenum, volnum, pagelinetolinestr)
            linenum += 1

def filllinestrext(volnum, pagelinetolinestr):
    subfoldername = "degetengyur-proofread/degetengyur"+str(volnum)
    for infilename in sorted(glob.glob(subfoldername+"/*.xml")):
        with open(infilename, 'r', encoding="utf-8") as inf:
            linenum = 1
            curline = 1
            curpage = "1a"
            for line in inf:
                if line.startswith("<pb"):
                    lastdashidx = line.rfind('-')
                    lastquoteidx = line.rfind('"')
                    curpage = line[lastdashidx+1:lastquoteidx]
                    curline = 0
                    continue
                linenum += 1
                curline += 1
                line = line[:-1]
                if line == "" or line.startswith("empty"):
                    continue
                pagelinestr = curpage+'.'+str(curline)
                line = unicodedata.normalize("NFKD", line)
                line = line.replace("ཱྀ", "ཱྀ").replace("ཱུ", "ཱུ").replace("ༀ", "ཨོཾ").replace("༌", "་")
                if not pagelinestr in pagelinetolinestr:
                    print("missing page "+pagelinestr+" in vol. "+str(volnum)+" of eTengyur")
                else:
                    pagelinetolinestr[pagelinestr]['a'] = line

def comparelines(volnum, pagelinetolinestr):
    for key in sorted(pagelinetolinestr):
        lineinfo = pagelinetolinestr[key]
        if not 'a' in lineinfo:
            print("missing page "+key+" in vol. "+str(volnum)+" A Tengyur")
            continue
        linee = lineinfo['e']
        linea = lineinfo['a']
        #print('-['+key+']'+linee)
        #print('+['+key+']'+linea)
        diffs = diff_wordMode(linee, linea)
        if len(diffs) == 1:
            continue
        patches = DMP.patch_make(linee, diffs)
        patch_text = DMP.patch_toText(patches)
        print('['+key+']:')
        print(unquote(patch_text))
        # if len(diffs) != 0:
        #     print('['+key+']'+format_diffs(diffs))

def compare_volume(volnum, filename):
    pagelinetolinestr = {}
    filllinestr(volnum, pagelinetolinestr)
    filllinestrext(volnum, pagelinetolinestr)
    comparelines(volnum, pagelinetolinestr)

if __name__ == '__main__':
    for infilename in sorted(glob.glob("../derge-tengyur-tags/*.txt")):
        volnum = infilename[22:25]
        shortfilename = infilename[22:-4]
        try:
            volnum = int(volnum)
        except ValueError:
            print('wrong file format: '+shortfilename+'.txt')
            continue
        compare_volume(volnum, shortfilename)
        break

errfile.close()