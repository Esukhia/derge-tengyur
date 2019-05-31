# kjtsv is the format requested by the Kumara Jiva translation project
# exports in Excel friendly tsv format, with links to images

import csv
import os
import re
import shutil
import datetime


inDir = '../text/'

releases = 'releases/'
if not os.path.exists(releases):
    os.makedirs(releases)

outDir = 'releases/kjtsv'
if not os.path.exists(outDir):
    os.makedirs(outDir)
shutil.rmtree(outDir, ignore_errors=True)
os.mkdir(outDir)


header = ['序號', '藏文文本Text', '中文翻譯Translation']
baseURL = 'https://s3.amazonaws.com/dtengyur/images/{volume}/{page}.jpg'

texts = os.listdir(inDir)

def writeTsv(data):
    with open(os.path.join(outDir, f'{t[:-3]}tsv'), 'wt', encoding='utf-16') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')
        for line in data:
            tsv_writer.writerow(line)

def formatData(lines, textName):
    tsvContent = [header]
    for line in lines:
        # if line headers
        if bool(re.search('(\[\d+[ab]\])', line)):
            lTag = re.search('(\[\d+[ab]\])', line).group(1)
            side = lTag[-2]
            # folio * 2 = page
            pageNum = int(lTag[1:-2])*2
            # folio * 2 - 1 = recto; folio * 2 = verso  
            if side == 'a':
                pageNum -= 1
            page = "{:0>4d}".format(pageNum)
            url = baseURL.format(volume=textName[:3], page=page)
            row = [f'=HYPERLINK("{url}", "{lTag}")']
            tsvContent.append(row)
        # if content
        elif bool(re.search('\d\]', line)):
            line = line.strip()
            row = ['', line]
            tsvContent.append(row)
        else:
            pass
    return tsvContent


def getData(text):
    tPath = os.path.join(inDir, text)
    with open(tPath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines


for t in texts:
    lines = getData(t)
    data = formatData(lines, t)
    writeTsv(data)

versionTag = str(datetime.date.today())[2:-3].replace('-', '')
shutil.make_archive(f'releases/deten_vol_kjtsv_v{versionTag}', 'zip', outDir)

    
