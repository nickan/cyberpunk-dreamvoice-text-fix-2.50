import os
import sys
import glob
import struct
import hashlib
import ctypes
from typing import Dict, Tuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from build_patch import get_crc_table, compute_crc, read_archive_metadata

def create_archive(game_dir: str, cr2w_dir: str, output_path: str):
    exe_path = os.path.join(game_dir, 'bin', 'x64', 'Cyberpunk2077.exe')
    c_text_path = os.path.join(game_dir, 'archive', 'pc', 'content', 'lang_ru_text.archive')
    e_text_path = os.path.join(game_dir, 'archive', 'pc', 'ep1', 'lang_ru_text.archive')
    dll_path = os.path.join(game_dir, 'bin', 'x64', 'oo2ext_7_win64.dll')

    print("[*] Loading Oodle DLL...")
    dll = ctypes.cdll.LoadLibrary(dll_path)
    compress = dll.OodleLZ_Compress
    compress.argtypes = [
        ctypes.c_int, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p,
        ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_void_p, ctypes.c_size_t
    ]
    compress.restype = ctypes.c_int

    print("[*] Extracting CRC table from Cyberpunk2077.exe...")
    crc_table = get_crc_table(exe_path)

    print("[*] Reading vanilla metadata to preserve timestamps...")
    c_recs, _ = read_archive_metadata(c_text_path)
    e_recs, _ = read_archive_metadata(e_text_path)
    ts_map = {}
    for r in c_recs:
        ts_map[r[0]] = r[1]
    for r in e_recs:
        ts_map[r[0]] = r[1]

    cr2w_files = glob.glob(os.path.join(cr2w_dir, '*.cr2w'))
    print(f"[*] Found {len(cr2w_files)} patched CR2W files to pack.")

    entries_to_pack = []
    
    for fpath in cr2w_files:
        fname = os.path.basename(fpath)
        # c_<hash>.cr2w or e_<hash>.cr2w
        nh_hex = fname.split('.')[0][2:]
        nh = int(nh_hex, 16)
        ts = ts_map.get(nh, 0)
        
        with open(fpath, 'rb') as f:
            raw_data = f.read()
            
        sz = len(raw_data)
        sha1 = hashlib.sha1(raw_data).digest()
        
        # Compress with Kraken (level 4)
        comp_buf = ctypes.create_string_buffer(sz + 65536)
        comp_len = compress(8, raw_data, sz, comp_buf, 4, None, None, None, None, 0)
        if comp_len <= 0:
            raise RuntimeError(f"Compression failed for {fname}")
            
        chunk_data = b'KARK' + struct.pack('<I', sz) + comp_buf.raw[:comp_len]
        zsz = len(chunk_data)
        
        entries_to_pack.append({
            'nh': nh,
            'ts': ts,
            'sha1': sha1,
            'sz': sz,
            'zsz': zsz,
            'chunk': chunk_data,
            'fname': fname
        })

    # Sort entries by file hash (mandatory for binary search in REDengine TOC)
    entries_to_pack.sort(key=lambda x: x['nh'])
    print(f"[*] Sorted {len(entries_to_pack)} entries by hash.")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    print(f"[*] Writing archive to: {output_path}")

    with open(output_path, 'wb') as f:
        # Initial header placeholder (172 bytes)
        f.write(b'\x00' * 172)

        file_segments = []
        file_records = []

        for i, entry in enumerate(entries_to_pack):
            seg_off = f.tell()
            f.write(entry['chunk'])
            file_segments.append((seg_off, entry['zsz'], entry['sz']))
            # REDengine 4 file record (56 bytes)
            rec = struct.pack('<QQIIIII', entry['nh'], entry['ts'], 0, i, i + 1, 0, 0) + entry['sha1']
            file_records.append(rec)

        # REDengine 4 DirectStorage rule: IndexPosition MUST be a multiple of 4096!
        pos = f.tell()
        if pos % 4096 != 0:
            f.write(b'\xd9' * (4096 - (pos % 4096)))

        index_pos = f.tell()
        fc = len(file_records)
        sc = len(file_segments)
        # REDengine 4 TableSize rule: excludes foff(4) and fsz(4), so isize - 8!
        table_size = 20 + (56 * fc) + (16 * sc)

        toc_buf = bytearray()
        toc_buf += struct.pack('<IIQ', 8, table_size, 0)
        toc_buf += struct.pack('<III', fc, sc, 0)
        for r in file_records:
            toc_buf += r
        for off, zsz, sz in file_segments:
            toc_buf += struct.pack('<QII', off, zsz, sz)

        # REDengine 4 CRC check
        crc_val = compute_crc(toc_buf[16:], crc_table)
        toc_buf[8:16] = struct.pack('<Q', crc_val)

        index_size = len(toc_buf)
        f.write(toc_buf)

        # REDengine 4 DirectStorage rule: Filesize MUST be a multiple of 4096!
        pos = f.tell()
        if pos % 4096 != 0:
            f.write(b'\xd9' * (4096 - (pos % 4096)))

        filesize = f.tell()
        f.seek(0)
        # Header (RDAR v12)
        hdr = struct.pack('<4sIQIQIQI', b'RDAR', 12, index_pos, index_size, 0, 0, filesize, 0)
        f.write(hdr)

    print(f"[+] Archive created successfully: {output_path}")
    print(f"    Size: {filesize:,} bytes (~{filesize / (1024*1024):.2f} MB)")
    print(f"    Files: {fc}, Segments: {sc}, 4096-aligned: True")

if __name__ == '__main__':
    game = r'E:\game\Cyberpunk.2077.Repack.by.HardwareMining\by Decepticon\Cyberpunk 2077'
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cr2w = os.path.join(base_dir, 'work', 'cr2w_patched')
    out_archive = os.path.join(game, 'archive', 'pc', 'mod', '###_DreamVoice_Fix_Text_2.50.archive')
    create_archive(game, cr2w, out_archive)

