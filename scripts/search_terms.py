import json
import re

with open('work/ep1_onscreens.json.cr2w.json', 'r', encoding='utf-8') as f:
    text = f.read()

matches = re.findall(r'(\b[пП][ёе]с[ьяиеоуы]\w*)', text)
print(f"Total matches: {len(matches)}")
unique = sorted(set(matches))
print("Unique words:")
for u in unique:
    print(" -", u)

