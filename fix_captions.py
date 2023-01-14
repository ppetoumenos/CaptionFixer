#!/usr/bin/env python3
import re

from vtt import VTT

_COMMON_SUBS = [
        ('c plus plus', 'C++'),
        ('C plus plus', 'C++'),
        ('ar ey double eye', 'RAII')]

def load_file(fname):
    with open(fname, 'r', encoding='utf-8') as fin:
        txt = fin.read()
        txt = re.sub(r'\s+', ' ', txt)
        for pattern_src, pattern_target in _COMMON_SUBS:
            txt = txt.replace(pattern_src, pattern_target)
    return txt

def main(fname1, fname2):
    captions = VTT(fname1)
    captions.repair(load_file(fname2))
    captions.serialize()

if __name__ == '__main__':
    import sys
    main(sys.argv[1], sys.argv[2])
