import json

with open('work/ep1_onscreens.json.cr2w.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

entries = d['Data']['RootChunk']['root']['Data']['entries']

count = 0
for e in entries:
    fem = e.get('femaleVariant', '')
    male = e.get('maleVariant', '')
    text = fem + " " + male
    if any(k in text.lower() for k in ["dogtown", "\u043f\u0451\u0441", "\u043f\u0435\u0441"]):
        print("Key:", e.get('secondaryKey'))
        print("  Female:", fem.encode('unicode_escape').decode('ascii'))
        count += 1
        if count >= 5:
            break

