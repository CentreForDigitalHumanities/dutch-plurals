#!/usr/bin/env python3
from typing import Dict, List, Tuple
from transform_wiki import wiki_articles
import re

# can be: de, het, de/het, -
articles: Dict[str, str] = {}
with open("gender.tsv", "r", encoding="utf-8-sig") as gender_file:
    for line in gender_file.readlines()[1:]:
        [article, group] = line.split("\t")[0:2]
        article = article.strip()
        group = group.strip()
        if article != "?":
            articles[group] = article

# Nominal adjectives should be recorded as adjectives
# These are of the form Nederlands, Nederlandse
# Note that the first form is a noun
# The second can be both (a Dutch woman or Dutch as adjective)
# The first form can also only be an adjective form e.g. for Amerikaans
adjectives: Dict[str, Tuple[str, str]] = {}
adjectives_exempt = set()
with open("adjectives.tsv", "r", encoding="utf-8-sig") as adjectives_file:
    for line in adjectives_file.readlines()[1:]:
        [without, with_e, nominative] = line.split("\t")[0:3]
        without = without.strip()
        with_e = with_e.strip()
        if without == "-":
            adjectives_exempt.add(with_e)
        else:
            adjectives[with_e] = (without, nominative)


def guess_article(group: str):
    match = ""
    for candidate in articles.keys():
        if len(candidate) > len(match) and group.endswith(candidate):
            match = candidate

    if match != "":
        return articles[match]

    return None


# lemma, word, postag, partitions
output = set()

# word -> (ntype, getal, graad, gender)
words: Dict[str, Tuple[str, str, List[str]]] = {}

skip_gender_input = False

missing_adjectives = set()


def add_noun(woord, lemma, ntype, getal, graad, genders):
    for gender in genders:
        if gender == "":
            output.add((lemma, woord, "SPEC", ("deeleigen")))
        else:
            if woord != lemma:
                # also add singular
                output.add((lemma, lemma, "N", (ntype, "ev", graad, gender, "stan")))
            if getal == "mv":
                output.add((lemma, woord, "N", (ntype, "mv", graad)))
            else:
                output.add((lemma, woord, "N", (ntype, getal, graad, gender, "stan")))


try:
    with open("input.tsv", "r", encoding="utf-8-sig") as input_file:
        for line in input_file.readlines()[1:]:
            [woord, lemma, group, remarks, freq] = line.split("\t")[0:5]
            woord = woord.strip()
            lemma = lemma.strip()
            if group == "":
                group = lemma
            if " " in woord or " " in lemma:
                # skip multi words
                print("skipped " + woord)
                continue
            remarks = remarks.strip()
            if woord[0].isupper():
                ntype = "eigen"
            else:
                ntype = "soort"
            singular_exists = False
            match remarks:
                case (
                    "verbeterd naar -s"
                    | "verbeterd naar -zen"
                    | "verbeterd naar -aars"
                    | "toegevoegd meervoud op -n"
                    "verbeterd"
                    "toegevoegd meervoud op -s" | ""
                ):
                    getal = "mv"
                    singular_exists = woord != lemma
                case "lemma moet al meervoud zijn" | "lemma is al meervoud":
                    woord = lemma
                    getal = "mv"
                case "meervoud bestaat niet" | "meervoud is hetzelfde":
                    woord = lemma
                    getal = "ev"
            # determine graad
            if group.endswith("je") and group not in (
                "Bulgarije",
                "Dzjoengarije",
                "Italië-Spanje",
                "Kroätie-Spanje",
                "Lombardije",
                "Mantsjoerije",
                "Oranje",
                "Skopje",
                "Slowakije",
                "Spanje",
                "Turkije",
                "Walachije",
                "Zwitserland-Spanje",
            ):
                graad = "dim"
            else:
                graad = "basis"
            try:
                article = articles[group]
            except KeyError:
                try:
                    article = wiki_articles[group]
                    print(f"from wiki: {article} {group}")
                except KeyError:
                    if skip_gender_input:
                        article = "?"
                    else:
                        while True:
                            guessed = guess_article(group)
                            article = input(
                                f"is {group} [d]e, [h]et, [b]oth or [n]one? "
                                + (f"guessed {guessed} " if guessed else "")
                            )
                            if len(article) and article[0] in (
                                "d",
                                "h",
                                "b",
                                "n",
                                "-",
                                "?",
                            ):
                                break
                            elif guessed:
                                article = guessed
                                break

                # normalize article
                match article[0]:
                    case "d":
                        article = "de"
                    case "h":
                        article = "het"
                    case "b":
                        article = "de/het"
                    case "?":
                        article = "?"
                        skip_gender_input = True
                    case _:
                        article = "-"
                articles[group] = article

            match article:
                case "de":
                    genders = ["zijd"]
                case "het":
                    genders = ["onz"]
                case "de/het":
                    # add both
                    genders = ["onz", "zijd"]
                case _:
                    genders = [""]

            words[woord] = (ntype, getal, graad, genders)
            if getal == "mv" and singular_exists:
                words[lemma] = (ntype, "ev", graad, genders)

            adjective = False
            if (
                "zijd" in genders
                and graad != "dim"
                and (re.match(r"^[A-Z].*e$", lemma) or lemma in adjectives)
            ):
                adjective = True
                for exempt in adjectives_exempt:
                    if lemma.endswith(exempt):
                        adjective = False
                        break
            if adjective:
                if lemma not in adjectives:
                    missing_adjectives.add(lemma)
                # add the plural form if it exists
                if getal == "mv":
                    output.add((lemma, woord, "N", (ntype, "mv", graad)))
            else:
                add_noun(woord, lemma, ntype, getal, graad, genders)
finally:
    with open("gender.tsv", "w", encoding="utf-8") as gender_file:
        gender_file.write("article\tgroup\n")
        for group in sorted(articles.keys()):
            article = articles[group]
            gender_file.write(f"{article}\t{group}\n")

# adjectives are done separately
for with_e, (without, nominative) in adjectives.items():
    if "E" not in nominative:
        output.add((without, with_e, "ADJ", ("prenom", "basis", "met-e", "stan")))
    if "Z" not in nominative:
        output.add((without, without, "ADJ", ("prenom", "basis", "zonder")))

    try:
        if "e" in nominative:
            ntype, getal, graad, genders = words[with_e]
            add_noun(with_e, with_e, ntype, getal, graad, genders)
    except KeyError:
        print(f"Missing {with_e} in input")

    try:
        if "z" in nominative:
            ntype, getal, graad, genders = words[without]
            add_noun(without, without, ntype, getal, graad, genders)
    except KeyError:
        print(f"Missing {without} in input")

if missing_adjectives:
    print("Missing adjectives:")

for adjective in missing_adjectives:
    guess = re.sub(r"e$", "", adjective)
    if guess.endswith("nes") or guess.endswith("res") or guess.endswith("les"):
        guess = guess[0:-2] + "ees"
    print(guess + "\t" + adjective + "\t??")

with open("output.tsv", "w", encoding="utf-8") as output_file:
    for lemma, woord, postag, partitions in sorted(output):
        if not isinstance(partitions, tuple):
            # work-around for single values
            partitions = [partitions]

        output_file.write(f"{woord}\t{lemma}\t{postag}({','.join(partitions)})\n")
