from pathlib import Path
import re

in_files = sorted(Path('../derge-tengyur-tags/').glob('*.txt'))
bo_int = {'0': '༠', '1': '༡', '2': '༢', '3': '༣', '4': '༤', '5': '༥', '6': '༦', '7': '༧', '8': '༨', '9': '༩'}
sections = {'ཚད་མ།': 'ཚད།',
            'རྒྱུད་འགྲེལ།': 'རྒྱུད།',
            'སྒྲ་མདོ།': 'སྒྲ།',
            'སྣ་ཚོགས།': 'སྣ།',
            'འདུལ་བ།': 'འདུལ།',
            'ཤེར་ཕྱིན།': 'ཤེར།',
            'སྐྱེས་རབས།': 'སྐྱེས།',
            'དབུ་མ།': 'དབུ།',
            'སེམས་ཙམ།': 'སེམས།',
            'འཁྲི་ཤིང།': 'འཁྲི།',
            'མདོ་སྡེ།': 'མདོ།',
            'མངོན་པ།': 'མངོན།',
            'གསོ་རིག': 'གསོ།',
            'སྤྲིང་ཡིག': 'སྤྲིང་།',
            'བསྟོད་ཚོགས།': 'བསྟོད།'}

counters = {'ཚད།': 0,
            'རྒྱུད།': 0,
            'སྒྲ།': 0,
            'སྣ།': 0,
            'འདུལ།': 0,
            'ཤེར།': 0,
            'སྐྱེས།': 0,
            'དབུ།': 0,
            'སེམས།': 0,
            'འཁྲི།': 0,
            'མདོ།': 0,
            'མངོན།': 0,
            'གསོ།': 0,
            'སྤྲིང་།': 0,
            'བསྟོད།': 0}

eq_table = []

current_section = ''
for f in in_files:
    print(f.name)
    name = f.stem
    vol_num, section, vol_ltr = name.split('_')
    section = sections[section]
    if not current_section:
        current_section = section
    if section != current_section:
        current_section = section
        text_count = 0

    content = f.read_text(encoding='utf-8-sig')
    chunks = re.split(r'({[A-Z].*?})', content)
    for i in range(1, len(chunks), 2):
        counters[section] += 1
        current = chunks[i]
        text_num = str(counters[section]).rjust(4, '0')
        text_num = ''.join([bo_int[a] for a in text_num])
        ref = f'D{vol_num}_{section}_{vol_ltr}_{text_num}'
        chunks[i] = '{' + ref + '}'
        eq_table.append((ref, current[1:-1]))

    f.write_text(''.join(chunks), encoding='utf-8-sig')

print(counters)
Path('old_new_names.tsv').write_text('\n'.join([a+'\t'+b for a, b in eq_table]))
