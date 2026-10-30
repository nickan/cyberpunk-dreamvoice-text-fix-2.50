import os
import struct
import ctypes
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from build_patch import read_archive_metadata

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

# Search patterns in UTF-8
targets = [
    "Пёсий".encode('utf-8'),
    "пёсий".encode('utf-8'),
    "Песий".encode('utf-8'),
    "песий".encode('utf-8'),
    "Пёсь".encode('utf-8'),
    "пёсь".encode('utf-8'),
    "Песь".encode('utf-8'),
    "песь".encode('utf-8'),
]

def scan_archive(arch_path, label):
    recs, segs = read_archive_metadata(arch_path)
    print(f"Scanning {label}: {len(recs)} records...")
    matches = []
    with open(arch_path, 'rb') as f:
        for i, rec in enumerate(recs):
            nh, ts, num_inline, ss, se, ds, de, sha1 = rec
            try:
                data = unpack_segment(f, segs[ss])
                found = []
                for t in targets:
                    c = data.count(t)
                    if c > 0:
                        found.append((t.decode('utf-8'), c))
                if found:
                    matches.append((nh, ts, segs[ss][2], found))
            except Exception as ex:
                pass
    print(f"Found in {label}: {len(matches)} files.")
    return matches

e_matches = scan_archive(os.path.join(game_dir, 'archive', 'pc', 'ep1', 'lang_ru_text.archive'), 'EP1 Text')
c_matches = scan_archive(os.path.join(game_dir, 'archive', 'pc', 'content', 'lang_ru_text.archive'), 'Content Text')

print("\n--- Summary of EP1 Matches ---")
for nh, ts, sz, found in e_matches:
    print(f"Hash: 0x{nh:016x}, Size: {sz}, Matches: {found}")

print("\n--- Summary of Content Matches ---")
for nh, ts, sz, found in c_matches:
    print(f"Hash: 0x{nh:016x}, Size: {sz}, Matches: {found}")
