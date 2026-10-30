import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from build_patch import read_archive_metadata
from scan_for_dogtown import scan_archive

game_dir = r'E:\game\Cyberpunk.2077.Repack.by.HardwareMining\by Decepticon\Cyberpunk 2077'
mod_recs, _ = read_archive_metadata(os.path.join(game_dir, 'archive', 'pc', 'mod', 'Rus_Dub_by_DreamVoice_v5.3.1.archive'))
mod_hashes = set(r[0] for r in mod_recs)

c_text = os.path.join(game_dir, 'archive', 'pc', 'content', 'lang_ru_text.archive')
e_text = os.path.join(game_dir, 'archive', 'pc', 'ep1', 'lang_ru_text.archive')

c_recs, c_segs = read_archive_metadata(c_text)
e_recs, e_segs = read_archive_metadata(e_text)

c_hashes = set(r[0] for r in c_recs)
e_hashes = set(r[0] for r in e_recs)

e_dog = set(x[0] for x in scan_archive(e_text, 'EP1'))
c_dog = set(x[0] for x in scan_archive(c_text, 'Content'))

all_target_c = (mod_hashes.intersection(c_hashes)).union(c_dog)
all_target_e = (mod_hashes.intersection(e_hashes)).union(e_dog)

print(f"Target files from Content: {len(all_target_c)}")
print(f"Target files from EP1: {len(all_target_e)}")
print(f"Total target files: {len(all_target_c) + len(all_target_e)}")

