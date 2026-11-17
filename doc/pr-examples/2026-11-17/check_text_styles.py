#!/usr/bin/env python3
"""Render staffdef-text-styles.mei and check the text styles of its syllables and directions."""

import argparse
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent

# Expected font style and weight of each element. Staff 1 inherits the scoreDef text styles; staff 2 overrides them in
# its staffDef. The scoreDef change before measure 2 makes the lyrics of both staves bold.
EXPECTED = {
    "syl_m1s1": ("italic", None),
    "syl_m1s2": ("normal", None),
    "dir_m1s1": ("normal", None),
    "dir_m1s2": ("italic", None),
    "syl_m2s1": ("italic", "bold"),
    "syl_m2s2": ("normal", "bold"),
    "dir_m2s1": ("normal", None),
    "dir_m2s2": ("italic", None),
}


def text_attributes(svg, element_id):
    match = re.search(r'<g id="%s"[^>]*>\s*<text([^>]*)>' % re.escape(element_id), svg)
    if not match:
        sys.exit(f"{element_id}: element not found in the SVG output")
    attributes = dict(re.findall(r'([a-z-]+)="([^"]*)"', match.group(1)))
    return attributes.get("font-style"), attributes.get("font-weight")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verovio", required=True, help="path to the Verovio command-line executable")
    parser.add_argument("--resources", required=True, help="path to the Verovio data directory")
    parser.add_argument("--out", default="/tmp/staffdef-text-styles", help="output directory")
    args = parser.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    svg_path = out / "staffdef-text-styles.svg"
    subprocess.run(
        [args.verovio, "-r", args.resources, "-o", str(svg_path), str(HERE / "staffdef-text-styles.mei")],
        check=True,
        capture_output=True,
    )
    svg = svg_path.read_text()

    failures = 0
    for element_id, expected in EXPECTED.items():
        actual = text_attributes(svg, element_id)
        status = "ok" if actual == expected else "FAIL"
        failures += status == "FAIL"
        print(f"{status:4} {element_id}: expected style={expected[0]} weight={expected[1]}, "
              f"got style={actual[0]} weight={actual[1]}")
    print(f"SVG written to {svg_path}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
