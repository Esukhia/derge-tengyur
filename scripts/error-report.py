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
import json

PAREN_RE = re.compile(r"\(([^\),]*),([^\),]*)\)")
TOH_RE = re.compile(r"\{T(?P<idx>\d+[ab]?)(?:-(?P<subidx>\d+))?\}")
file_to_nberr = {}

def parrepl(match, mode, pagelinenum, filelinenum, volnum, shortfilename, options):
    first = match.group(1)
    sec = match.group(2)
    if (len(first) > 0 and len(sec) > 0 and (
            (first[0]== '་' and sec[0]!= '་') or 
            (sec[0]== '་' and first[0]!= '་') or
            (first[-1]== '་' and sec[-1]!= '་') or
            (sec[-1]== '་' and first[-1]!= '་'))):
        report_error(pagelinenum, filelinenum, volnum, shortfilename, "punctuation", "༺ཚེག་དང་གུག་རྟགས་མི་འགྲིག་པ།༻ tsheg not matching in parenthesis", "", options)
    return mode == 'first' and first or sec

error_regexps = [
        {"reg": re.compile(r"([^ །\(\)\[,]།[^ །\(\]\)༽,n]|(?:[^ངོེིུྃཾ]|ང[^ངོེིུྃཾ]|[^ང][ོེིུྃཾ])་།|(?:[^ཀགཤ།ོེིུྃཾ]|[ཀགཤ][^ཀགཤོེིུྃཾ]|[^ཀགཤ][ོེིུྃཾ]|[ཀགཤ][ོེིུྃཾ]།+)། །།|།།།)"), "msg": "༺ཚེག་ཤད་མི་འགྲིག་པ།༻ invalid shad sequence", "type": "punctuation"},
        {"reg": re.compile(r"[^ཀ-ྼ][ཱ-྄྆྇ྍ-ྼ]"), "msg": "༺ཁྲིམས་འགལ་ཡི་གེ།༻ invalid unicode combination sequence", "type": "invalid"},
        {"reg": re.compile(r"([^༄༅]༅|[^࿓࿔]࿔|[࿔༅][^།༅࿔])"), "msg": "༺ཡིག་མགོ་ཁྲིམས་འགལ།༻ invalid yigo", "type": "invalid"},
        {"reg": re.compile(r"[^ༀ-࿚#-~ \[\]\{\}\.ऽ।ं]"), "msg": "༺བོད་ཡིག་མིན་པ།༻ invalid unicode characters (non-Tibetan, non-ascii)", "type": "invalid"},
        {"reg": re.compile(r"([ྱུྲཿཾ྄ྃྭིྀ་ ])\1"), "msg": "༺དབྱངས་ཀྱི་སྐྱོན།༻ invalid double diactitic sign (shabkyu, gigu, etc.)", "type": "invalid"},
        {"reg": re.compile(r"[ༀ-༃༆-༊༎-༟ྰ]"), "msg": "༺ཡི་གེའི་དོགས་གཞི།༻ suspicious Tibetan character (mind 0FB0 vs. 0F71)", "type": "invalid"},
        {"reg": re.compile(r"([ཱ-྇][ྍ-ྼ]|[ི-྄]ཱ|[ྃཾཿ][ཱ-ཽྀ])"), "msg": "༺ཡི་གེ་གོ་རིམ་མི་འགྲིག་པ།༻ invalid character order (vowel before subscript)", "type": "invalid"},
        {"reg": re.compile(r"(ཪ[ླྙྲྱཱ-྇ །་༼-ྌྉྈ\(\)\[\]]|[^ཏ]ྲ[ྐ-ྫྷྮ-ྻ])"), "msg": "༺ར་མགོ་སྐྱོན་ཅན་གྱི་དོགས་གཞི།༻ possible wrong form of rago used (0F62 vs. 0F65)", "type": "invalid"},
        {"reg": re.compile(r"([ཀགཤ།] །|[^ ཀགཤ།]། |[ཀགཤ།]། |[ཀགཤ།][། ]|[༽ཿ་ \]nl])$"), "msg": "༺ཐིག་འཕྲེང་མཇུག་མཐའ་སྐྱོན་ཅན།༻ invalid end of line", "type": "punctuation", "neg": True},
        {"reg": re.compile(r"([ྀིེཻོཽུ]{2,}|ཱ{2,})"), "msg": "༺དབྱངས་ཀྱི་སྐྱོན།༻ invalid vowel duplication (use 0F7D and 0F7B when relevant)", "type": "invalid"},
        {"reg": re.compile(r"ཿ་"), "msg": "༺རྣམ་བཅད་མཐར་ཚེག་བཀོད་པའི་སྐྱོན།༻ invalid visarga + tshek", "type": "punctuation"},
    ]

