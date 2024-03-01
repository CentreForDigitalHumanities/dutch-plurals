#!/usr/bin/env python3
output = set()
with open("input.tsv", "r", encoding="utf-8-sig") as input_file:
    for line in input_file.readlines()[1:]:
        [woord, lemma, group, remarks, freq] = line.split('\t')[0:5]
        woord = woord.strip()
        lemma = lemma.strip()
        if ' ' in woord or ' ' in lemma:
            # skip multi words
            print('skipped ' + woord)
            continue
        remarks = remarks.strip()
        if woord[0].isupper():
            ntype = "eigen"
        else:
            ntype = "soort"
        match remarks:
            case 'verbeterd naar -s' | \
                    'verbeterd naar -zen' | \
                    'verbeterd naar -aars' | \
                    'toegevoegd meervoud op -n' \
                    'verbeterd' \
                    'toegevoegd meervoud op -s' | \
                    'lemma moet al meervoud zijn' | \
                    '':
                getal = "mv"
            case 'lemma is al meervoud':
                woord = lemma
                getal = "mv"
            case 'meervoud bestaat niet' | 'meervoud is hetzelfde':
                woord = lemma
                getal = "ev"
        # determine graad
        if group.endswith('je') and group != 'Spanje':
            graad = "dim"
        else:
            graad = "basis"

        output.add((woord, lemma, ntype, getal, graad))

with open("output.tsv", "w", encoding="utf-8") as output_file:
    for (woord, lemma, ntype, getal, graad) in sorted(output):
        output_file.write(f"{woord}\t{lemma}\tN({ntype},{getal},{graad})\n")
