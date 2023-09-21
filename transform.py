#!/usr/bin/env python3
output = []
with open("input.tsv", "r", encoding="utf-8-sig") as input_file:
    for line in input_file.readlines()[1:]:
        [woord, lemma, group, remarks, freq] = line.split('\t')[0:5]
        remarks = remarks.strip()
        if woord[0].isupper():
            ntype = "eigen"
        else:
            ntype = "basis"
        match remarks:
            case 'verbeterd naar -s' | \
                    'verbeterd naar -zen' | \
                    'verbeterd naar -aars' | \
                    'toegevoegd meervoud op -n' \
                    'verbeterd' \
                    'toegevoegd meervoud op -s' | \
                    'lemma moet al meervoud zijn' | \
                    '':
                getal = "meervoud"
            case 'lemma is al meervoud':
                woord = lemma
                getal = "meervoud"
            case 'meervoud bestaat niet' | 'meervoud is hetzelfde':
                woord = lemma
                getal = "enkelvoud"
        # determine graad
        if group.endswith('je') and group != 'Spanje':
            graad = "diminutief"
        else:
            graad = "basis"
        output.append((woord, lemma, ntype, getal, graad))

output.sort()

with open("output.tsv", "w", encoding="utf-8") as output_file:
    for (woord, lemma, ntype, getal, graad) in output:
        output_file.write(f"{woord}\t{lemma}\tN({ntype},{getal},{graad})\n")
