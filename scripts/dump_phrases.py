import json
import re

with open('work/ep1_onscreens.json.cr2w.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

entries = data['Data']['RootChunk']['root']['Data']['entries']
print("Entries count:", len(entries))

dog_entries = []
pattern = re.compile(r'([пП][ёе]с\w+)', re.IGNORECASE)

words = set()
samples = []

for e in entries:
    for var in ['femaleVariant', 'maleVariant']:
        val = e.get(var, '')
        if not val:
            continue
        m = pattern.findall(val)
        if m:
            for w in m:
                words.add(w)
            samples.append(val)

print("Unique words found:", len(words))
print("Sample entries with dogtown:", len(samples))
with open('work/dogtown_words.txt', 'w', encoding='utf-8') as out:
    for w in sorted(words):
        out.write(w + '\n')

with open('work/dogtown_samples.txt', 'w', encoding='utf-8') as out:
    for s in samples[:50]:
        out.write(s + '\n---\n')