def check_simple_regexp(line, pagelinenum, filelinenum, volnum, options, shortfilename):
    for regex_info in error_regexps:
        if not options["report"][regex_info["type"]]:
            continue
        if "neg" in regex_info and regex_info["reg"]:
            if not regex_info["reg"].search(line):
                report_error(pagelinenum, filelinenum, volnum, shortfilename, regex_info["type"], regex_info["msg"], "", options)
            continue
        for match in regex_info["reg"].finditer(line):
            s = match.start()
            e = match.end()
            linewithhighlight = line[:s]+"**"+line[s:e]+"**"+line[e:]
            report_error(pagelinenum, filelinenum, volnum, shortfilename, regex_info["type"], regex_info["msg"], linewithhighlight, options)

def report_error(linestr, filelinenum, volnum, shortfilename, errortype, errorstr, linewithhighlight, options):
    if not options["report"][errortype]:
        return
    printerror(shortfilename+", l. "+str(filelinenum)+" ("+linestr+"): "+errortype+": "+errorstr)
    if len(linewithhighlight) > 1:
        printerror("  -> "+linewithhighlight)
    if not shortfilename in file_to_nberr:
        file_to_nberr[shortfilename] = {'total': 0}
    fileerrs = file_to_nberr[shortfilename]
    fileerrs['total'] += 1
    if not errortype in fileerrs:
        fileerrs[errortype] = 0
    fileerrs[errortype] += 1
    

def endofverse(state, volnum, shortfilename, options):
    nbsyls = state['curnbsyllables']
    #print(str(nbsyls)+" "+str(state['prevnbsyllables']))
    if state["nbshad"] == 2 and state["prevnbshad"] == 2 and not state['hasjoker']:
        prevnbsyls = state['prevnbsyllables']
        nbsylsdiff = prevnbsyls - nbsyls
        if (prevnbsyls in [7,9,11]) and (nbsylsdiff == 1 or nbsylsdiff == -1):
            bchar = state['curbeginchar']
            line = state['curbeginline']
            highlight = line[:bchar]+"***"+line[bchar:]
            report_error(state['curbeginpagelinenum'], state['curbeginfilelinenum'], volnum, shortfilename, "verses", "verse has "+str(nbsyls)+" syllables while previous one has "+str(prevnbsyls), highlight, options)
    state['prevnbsyllables'] = nbsyls
    state['prevnbshad'] = state['nbshad']
    state['nbshad'] = 0
    state['curbeginchar'] = -1
    state['hasjoker'] = False

def endofsyllable(state):
    line = state['curbeginsylline']
    syllable = line[state['curbeginsylchar']:state['curendsylchar']]
    if syllable.startswith('བཛྲ') or syllable.startswith('པདྨ') or syllable.startswith('ཀརྨ') or syllable.startswith("ཤཱཀྱ"):
        state['curnbsyllables'] += 1
    if syllable.endswith('འོ') or syllable.endswith("འམ") or syllable.endswith("འང"):
        state['hasjoker'] = True
    state['curnbsyllables'] += 1

def check_verses(line, pagelinenum, filelinenum, state, volnum, options, shortfilename):
    lastistshek = state['lastistshek']
    lastisbreak = False
    for idx in range(0,len(line)):
        c = line[idx]
        if c in "#\{\}[]T01234567890ab.\n":
            continue
        if (c >= 'ཀ' and c <= 'ྃ') or (c >= 'ྐ' and c <= 'ྼ'):
            if lastisbreak:
                endofsyllable(state)
                endofverse(state, volnum, shortfilename, options)
            if state['curbeginchar'] == -1:
                state['curbeginchar'] = idx
                state['curnbsyllables'] = 0
                state['curbeginpagelinenum'] = pagelinenum
                state['curbeginline'] = line
                state['curbeginfilelinenum'] = filelinenum
            if not lastistshek and not lastisbreak:
                continue
            if lastistshek and not lastisbreak:
                endofsyllable(state)
            lastisbreak = False
            state['curbeginsylchar'] = idx
            state['curbeginsylline'] = line
            lastistshek = False
        elif c == '་' and not lastistshek and not lastisbreak:
            state['curendsylchar'] = idx
            lastistshek = True
        else:
            if not lastisbreak:
                if not lastistshek:
                    state['curendsylchar'] = idx
                lastisbreak = True
            if c == '།':
                state['nbshad'] += 1
    state['lastistshek'] = lastistshek

