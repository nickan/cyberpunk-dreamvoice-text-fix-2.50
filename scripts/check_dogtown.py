import json

with open('work/ep1_onscreens.json.cr2w.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

entries = d['Data']['RootChunk']['root']['Data']['entries']
print("Total entries:", len(entries))

count = 0
for e in entries:
    fem = e.get('femaleVariant', '')
    male = e.get('maleVariant', '')
    # Check for dog / dogtown in Russian or English
    text = fem + " " + male
    if any(k in text.lower() for k in ["dogtown", "\u043f\u0451\u0441", "\u043f\u0435\u0441"]):
        print(f"Key: {e.get('secondaryKey')}")
        print(f"  Female: {fem}")
        if male:
            print(f"  Male: {male}")
        count += 1
        if count >= 10:
            break

print("Found matching entries:", count)

