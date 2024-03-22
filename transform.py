#!/usr/bin/env python3
from typing import Dict
from transform_wiki import wiki_articles

# can be: de, het, de/het, -
articles: Dict[str, str] = {}
with open("gender.tsv", "r", encoding="utf-8-sig") as gender_file:
    for line in gender_file.readlines()[1:]:
        [article, group] = line.split("\t")[0:2]
        article = article.strip()
        group = group.strip()
        if article != "?":
            articles[group] = article


def guess_article(group: str):
    match = ""
    for candidate in articles.keys():
        if len(candidate) > len(match) and group.endswith(candidate):
            match = candidate

    if match != "":
        return articles[match]

    return None


output = set()
skip_gender_input = False
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
            match remarks:
                case (
                    "verbeterd naar -s"
                    | "verbeterd naar -zen"
                    | "verbeterd naar -aars"
                    | "toegevoegd meervoud op -n"
                    "verbeterd"
                    "toegevoegd meervoud op -s" | "lemma moet al meervoud zijn" | ""
                ):
                    getal = "mv"
                case "lemma is al meervoud":
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
                    gender = "zijd"
                case "het":
                    gender = "onz"
                case "de/het":
                    gender = "onz"
                    # add both
                    output.add((woord, lemma, ntype, getal, graad, "zijd"))
                case _:
                    gender = ""
            output.add((woord, lemma, ntype, getal, graad, gender))
finally:
    with open("gender.tsv", "w", encoding="utf-8") as gender_file:
        gender_file.write("article\tgroup\n")
        for group in sorted(articles.keys()):
            article = articles[group]
            gender_file.write(f"{article}\t{group}\n")

with open("output.tsv", "w", encoding="utf-8") as output_file:
    for woord, lemma, ntype, getal, graad, gender in sorted(output):
        if gender == "":
            output_file.write(f"{woord}\t{lemma}\tSPEC(deeleigen)\n")
        else:
            output_file.write(
                f"{woord}\t{lemma}\tN({ntype},{getal},{graad},{gender},stan)\n"
            )
