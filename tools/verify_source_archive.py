#!/usr/bin/env python3
"""Inspect archive metadata/hashes without extracting or running anything."""
import hashlib,sys,zipfile
from pathlib import PurePosixPath
BAD_EXT={'.vsb','.exe','.dll','.com','.bat','.cmd','.scr','.msi','.elf','.bin','.so','.dylib','.pyd','.ps1'}
ALLOWED_EXT={'.c','.h','.s','.ld','.sh','.py','.md','.txt','.json','.sha256','.html'}
def verify(p):
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None,'ZIP CRC mismatch'
  names=z.namelist()
  assert len(names)==len(set(names)), 'duplicate file names'
  assert 'MANIFEST.sha256' in names,'missing manifest'
  entries={}
  for info in z.infolist():
   n=info.filename; q=PurePosixPath(n)
   assert n and not n.startswith('/') and not n.startswith('\\') and '..' not in q.parts and '\\' not in n, f'unsafe path {n}'
   assert not info.is_dir(),f'unexpected directory entry {n}'
   assert q.suffix.lower() not in BAD_EXT, f'forbidden extension {n}'
   assert q.suffix.lower() in ALLOWED_EXT, f'unknown file type {n}'
   assert not (info.external_attr >> 16) & 0o111, f'executable bit forbidden {n}'
   assert (info.external_attr >> 16) & 0o170000 != 0o120000, f'symlink forbidden {n}'
   assert info.file_size < 500000, f'unexpected large file {n}'
   entries[n]=hashlib.sha256(z.read(info)).hexdigest()
  print('Archive path/CRC/types/executable-bits PASS')
  for line in z.read('MANIFEST.sha256').decode().splitlines():
   if not line.strip(): continue
   h,n=line.split('  ',1)
   assert n in entries and entries[n]==h,f'hash mismatch {n}'
  assert len(entries)-1==len(z.read('MANIFEST.sha256').decode().splitlines()),'manifest missing files'
  print('SHA256 of every file PASS;',len(entries),'source/report files; zero VSB/exe/bin/elf')
if __name__=='__main__':
 assert len(sys.argv)==2,'usage: python verify_source_archive.py ARCHIVE.zip'
 verify(sys.argv[1])