def tohmatch(tohm, state, pagelinenum, filelinenum, volnum, shortfilename, options):
    idx = tohm.group('idx')
    letter = ""
    if idx.endswith('a') or idx.endswith('b'):
        letter = idx[-1:]
        idx = idx[:-1]
    try:
        idxi = int(idx)
    except ValueError:
        report_error(pagelinenum, filelinenum, volnum, shortfilename, "format", "cannot convert Tohoku index to integer", "", options)
        return
    if idxi == 0:
        return
    lastidx = state['lasttohidx']
    lastletter = state['lasttohletter']
    if idxi != lastidx+1:
        if idxi == lastidx and ((lastletter == "a" and letter == "b") or (lastletter == "" and letter == "a")):
            pass
        else:
            report_error(pagelinenum, filelinenum, volnum, shortfilename, "tohoku", "non consecutive Tohoku indexes: "+str(lastidx)+lastletter+" -> "+idx+letter, "", options)
    state['lasttohidx'] = idxi
    state['lasttohletter'] = letter

def parse_one_line(line, filelinenum, state, volnum, options, shortfilename):
    if filelinenum == 1:
        state['pageseqnum']= 1
        state['pagenum']= 1
        state['pageside']= 'a'
        state['linenum'] = 0
        return
    pagelinenum = ''
    endpnumi = line.find(']')
    if endpnumi == -1:
        report_error("", filelinenum, volnum, shortfilename, "format", "cannot find \"]\"", "", options)
        return
    pagelinenum = line[1:endpnumi]
    if len(pagelinenum) < 2:
        report_error("", filelinenum, volnum, shortfilename, "format", "cannot understand page indication \"["+pagelinenum+"]\"", "", options)
        return
    pagenum = -1
    pageside = -1
    linenum = 0
    isBis = False
    doti = pagelinenum.find('.')
    if doti == -1:
        pageside = pagelinenum[-1]
        if pageside not in ['a', 'b']:
            report_error(pagelinenum, filelinenum, volnum, shortfilename, "format", "cannot understand page side", "", options)
            return
        pagenumstr = pagelinenum[:-1]
        if pagelinenum[-2]== 'x':
            isBis = True
            pagenumstr = pagelinenum[:-2]
        try:
            pagenum = int(pagenumstr)
        except ValueError:
            report_error(pagelinenum, filelinenum, volnum, shortfilename, "format", "cannot convert page to integer", "", options)
            return
    else:
        linenumstr = pagelinenum[doti+1:]
        pageside = pagelinenum[doti-1]
        if pageside not in ['a', 'b']:
            report_error(pagelinenum, filelinenum, volnum, shortfilename, "format", "cannot understand page side", "", options)
            return
        pagenumstr = pagelinenum[0:doti-1]
        if pagelinenum[doti-2]== 'x':
            isBis = True
            pagenumstr = pagelinenum[0:doti-2]
        try: 
            pagenum = int(pagenumstr)
            linenum = int(linenumstr)
        except ValueError:
            report_error(pagelinenum, filelinenum, volnum, shortfilename, "format", "cannot convert page / line to integer", "", options)
            return
    newpage = False
    if 'pagenum' in state and 'pageside' in state:
        oldpagenum = state['pagenum']
        oldpageside = state['pageside']
        if oldpagenum != pagenum and oldpagenum != pagenum-1:
            report_error("", filelinenum, volnum, shortfilename, "pagenumbering", "༺ཤོག་གྲངས་ཀྱི་སྐྱོན།༻ leap in page numbers from "+str(oldpagenum)+" to "+str(pagenum), "", options)
        if oldpagenum == pagenum and oldpageside == 'b' and pageside == 'a':
            report_error("", filelinenum, volnum, shortfilename, "pagenumbering", "༺ཤོག་ངོའི་སྐྱོན།༻ going backward in page sides", "", options)
        if oldpagenum == pagenum-1 and (pageside == 'b' or oldpageside == 'a'):
            report_error("", filelinenum, volnum, shortfilename, "pagenumbering", "༺ཤོག་ངོའི་སྐྱོན།༻ leap in page sides", "", options)
        if oldpagenum != pagenum or oldpageside != pageside:
            newpage = True
    if newpage:
        state['pageseqnum']+= 1
    state['pagenum']= pagenum
    state['pageside']= pageside
    if 'linenum' in state and linenum != 0:
        oldlinenum = state['linenum']
        if oldlinenum != linenum and oldlinenum != linenum-1:
            report_error(pagelinenum, filelinenum, volnum, shortfilename, "pagenumbering", "༺ཐིག་གྲངས་ཀྱི་སྐྱོན།༻ leap in line numbers from "+str(oldlinenum)+" to "+str(linenum), "", options)
    state['linenum']= linenum
    check_simple_regexp(line, pagelinenum, filelinenum, volnum, options, shortfilename)
    text = ''
    if len(line) > endpnumi+1:
        text = line[endpnumi+1:]
        if '{T' in text:
            if not '}' in text:
                report_error(pagelinenum, filelinenum, volnum, shortfilename, "format", "missing closing \"}\"", "", options)
            closeidx = text.find('}')
            if not text.startswith('༄༅༅། །', closeidx+1) and not text.startswith('༄༅། །', closeidx+1) and not text.startswith('༄། །', closeidx+1):
                rightcontext = text[closeidx+1:closeidx+5]
                report_error(pagelinenum, filelinenum, volnum, shortfilename, "punctuation", "༺དབུ་འཁྱུད་ཆད་པའི་སྐྱོན།༻ possible wrong beginning of text: \""+rightcontext+"\" should be \"༄༅༅། །\", \"༄༅། །\" or \"༄། །\"", "", options)
        for tohm in TOH_RE.finditer(text):
            tohmatch(tohm, state, pagelinenum, filelinenum, volnum, shortfilename, options)
        if 'keep_errors_indications' not in options or not options['keep_errors_indications']:
            text = text.replace('[', '').replace(']', '')
        if 'fix_errors' not in options or not options['fix_errors']:
            text = PAREN_RE.sub(lambda m: parrepl(m, 'first', pagelinenum, filelinenum, volnum, shortfilename, options), text)
        else:
            text = PAREN_RE.sub(lambda m: parrepl(m, 'second', pagelinenum, filelinenum, volnum, shortfilename, options), text)
        if options["report"]["verses"]:
            check_verses(text, pagelinenum, filelinenum, state, volnum, options, shortfilename)
        if text.find('(') != -1 or text.find(')') != -1:
            report_error(pagelinenum, filelinenum, volnum, shortfilename, "format", "༺གུག་རྟགས་ཆད་པའི་སྐྱོན།༻ spurious parenthesis", "", options)

