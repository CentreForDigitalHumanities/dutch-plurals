#!/usr/bin/env python3
from typing import Dict, List, Set

frog_entries: Dict[str, Set[str]] = {}
output_entries: Dict[str, Set[str]] = {}

with open(
    "../frogdata/config/nld/Frog.mbt.1.1.lex.ambi.05", "r", encoding="utf-8-sig"
) as frog_lex:
    for line in frog_lex.readlines():
        [word, tags] = line.split(" ", 1)
        tag_set = set()
        for tag in tags.strip().split(";"):
            if not tag.startswith("WW"):
                tag_set.add(tag)
        frog_entries[word] = tag_set

with open("output.tsv", "r", encoding="utf-8-sig") as output:
    for line in output.readlines():
        [word, lemma, tag] = line.strip().split("\t")
        try:
            output_entries[word].add(tag)
        except KeyError:
            output_entries[word] = set([tag])

missing_in_output: List[str] = []
new_entries: List[str] = []
identical_entries: List[str] = []
differing_entries: List[str] = []

for entry in frog_entries:
    if entry not in output_entries:
        missing_in_output.append(entry)

for entry in output_entries:
    if entry not in frog_entries:
        new_entries.append(entry)
    elif output_entries[entry] == frog_entries[entry]:
        identical_entries.append(entry)
    else:
        differing_entries.append(entry)

print(f"{len(missing_in_output)} entries not in output")
print(f"{len(new_entries)} new entries")
print(f"{len(identical_entries)} identical entries")
print(f"{len(differing_entries)} differing entries")
