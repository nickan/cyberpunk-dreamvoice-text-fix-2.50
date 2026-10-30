import os
import glob
import json
import re
from test_dogtown_replacement import RULES, apply_replacements

def patch_all_jsons(cr2w_dir: str):
    json_files = glob.glob(os.path.join(cr2w_dir, '*.cr2w.json'))
    print(f"[*] Patching {len(json_files)} JSON files in {cr2w_dir}...")
    
    total_replacements = 0
    modified_files = 0
    
    for jf in json_files:
        with open(jf, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        file_mod = False
        
        def process(node):
            nonlocal file_mod
            nonlocal total_replacements
            if isinstance(node, dict):
                for k, v in node.items():
                    if isinstance(v, str):
                        new_v = apply_replacements(v)
                        if new_v != v:
                            node[k] = new_v
                            total_replacements += 1
                            file_mod = True
                    else:
                        process(v)
            elif isinstance(node, list):
                for item in node:
                    process(item)
                    
        process(data)
        
        if file_mod:
            modified_files += 1
            with open(jf, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
    print(f"[+] Done! Made {total_replacements} replacements in {modified_files} files.")

if __name__ == '__main__':
    raw_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'work', 'cr2w_raw')
    patch_all_jsons(raw_dir)

