#!/usr/bin/env python3
"""Render the staff-item order examples and check the vertical position of their control events."""

import argparse
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent

# SVG y coordinates grow downwards: above the staff, a larger y is closer to the staff; below, a smaller one.
# Each check is (description, ids from top to bottom) or (description, "same", ids on a common baseline).
CHECKS = {
    "aboveorder-beloworder.mei": [
        ("scoreDef aboveorder: tempo closest, then dir, then dynam", ["dynam_s1", "dir_s1", "tempo_s1"]),
        ("scoreDef beloworder: dir closest, then dynam", ["dir_s1_below", "dynam_s1_below"]),
        ("staffDef aboveorder overrides scoreDef: dynam closest", ["tempo_s2", "dir_s2", "dynam_s2"]),
    ],
    "order-changes.mei": [
        ("measure 1, staffDef order: dynam closest", ["dir_m1", "dynam_m1"]),
        ("measure 2, later scoreDef order replaces it: dir closest", ["dynam_m2", "dir_m2"]),
        ("measure 3, later staffDef order: dynam closest", ["dir_m3", "dynam_m3"]),
    ],
    "vgrp-across-classes.mei": [
        ("tempo, dynam and dir share vgrp 1", "same", ["tempo_vgrp1", "dynam_vgrp1", "dir_vgrp1"]),
        ("dir within the staff stays between the staff lines", "within", ["dir_within"]),
    ],
    "octave-system-break.mei": [
        ("second system, later scoreDef order: dir below the continued octave line", ["octave#-1", "dir_m2"]),
    ],
    "octave-barline.mei": [
        ("dynam in measure 2 below the octave line from measure 1", ["octave", "dynam_m2"]),
    ],
}


def segments(svg, element_id):
    """Return the SVG of each segment of an element (one per system for spanning elements)."""
    starts = [m.start() for m in re.finditer(r'<g (?:id="%s"|class="[^"]*\bid-%s\b[^"]*")' % (element_id, element_id), svg)]
    return [svg[start:svg.find("</g>", start)] for start in starts]


def reference_y(svg, key):
    element_id, _, index = key.partition("#")
    found = segments(svg, element_id)
    if not found:
        sys.exit(f"{element_id}: element not found in the SVG output")
    segment = found[int(index) if index else 0]
    match = re.search(r'<text[^>]* y="(-?\d+)"|translate\(-?\d+, (-?\d+)\)|d="M-?\d+ (-?\d+)', segment)
    return int(next(group for group in match.groups() if group is not None))


def staff_line_range(svg, element_id):
    """Return the y range of the staff lines of the staff preceding an element."""
    position = svg.find('<g id="%s"' % element_id)
    staff = svg.rfind('class="staff"', 0, position)
    lines = [int(y) for y in re.findall(r'<path d="M-?\d+ (-?\d+) L-?\d+ \1"', svg[staff:position])[:5]]
    return min(lines), max(lines)


def evaluate(svg, check):
    if check[1] == "same":
        values = [reference_y(svg, key) for key in check[2]]
        return len(set(values)) == 1, values
    if check[1] == "within":
        top, bottom = staff_line_range(svg, check[2][0])
        value = reference_y(svg, check[2][0])
        return top <= value <= bottom, [top, value, bottom]
    values = [reference_y(svg, key) for key in check[1]]
    return all(upper < lower for upper, lower in zip(values, values[1:])), values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verovio", required=True, help="path to the Verovio command-line executable")
    parser.add_argument("--resources", required=True, help="path to the Verovio data directory")
    parser.add_argument("--out", default="/tmp/staff-item-order", help="output directory")
    args = parser.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    failures = 0
    for name, checks in CHECKS.items():
        svg_path = out / name.replace(".mei", ".svg")
        command = [args.verovio, "-r", args.resources, "--breaks", "encoded", "-o", str(svg_path), str(HERE / name)]
        subprocess.run(command, check=True, capture_output=True)
        svg = svg_path.read_text()
        for check in checks:
            passed, values = evaluate(svg, check)
            failures += not passed
            print(f"{'ok' if passed else 'FAIL':4} {name}: {check[0]} (y = {values})")
    print(f"SVG files written to {out}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
