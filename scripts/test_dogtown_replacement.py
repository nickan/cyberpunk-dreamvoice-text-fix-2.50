import os
import glob
import json
import re

RULES = [
    # Adjectives: пёсьегородский -> догтаунский
    (r'\b[Пп][ёе]сьегоро[дц]ск([а-яё]+)\b', lambda m: ('Догтаунск' if m.group(0)[0].isupper() else 'догтаунск') + m.group(1)),
    (r'\bПЁСЬЕГОРО[ДЦ]СК([А-ЯЁ]+)\b', lambda m: 'ДОГТАУНСК' + m.group(1)),

    # ALL CAPS
    (r'\bПЁСЬЕГО\s+ГОРОДА\b', 'ДОГТАУНА'),
    (r'\bПЕСЬЕГО\s+ГОРОДА\b', 'ДОГТАУНА'),
    (r'\bПЁСЬЕМУ\s+ГОРОДУ\b', 'ДОГТАУНУ'),
    (r'\bПЕСЬЕМУ\s+ГОРОДУ\b', 'ДОГТАУНУ'),
    (r'\bПЁСЬЕМ\s+ГОРОДЕ\b', 'ДОГТАУНЕ'),
    (r'\bПЕСЬЕМ\s+ГОРОДЕ\b', 'ДОГТАУНЕ'),
    (r'\bПЁСЬИМ\s+ГОРОДОМ\b', 'ДОГТАУНОМ'),
    (r'\bПЕСЬИМ\s+ГОРОДОМ\b', 'ДОГТАУНОМ'),
    (r'\bПЁСИЙ\s+ГОРОД\b', 'ДОГТАУН'),
    (r'\bПЕСИЙ\s+ГОРОД\b', 'ДОГТАУН'),

    # Title / lower case
    (r'\b[Пп][ёе]сьего\s+города\b', lambda m: 'Догтауна' if m.group(0)[0].isupper() else 'догтауна'),
    (r'\b[Пп][ёе]сьему\s+городу\b', lambda m: 'Догтауну' if m.group(0)[0].isupper() else 'догтауну'),
    (r'\b[Пп][ёе]сьем\s+городе\b', lambda m: 'Догтауне' if m.group(0)[0].isupper() else 'догтауне'),
    (r'\b[Пп][ёе]сьим\s+городом\b', lambda m: 'Догтауном' if m.group(0)[0].isupper() else 'догтауном'),
    (r'\b[Пп][ёе]сий\s+город\b', lambda m: 'Догтаун' if m.group(0)[0].isupper() else 'догтаун'),
]

def apply_replacements(text: str) -> str:
    res = text
    for pat, rep in RULES:
        res = re.sub(pat, rep, res)
    return res

def test_all():
    json_files = glob.glob(r'C:\Users\jekak\.gemini\antigravity\scratch\cyberpunk-dreamvoice-text-fix-2.50\work\cr2w_raw\*.json')
    print(f"Testing on {len(json_files)} JSON files...")

    total_changes = 0
    changed_files = 0
    samples = []

    for jf in json_files:
        with open(jf, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        file_modified = False
        
        def process_node(node):
            nonlocal file_modified
            nonlocal total_changes
            if isinstance(node, dict):
                for k, v in node.items():
                    if isinstance(v, str):
                        new_v = apply_replacements(v)
                        if new_v != v:
                            total_changes += 1
                            file_modified = True
                            if len(samples) < 30:
                                samples.append((v, new_v))
                    else:
                        process_node(v)
            elif isinstance(node, list):
                for item in node:
                    process_node(item)

        process_node(data)
        if file_modified:
            changed_files += 1

    print(f"Total string replacements: {total_changes} in {changed_files} files.")
    print("\nSample replacements (before -> after):")
    for b, a in samples[:15]:
        b_disp = (b[:70] + '...') if len(b) > 70 else b
        a_disp = (a[:70] + '...') if len(a) > 70 else a
        print(f"  [-] {b_disp.encode('unicode_escape').decode('ascii')}")
        print(f"  [+] {a_disp.encode('unicode_escape').decode('ascii')}\n")

if __name__ == '__main__':
    test_all()
