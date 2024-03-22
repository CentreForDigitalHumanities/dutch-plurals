#!/usr/bin/env python3
import json
from typing import Dict


def gender_from_template(template, key: str):
    if key not in template["args"]:
        return None

    match template["args"][key]:
        case "n":
            return "het"

        case "m" | "f" | "c" | "p":
            # p: only plural
            return "de"

        case "":
            # no article
            return "-"

        case "?" | "nl":
            return "skip"

    return None


def determine_gender(data):
    try:
        template = data["head_templates"][0]
    except KeyError:
        return "skip"
    if template["name"] in ("nl-noun", "head"):
        genders = set()
        for key in ("1", "g2"):
            gender = gender_from_template(template, key)
            if gender is not None:
                genders.add(gender)

        if "de" in genders and "het" in genders:
            return "de/het"
        elif "de" in genders:
            return "de"
        elif "het" in genders:
            return "het"
        elif "-" in genders:
            return "-"
        else:
            return "skip"

    elif template["name"] in ("nl-adj", "nl-decl-adj", "nl-proper noun", "nl-verb"):
        return "-"

    raise Exception(f"Could not parse {data['word']}")


wiki_articles: Dict[str, str] = {}
with open(
    "kaikki.org-dictionary-Dutch-by-pos-noun.json", "r", encoding="utf-8-sig"
) as wiktionary_file:
    for line in wiktionary_file.readlines():
        data = json.loads(line)
        word = data["word"]
        if " " in word:
            continue
        try:
            article = determine_gender(data)
        except:
            print(data)
            raise
        wiki_articles[word] = article
        if article == "skip":
            continue
