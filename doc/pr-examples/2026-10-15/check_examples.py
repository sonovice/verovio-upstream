#!/usr/bin/env python3
"""Run reduced MusicXML/MEI import checks against a supplied Verovio CLI.
Usage: python3 check_examples.py --verovio /path/to/verovio --resources /path/to/data --topic harmony --out /tmp/check
"""
import argparse
import collections
import json
from pathlib import Path
import resource
import subprocess
import sys
from xml.etree import ElementTree as ET

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
M = '{http://www.music-encoding.org/ns/mei}'
FIXTURES = {
    'harmony': 'harmony-display-text.musicxml',
    'tempo': 'd1-direction-sound-tempo.musicxml',
    'cross-staff-octave': 'd5-cross-staff-octave-shift.musicxml',
    'midi-octave': 'midi-octave-without-end.mei',
    'midi-pedal': 'midi-pedal-without-start.mei',
    'natural': 'accid-carried-natural.musicxml',
    'natural-cross-staff': 'natural-cross-staff.musicxml',
}

def vlq(data, i):
    value = 0
    while True:
        c = data[i]; i += 1
        value = value * 128 + (c & 127)
        if not c & 128:
            return value, i

def pitches(path):
    data = path.read_bytes(); i = 8 + int.from_bytes(data[4:8], 'big'); out = []
    while i < len(data):
        end = i + 8 + int.from_bytes(data[i + 4:i + 8], 'big'); j = i + 8; status = 0
        while j < end:
            _, j = vlq(data, j); event = data[j]
            if event == 255:
                size, start = vlq(data, j + 2); j = start + size; continue
            if event in (240, 247):
                size, start = vlq(data, j + 1); j = start + size; continue
            if event & 128:
                status = event; j += 1
            kind = status & 240
            if kind == 144 and data[j + 1] > 0:
                out.append(data[j])
            j += 1 if kind in (192, 208) else 2
        i = end
    return out

def run(cli, resources, topic, out):
    src = Path(__file__).resolve().parent / FIXTURES[topic]
    out.mkdir(parents=True, exist_ok=True)
    result = {'topic': topic, 'input': src.name, 'returncodes': {}}
    for fmt in ('mei', 'svg', 'midi'):
        dst = out / ('example.' + ('mid' if fmt == 'midi' else fmt))
        proc = subprocess.run([cli, '-r', resources, '-x', '1', '--expand-never', '-t', fmt, '-o', str(dst), str(src)], capture_output=True, timeout=60)
        result['returncodes'][fmt] = proc.returncode
        (out / (fmt + '.log')).write_bytes(proc.stderr)
    root = ET.parse(out / 'example.mei').getroot()
    if topic == 'harmony':
        actual = [''.join(h.itertext()).strip() for h in root.iter(M + 'harm')]
        result.update(actual=actual, expected=['Cm', 'N.C.', '', 'C', 'Do7'])
        passed = actual == result['expected']
    elif topic == 'tempo':
        actual = [t.get('midi.bpm') for t in root.iter(M + 'tempo')]
        result.update(actual=actual, expected=['100', '60', '140'])
        passed = actual == result['expected']
    elif topic == 'natural-cross-staff':
        notes = {n.get('{http://www.w3.org/XML/1998/namespace}id'): n for n in root.iter(M + 'note')}
        actual = [notes[n].get('accid.ges') for n in ('cross-natural', 'cross-unaltered')]
        result.update(actual=actual, expected=['n', None])
        passed = actual == result['expected']
    elif topic == 'natural':
        actual = sum(a.get('accid.ges') == 'n' for a in root.iter())
        result.update(actual=actual, expected=6)
        passed = actual == 6
    else:
        midi_ok = result['returncodes']['midi'] == 0
        actual = pitches(out / 'example.mid') if midi_ok else []
        expected = [84, 88, 67, 69, 48, 84, 48, 52, 79, 83] if topic == 'cross-staff-octave' else [48, 47, 48]
        result.update(actual=actual, expected=expected)
        passed = midi_ok and collections.Counter(actual) == collections.Counter(expected)
    result['passed'] = passed and all(code == 0 for code in result['returncodes'].values())
    return result

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--verovio', required=True); ap.add_argument('--resources', required=True)
    ap.add_argument('--topic', choices=FIXTURES, required=True); ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    result = run(args.verovio, args.resources, args.topic, args.out)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result['passed'] else 1)
