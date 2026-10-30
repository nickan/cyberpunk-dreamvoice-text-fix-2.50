import os
import sys
import struct
import ctypes

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from build_patch import read_archive_metadata
from scan_for_dogtown import scan_archive

game_dir = r'E:\game\Cyberpunk.2077.Repack.by.HardwareMining\by Decepticon\Cyberpunk 2077'
dll = ctypes.cdll.LoadLibrary(os.path.join(game_dir, 'bin', 'x64', 'oo2ext_7_win64.dll'))
decompress = dll.OodleLZ_Decompress
decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
decompress.restype = ctypes.c_int

def unpack_segment(f, seg):
    off, zsz, sz = seg
    f.seek(off)
    raw = f.read(zsz)
    if zsz == sz:
        return raw
    if raw[:4] == b'KARK':
        raw = raw[8:]
        zsz -= 8
    buf = ctypes.create_string_buffer(sz)
    ret = decompress(raw, zsz, buf, sz, 0, 0, 0, None, 0, None, None, None, 0, 0)
    if ret <= 0:
        raise RuntimeError(f"Decompress error: {ret}")
    return buf.raw[:ret]

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

targets_c = (mod_hashes.intersection(c_hashes)).union(c_dog)
targets_e = (mod_hashes.intersection(e_hashes)).union(e_dog)

print(f"Target Content files: {len(targets_c)}, Target EP1 files: {len(targets_e)}")

# Create output dirs
out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'work', 'cr2w_raw')
os.makedirs(out_dir, exist_ok=True)

extracted = []

with open(c_text, 'rb') as f:
    for rec in c_recs:
        nh = rec[0]
        if nh in targets_c:
            ss = rec[3]
            data = unpack_segment(f, c_segs[ss])
            p = os.path.join(out_dir, f"c_{nh:016x}.cr2w")
            with open(p, 'wb') as out_f:
                out_f.write(data)
            extracted.append((nh, 'content', rec, p))

with open(e_text, 'rb') as f:
    for rec in e_recs:
        nh = rec[0]
        if nh in targets_e:
            ss = rec[3]
            data = unpack_segment(f, e_segs[ss])
            p = os.path.join(out_dir, f"e_{nh:016x}.cr2w")
            with open(p, 'wb') as out_f:
                out_f.write(data)
            extracted.append((nh, 'ep1', rec, p))

print(f"Successfully extracted {len(extracted)} files to {out_dir}")
