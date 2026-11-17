#!/usr/bin/env python3
"""Write two-staff benchmark files with dense ordered and grouped control events (benchmark-48/96/192.mei)."""

import pathlib

HERE = pathlib.Path(__file__).resolve().parent

for count in (48, 96, 192):
    measures = []
    for m in range(1, count + 1):
        change = ""
        if m % 8 == 1 and m > 1:
            order = "dynam dir tempo" if m % 2 else "tempo dir dynam"
            change = f'<scoreDef aboveorder="{order}"/>'
        staves = ""
        for s in (1, 2):
            notes = "".join(
                f'<note xml:id="m{m}s{s}n{k}" pname="{"cdefgab"[k]}" oct="{5 if s == 1 else 3}" dur="4"/>' for k in range(4)
            )
            staves += f'<staff n="{s}"><layer n="1">{notes}</layer></staff>'
        controls = ""
        for s in (1, 2):
            for k in range(4):
                group = m * 10 + k
                start = f'staff="{s}" startid="#m{m}s{s}n{k}"'
                controls += f'<dynam {start} place="above" vgrp="{group}">p</dynam>'
                controls += f'<dir {start} place="above" vgrp="{group}">dolce</dir>'
                controls += f'<tempo {start} place="above">Lento</tempo>'
                controls += f'<fermata {start} place="below" vgrp="{group + 5000}"/>'
                controls += f'<dynam {start} place="below" vgrp="{group + 5000}">f</dynam>'
        measures.append(f'{change}<measure n="{m}">{staves}{controls}</measure>')
    (HERE / f"benchmark-{count}.mei").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<mei xmlns="http://www.music-encoding.org/ns/mei" meiversion="5.1"><meiHead><fileDesc><titleStmt>'
        f"<title>Staff-item order benchmark ({count} measures)</title></titleStmt><pubStmt/></fileDesc></meiHead>"
        '<music><body><mdiv><score><scoreDef meter.count="4" meter.unit="4" aboveorder="dynam dir tempo" '
        'beloworder="fermata dynam"><staffGrp><staffDef n="1" lines="5" clef.shape="G" clef.line="2"/>'
        '<staffDef n="2" lines="5" clef.shape="F" clef.line="4"/></staffGrp></scoreDef>'
        f'<section>{"".join(measures)}</section></score></mdiv></body></music></mei>\n'
    )