def parse_one_file(infilename, state, volnum, options, shortfilename):
    with open(infilename, 'r', encoding="utf-8") as inf:
        state["curnbsyllables"] = 0
        state["prevnbsyllables"] = 0
        state["curbeginpagelinenum"] = ""
        state["curbeginline"] = ""
        state["curbeginchar"] = -1
        state["curbeginsylchar"] = -1
        state["curbeginfilelinenum"] = 0
        state["curendsylchar"] = -1
        state["curbeginsylline"] = ""
        state["nbshad"] = 0
        state["lastistshek"] = False
        state['hasjoker'] = False
        state['prevnbshad'] = 0
        linenum = 1
        for line in inf:
            if linenum == 1:
                line = line[1:]# remove BOM
            # [:-1]to remove final line break
            parse_one_line(line[:-1], linenum, state, volnum, options, shortfilename)
            linenum += 1
        endofverse(state, volnum, shortfilename, options)

errfile = open("errors.txt","w", encoding="utf-8")

def printerror(err):
    errfile.write(err+"\n")

if __name__ == '__main__':
    """ Example use """
    state = {
        "lasttohidx": 1108, # first index is 1109
        "lasttohsubidx": 0,
        "lasttohletter": ""
    }
    options = {
        "fix_errors": False,
        "keep_errors_indications": False,
        "report" : {
            "format": True,
            "pagenumbering": True,
            "invalid": True,
            "verses": False,
            "punctuation": False,
            "tohoku": True,
            "sanskrit": False
        }
    }
    for infilename in sorted(glob.glob("../text/*.txt")):
        #print(infilename)
        volnum = infilename[3:6]
        shortfilename = infilename[7:-4]
        try:
            volnum = int(volnum)
        except ValueError:
            print('wrong file format: '+volnum+'.txt')
            continue
        parse_one_file(infilename, state, volnum, options, shortfilename)

errfile.write("\n\n"+json.dumps(file_to_nberr, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))+"\n")
errfile.close()
