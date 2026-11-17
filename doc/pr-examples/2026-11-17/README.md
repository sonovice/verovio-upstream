# Reduced Verovio PR examples (2026-11-17)

These small MEI examples and generated benchmarks accompany the staff-item order and vertical group PR (#4407), based on upstream `develop` at `dd5cea020`. They contain no production score assets. Images are generated with Verovio, rasterized with librsvg, and captioned with ImageMagick.

The examples use the element-based header of the `verovio.org` test corpus and validate against the MEI 6.0-dev Relax NG schema.

## Layout checks

Build the relevant branch with the usual CMake CLI build, then run:

```sh
python3 check_staff_items.py --verovio /path/to/build/verovio \
  --resources /path/to/verovio/data --out /tmp/staff-items
```

The checker renders each example with `--breaks encoded` and compares the SVG y positions of the control events. It exits with status 1 if any check fails.

| Example | Check | `develop` | Previous PR head `7a4ed2a62` | PR head |
| --- | --- | --- | --- | --- |
| `aboveorder-beloworder.mei` | `scoreDef@aboveorder` | fail | ok | ok |
| | `scoreDef@beloworder` | fail | ok | ok |
| | `staffDef@aboveorder` overrides `scoreDef` | ok¹ | ok | ok |
| `order-changes.mei` | initial `staffDef` order | ok¹ | ok | ok |
| | later `scoreDef` order replaces it | fail | fail | ok |
| | later `staffDef` order | ok¹ | ok | ok |
| `vgrp-across-classes.mei` | tempo, dynam and dir share `vgrp="1"` | fail | ok | ok |
| | dir with `place="within"` stays in the staff | ok | fail | ok |
| `octave-system-break.mei` | continued octave line follows the order of the second system | fail | fail | ok |
| `octave-barline.mei` | dynam in measure 2 below an octave line from measure 1 | ok¹ | fail | ok |

¹ The requested order coincides with the legacy class order.

The previous PR head is measured on its rebase onto `dd5cea020`, which is identical to the merge of `upstream/develop` into it.

In `vgrp-across-classes.mei`, explicit groups align the reference positions of their members. For the fermata below the staff, this is the top of the glyph, which is therefore aligned with the baseline of `rit.`.

## Performance

```sh
python3 make_benchmark.py
/path/to/build/verovio -r /path/to/verovio/data --breaks none -o /tmp/benchmark.svg benchmark-192.mei
```

`make_benchmark.py` writes two-staff files with 48, 96, and 192 measures in a single system, with five ordered control events per beat and staff, explicit vertical groups, and an order change every eight measures. Release timings on macOS arm64, minimum of five runs:

| Measures | `develop` | PR head | PR head with #4573 |
| ---: | ---: | ---: | ---: |
| 48 | 0.15 s | 0.29 s | 0.13 s |
| 96 | 0.45 s | 1.00 s | 0.34 s |
| 192 | 1.58 s | 3.77 s | 1.11 s |

The SVG output of the PR head is identical with and without #4573.
