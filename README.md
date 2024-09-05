# Dutch Plurals and Articles

[![DOI](https://zenodo.org/badge/694572139.svg)](https://zenodo.org/doi/10.5281/zenodo.10491765)

This repository contains a list of manually annotated/verified Dutch plural singular/lemma combinations. This was done by Henk Pander Maat and can be found under `input.tsv`.

It also contains a list of articles at `gender.tsv`.

Using `transform.py` these files can be converted into `output.tsv` which is a file which can be used as input for [`froggen`](https://frognlp.readthedocs.io/en/latest/advanced.html).

## Wiktionary

The machine-readable Wiktionary data from [Tatu Ylonen](https://kaikki.org/dictionary/Dutch/pos-noun/index.html) was used to expand these list and make an initial file containing the articles.

## Considerations for Article Usage

For uncapitalized words an article can often be easily determined by a native speaker. If there is none (for example for months) it is left blank. For capitalized words there is more room for ambiguity. Rivers, lakes, seas, mountains, deserts, inhabitants, streets, squares and languages have articles. Acronyms, cars and devices also generally have them. Countries, cities, regions and brand names generally do not.
Nominal adjectives should be recorded as adjectives

## Nominal Adjectives

Words which can be used as a nominal adjectives are tagged as `'ADJ'` instead of `'N'`. If they can also be used as normal nouns those tags will also be added to the output file. For example compare _"Het **Nederlands** is een Germaanse taal."_ (`N`) versus _"Dat is typisch **Nederlands**."_ (`ADJ`).
