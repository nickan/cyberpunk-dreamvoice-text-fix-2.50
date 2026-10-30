"""
Cyberpunk 2077 - DreamVoice Phantom Liberty Text Fix Builder (Patch 2.50+)
Author: Antigravity & User

Automated tool to create a lightweight patch archive (.archive) that overrides
outdated text localization files from DreamVoice Russian Dub mod while keeping
100% of the Russian voice acting intact.
"""

import os
import sys
import struct
import argparse
from typing import List, Dict, Tuple, Set

def get_crc_table(exe_path: str) -> Tuple[int, ...]:
    """Extracts the exact REDengine 4 64-bit CRC table from Cyberpunk2077.exe."""
    with open(exe_path, 'rb') as f:
        f.seek(0x36f6b40)
        return struct.unpack('<256Q', f.read(2048))

def compute_crc(data: bytes, table: Tuple[int, ...]) -> int:
    """Computes REDengine 4 64-bit CRC for archive table of contents."""
    c = 0xffffffffffffffff
    for b in data:
        c = table[(c ^ b) & 0xff] ^ (c >> 8)
    return c ^ 0xffffffffffffffff

def read_archive_metadata(path: str):
    """Parses .archive (RDAR) header, file records and segments."""
    with open(path, 'rb') as f:
        hdr = f.read(40)
        magic, ver, ipos, isize = struct.unpack('<4sIQI', hdr[:20])
        if magic != b'RDAR':
            raise ValueError(f"Invalid archive magic: {magic} in {path}")
        f.seek(ipos)
        tbytes = f.read(isize)
        foff, fsz, crc, fc, sc, dc = struct.unpack('<IIQIII', tbytes[:28])
        
        recs = []
        ptr = 28
        for _ in range(fc):
            rec = tbytes[ptr:ptr+56]
            nh, ts, num_inline, ss, se, ds, de = struct.unpack('<QQIIIII', rec[:36])
            sha1 = rec[36:56]
            recs.append((nh, ts, num_inline, ss, se, ds, de, sha1))
            ptr += 56
            
        segs = []
        for _ in range(sc):
            seg = tbytes[ptr:ptr+16]
            off, zsz, sz = struct.unpack('<QII', seg)
            segs.append((off, zsz, sz))
            ptr += 16
            
    return recs, segs

def build_patch(game_dir: str, output_path: str):
    exe_path = os.path.join(game_dir, 'bin', 'x64', 'Cyberpunk2077.exe')
    mod_path = os.path.join(game_dir, 'archive', 'pc', 'mod', 'Rus_Dub_by_DreamVoice_v5.3.1.archive')
    c_text_path = os.path.join(game_dir, 'archive', 'pc', 'content', 'lang_ru_text.archive')
    e_text_path = os.path.join(game_dir, 'archive', 'pc', 'ep1', 'lang_ru_text.archive')

    for p in [exe_path, mod_path, c_text_path, e_text_path]:
        if not os.path.isfile(p):
            raise FileNotFoundError(f"Required file not found: {p}")

    print("[*] Extracting CRC table from executable...")
    crc_table = get_crc_table(exe_path)

    print("[*] Reading DreamVoice mod entries...")
    mod_recs, _ = read_archive_metadata(mod_path)
    mod_hashes = set(r[0] for r in mod_recs)

    print("[*] Reading vanilla 2.50 text archives...")
    c_recs, c_segs = read_archive_metadata(c_text_path)
    e_recs, e_segs = read_archive_metadata(e_text_path)

    entries_to_pack = []

    # Read conflicting files from basegame content
    with open(c_text_path, 'rb') as f:
        for nh, ts, num_inline, ss, se, ds, de, sha1 in c_recs:
            if nh in mod_hashes:
                off, zsz, sz = c_segs[ss]
                f.seek(off)
                entries_to_pack.append({
                    'nh': nh, 'ts': ts, 'sha1': sha1,
                    'zsz': zsz, 'sz': sz, 'data': f.read(zsz)
                })

    # Read conflicting files from EP1 Phantom Liberty
    with open(e_text_path, 'rb') as f:
        for nh, ts, num_inline, ss, se, ds, de, sha1 in e_recs:
            if nh in mod_hashes:
                off, zsz, sz = e_segs[ss]
                f.seek(off)
                entries_to_pack.append({
                    'nh': nh, 'ts': ts, 'sha1': sha1,
                    'zsz': zsz, 'sz': sz, 'data': f.read(zsz)
                })

    print(f"[*] Found {len(entries_to_pack)} conflicting text files to patch.")
    entries_to_pack.sort(key=lambda x: x['nh'])

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    print(f"[*] Writing patch archive: {output_path}")

    with open(output_path, 'wb') as f:
        f.write(b'\x00' * 172)
        
        file_segments = []
        file_records = []
        for i, entry in enumerate(entries_to_pack):
            seg_off = f.tell()
            f.write(entry['data'])
            file_segments.append((seg_off, entry['zsz'], entry['sz']))
            rec = struct.pack('<QQIIIII', entry['nh'], entry['ts'], 0, i, i + 1, 0, 0) + entry['sha1']
            file_records.append(rec)
        
        pos = f.tell()
        if pos % 8 != 0:
            f.write(b'\xd9' * (8 - (pos % 8)))
            
        index_pos = f.tell()
        fc = len(file_records)
        sc = len(file_segments)
        table_size = 28 + (56 * fc) + (16 * sc)
        
        toc_buf = bytearray()
        toc_buf += struct.pack('<IIQ', 8, table_size, 0)
        toc_buf += struct.pack('<III', fc, sc, 0)
        for r in file_records:
            toc_buf += r
        for off, zsz, sz in file_segments:
            toc_buf += struct.pack('<QII', off, zsz, sz)
            
        crc_val = compute_crc(toc_buf[16:], crc_table)
        toc_buf[8:16] = struct.pack('<Q', crc_val)
        
        index_size = len(toc_buf)
        f.write(toc_buf)
        
        pos = f.tell()
        if pos % 8 != 0:
            f.write(b'\xd9' * (8 - (pos % 8)))
            
        filesize = f.tell()
        f.seek(0)
        hdr = struct.pack('<4sIQIQIQ', b'RDAR', 12, index_pos, index_size, 0, 0, filesize)
        f.write(hdr)

    print(f"[+] Done! Archive size: {filesize} bytes (~{filesize // (1024*1024)} MB).")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Build DreamVoice Phantom Liberty Text Fix for CP2077 2.50+")
    parser.add_argument('--game-dir', default=r'E:\game\Cyberpunk.2077.Repack.by.HardwareMining\by Decepticon\Cyberpunk 2077', help="Game installation root folder")
    parser.add_argument('--out', default='###_DreamVoice_Fix_Text_2.50.archive', help="Output archive path")
    args = parser.parse_args()
    build_patch(args.game_dir, args.out)
