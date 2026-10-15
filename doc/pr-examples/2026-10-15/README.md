# Reduced Verovio PR examples (2026-10-15)

These small MusicXML/MEI examples and generated piano benchmarks accompany independent PRs based on upstream `develop` at `37ec05f45`. They contain no production score assets. Images are generated with Verovio, rasterized with librsvg, and captioned with ImageMagick; the performance chart uses Matplotlib.

## Import and MIDI checks

Build the relevant branch with the usual CMake CLI build, then run:

```sh
python3 check_examples.py --verovio /path/to/build/verovio \
  --resources /path/to/verovio/data --topic harmony --out /tmp/harmony
```

Other topics: `tempo`, `cross-staff-octave`, `midi-octave`, `midi-pedal`, `natural`, `natural-cross-staff`. Each command exports MEI, SVG, and MIDI and asserts the expected result. The corresponding baseline is expected to fail the assertion; the incomplete-octave and unresolved-pedal baseline MIDI conversions terminate with SIGSEGV. Core dumps are disabled by the checker.

| Topic | Baseline | Changed branch |
| --- | --- | --- |
| Harmony | `Cm`, `C`, `C`, `C`, `C7` | `Cm`, `N.C.`, empty, `C`, `Do7` |
| Tempo | 100, 100, 60, 140, 140 MEI tempos | 100, 60, 140 |
| Cross-staff octave | G4/A4 sound as MIDI 79/81 | MIDI 67/69; notation unchanged |
| Incomplete octave | MIDI crashes | MIDI succeeds, pitches 48/47/48 |
| Unresolved pedal | MIDI crashes | MIDI succeeds, pitches 48/47/48 |
| Natural markers | 0 explicit gestural naturals | 6; notation and Verovio MIDI unchanged |
| Cross-staff natural markers | Missing on altered notation staff | Present only on altered notation staff |

The natural-marker change is an interoperability proposal, not a claim that Verovio's baseline MIDI is incorrect. `midi-octave-without-end.musicxml` additionally shows the import route producing the incomplete MEI control event.

## Performance

```sh
npm install
python3 make_benchmark.py
node benchmark.mjs /path/to/baseline-module.mjs --reps 7 --out benchmark-before.json
node benchmark.mjs /path/to/candidate-module.mjs --reps 7 --out benchmark-after.json
node check_outputs.mjs /path/to/baseline-module.mjs /path/to/candidate-module.mjs
```

The WASM modules must be built from the baseline and candidate revisions, using the same Emscripten toolchain and `./buildToolkit -w -M -H -m` in `emscripten/`. The pinned npm package supplies the JavaScript API wrapper only. Measurements use Node's `process.threadCpuUsage()` (Node 24+) on macOS arm64. They are the minimum of seven runs per synthetic workload: import, layout at widths 1200 and 2100, and every SVG page. Each case runs with and without `note@n`, `note@oct`, and `note@pname` additional SVG attributes. These are CPU measurements on a development computer, not mobile-device latency estimates. Phase minima are independent and need not sum to the minimum total.

`benchmark-before.json` measures `37ec05f45`; `benchmark-after.json` measures `ea13145a5`. `check_outputs.mjs` checks 46 MEI, MIDI, and SVG outputs; XML IDs, generated dates, and version strings are normalized before comparing XML. MIDI is compared unchanged.

## Custom tuning and copy semantics

`check_tuning.cpp` checks default and const getters, mutable getter compatibility, invalid input, explicit 24-EDO, deep copies, copy/move assignment, self assignment, reset, and moved-from validity. Build Verovio as a shared library, then compile the check with the same source include directories as that build, for example (macOS/Linux):

```sh
cmake -S /path/to/verovio/cmake -B /tmp/verovio-lib -DBUILD_AS_LIBRARY=ON -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/verovio-lib --parallel
V=/path/to/verovio
c++ -std=c++20 check_tuning.cpp -I"$V/include" -I"$V/include/vrv" \
  -I"$V/include/tuning-library" -I"$V/include/pugi" -I"$V/include/json" \
  -I"$V/libmei/dist" -I"$V/libmei/addons" \
  -L/tmp/verovio-lib -lverovio -Wl,-rpath,/tmp/verovio-lib -o /tmp/check-tuning
/tmp/check-tuning "$V/data" 24-edo.ascl
```

The expected invalid-input test logs an error. The ASCL definition is extracted from the public Verovio test `verovio.org/_tests/midi/005-maqam-rast-external-tuning.mei`; the 24-EDO definition credits the Ableton tuning system. `tuning-final.json` records byte-identical baseline/candidate MIDI for all seven public upstream MIDI fixtures, explicitly passing `extMeta.tuningFile` to the CLI for the two MEI fixtures that specify it.
