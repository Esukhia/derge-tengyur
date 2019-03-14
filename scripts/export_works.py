import argparse
from pathlib import Path
import re


def extract_lines():
    """
    parses the files line per line and returns the following structure

    return:
        {toh1: [(vol_id, line1), (vol_id, line2), ...], toh2: ...}
    """
    in_path = Path('../derge-tengyur-tags')
    files = sorted(list(in_path.glob('*.txt')))

    works = []
    prev_ref = ''
    current_work = []
    for file in files:
        prefix = file.stem
        lines = [line.strip().strip('\ufeff') for line in file.open().readlines()]
        for line in lines:
            ref = re.findall(r'{([DX].*?[ab]?)}', line)
            if ref:
                ### hack for case where two work refs are on the same line
                if len(ref) == 2 and ref[0] != ref[1]:
                    end_text, end_ref, start_text, start_ref, continue_text = re.split(r'{([DX].*?[ab]?)}', line)
                    current_work.append((prefix, end_text))
                    works.append((prev_ref, current_work))
                    works.append((end_ref, [(prefix, start_text)]))
                    prev_ref = start_ref
                    current_work = [(prefix, continue_text)]
                    continue
                ### end of hack
                if prev_ref != '':
                    current_work.append((prefix, line))

                    works.append((prev_ref, current_work))
                ref = ref[0]
                # initialize new work
                current_work = [(prefix, line)]
                prev_ref = ref
            else:
                current_work.append((prefix, line))
    return works


def works_in_pages(works_in_lines):
    """
    input:
        {toh1: [(vol_id, line1), (vol_id, line2), ...], toh2: ...}

    action:
        removes vol_id except for the first line of the work and for any volume change
    """
    works = []
    for work, lines in works_in_lines:
        vol_id = ''
        current_work = []
        for line in lines:
            vol, l = line
            if vol_id != vol:
                current_work.append(line)
                vol_id = vol
            else:
                current_work.append(l)
        works.append((work, current_work))
    return works


def works_stripped(works_in_lines):
    """
    Strips the beginning and ending lines of the bits of the surrounding works
    """
    works = []
    for work, lines in works_in_lines:
        current_work = []
        is_beginning = True
        for line in lines:
            # clean beginning line
            if is_beginning:
                if isinstance(line, tuple):
                    is_beginning = False
                    vol, l = line

                    # clean line
                    end_pagemark = l.find(']')
                    start_toh = l.find('{')
                    if end_pagemark + 1 < start_toh:
                        l = l[:end_pagemark+1] + l[start_toh:]
                    line = (vol, l)

            # clean ending line
            if line == lines[-1]:
                if isinstance(line, tuple):
                    line = line[1]
                new_toh_start = line.find('{')
                line = line[:new_toh_start]  # cut off new work
                end_pagemark = line.find(']')
                if end_pagemark == len(line) - 1:
                    continue

            # escapes preceding lines
            if not is_beginning:
                current_work.append(line)

        empty_line = True
        while empty_line:
            to_check = current_work[-1]
            if isinstance(to_check, tuple):
                to_check = to_check[1]
            if to_check.find(']') == len(to_check) - 1:
                del current_work[-1]
            else:
                empty_line = False

        works.append((work, current_work))
    return works


def flatten_for_output(works):
    """
    turns the volume names either at work beginning or at volume change into strings.
    The filename stem is included as volume indication.
    """
    for name, work in works:
        i = 0
        while i < len(work):
            if isinstance(work[i], tuple):
                work[i] = '[{} {}'.format(work[i][0].split('_', 1)[1].replace('_', ' '), work[i][1][1:])
            i += 1


def write_works(works, linesep='\n'):
    out_path = Path('export')
    if not out_path.is_dir():
        out_path.mkdir(exist_ok=True)
    out_path = out_path / 'works'
    if not out_path.is_dir():
        out_path.mkdir(exist_ok=True)

    for work, lines in works:
        if not work.startswith('X'):
            out_file = out_path / str(work + '.txt')
            out_file.write_text(linesep.join(lines))


def remove_markup(works):
    out = []
    for name, work in works:
        current_work = []
        for line in work:
            line = re.sub(r'\[.*?\]', '', line)
            line = re.sub(r'\{.*?\}', '', line)
            line = line.replace('#', '')

            # temporary removal of unprocessed files
            line = re.sub(r'^[0-9]+\.\s+', '', line)

            current_work.append(line)
        out.append((name, current_work))
    return out


parser = argparse.ArgumentParser()
parser.add_argument('--clean-content', help='"true" to clean the page and line markup')

if __name__ == '__main__':
    args = parser.parse_args()

    works = extract_lines()
    works = works_in_pages(works)
    works = works_stripped(works)
    flatten_for_output(works)
    if bool(args.clean_content):
        works = remove_markup(works)
    write_works(works)
