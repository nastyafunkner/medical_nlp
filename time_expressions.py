#!/usr/bin/env python
# coding: utf-8

import re
import spacy
import pandas as pd
from spacy.tokens import Doc
from yargy import Parser, and_, not_, or_, rule
from yargy.pipelines import morph_pipeline
from yargy.predicates import caseless, dictionary, gram, gte, in_, lte, normalized, type
from yargy.tokenizer import MorphTokenizer, TokenRule


def doc_from_conllu(vocab, lines):
    """
    Convert conllu string to spacy doc
    """
    words, spaces, tags, poses, morphs, lemmas = [], [], [], [], [], []
    heads, deps = [], []
    for i in range(len(lines)):
        line = lines[i]
        parts = line.split("\t")
        id_, word, lemma, pos, tag, morph, head, dep, _1, misc = parts
        if "." in id_ or "-" in id_:
            continue
        if "SpaceAfter=No" in misc:
            spaces.append(False)
        else:
            spaces.append(True)

        id_ = int(id_) - 1
        head = (int(head) - 1) if head not in ("0", "_") else id_
        tag = pos if tag == "_" else tag
        morph = morph if morph != "_" else ""
        dep = "ROOT" if dep == "root" else dep

        words.append(word)
        lemmas.append(lemma)
        poses.append(pos)
        tags.append(tag)
        morphs.append(morph)
        heads.append(head)
        deps.append(dep)

    doc = Doc(vocab, words=words, spaces=spaces)
    for i in range(len(doc)):
        doc[i].tag_ = tags[i]
        doc[i].pos_ = poses[i]
        doc[i].dep_ = deps[i]
        doc[i].lemma_ = lemmas[i]
        doc[i].head = doc[heads[i]]
    doc.is_parsed = True
    doc.is_tagged = True

    return doc




def get_time_expressions(sentences, save=False):
    """
    Extract time expressions from list of sentences
    sentences - list of sentences
    save - use True to save result as csv file
    """

    # Add types for date and time in yargy
    DATE_RULE = TokenRule(
        "DATE",
        "([0-3]\d[-][0-3]\d[.][0-1]\d[.][0-2]\d{3})|([0-3]\d[.][0-1]\d[.][0-2]\d{3})|([0-3]\d[.][0-1]\d[.]\d\d)|(\d[.][0-1]\d[.]\d\d)|([0-1]\d[.][0-2]\d{3})|(/d[.][0-2]\d[.]\d\d)|([0-3]\d[.][0-1]\d[ ][0-2]\d{3})",
    )

    TIME_RULE = TokenRule(
        "TIME", "([0-2][0-9][.,-][0-5][0-9])(?=\D)|([0-9][.-][0-5][0-9])(?=\D)"
    )

    tokenizer = MorphTokenizer()
    tokenizer = tokenizer.add_rules(DATE_RULE)
    tokenizer = tokenizer.add_rules(TIME_RULE)

    # Add common time rules and units
    MONTHS = dictionary(
        {
            "январь",
            "февраль",
            "март",
            "апрель",
            "мая",
            "июнь",
            "июль",
            "август",
            "сентябрь",
            "октябрь",
            "ноябрь",
            "декабрь",
        }
    )

    SHORT_MONTHS = dictionary(
        {"янв", "фев", "мар", "апр", "май", "ин", "ил", "авг", "сен", "окт", "нояб", "дек"}
    )
    SEASONS = dictionary({"лето", "зима", "весна", "осень",})
    DAYTIME = dictionary({"день", "утро", "вечер", "ночь",})
    YEAR_PART = dictionary({"конец", "начало", "середина",})
    DAY = and_(gte(1), lte(31))
    MONTH = and_(gte(1), lte(12))
    YEAR = and_(gte(1), lte(99))
    YEARFULL = and_(gte(1900), lte(2020))
    HOURS = and_(gte(0), lte(23))
    MINUTES = and_(gte(0), lte(59))

    time_events = dictionary({"сегодня", "вчера", "позавчера"})
    time_dict = dictionary({"лет", "год", "г", "мес", "месяц", "неделя", "день", "ч", "л"})
    time_units = dictionary(
        {
            "год",
            "месяц",
            "неделя",
            "день",
            "час",
            "минута",
            "полугода",
            "сутки",
            "мин",
            "лет",
        }
    )
    time_regular = dictionary(
        {
            "ежедневно",
            "ежемесячно",
            "еженедельно",
            "ежегодно",
            "неоднократно",
            "впервые",
            "дважды",
        }
    )

    # Rules for time expressions
    TIME_EXP_RULE = or_(
        rule(DAY, MONTHS, YEARFULL.optional()),
        rule(YEAR_PART, MONTHS, or_(time_units, YEARFULL).optional(), time_dict.optional()),
        rule(
            type("INT"),
            dictionary({"-", ",", "–"}),
            type("INT"),
            dictionary({"-", ",", "–"}),
            type("INT"),
            time_dict,
        ),
        rule(
            type("INT"),
            dictionary({"-", ",", "–"}),
            type("INT"),
            or_(time_units, time_dict),
        ),
        rule("раз", "в", or_(type("INT"), gram("NUMR")), time_dict),
        rule(
            or_(type("INT"), gram("NUMR"), normalized("один")).optional(),
            dictionary({"раз", "р"}),
            "в",
            time_dict,
            dictionary({"-", "–"}).optional(),
            type("INT").optional(),
            time_dict.optional(),
        ),
        rule(type("INT"), time_units, "в", time_units),
        rule(
            type("INT"),
            dictionary({"-", "–"}),
            type("INT"),
            normalized("раз").optional(),
            "в",
            time_dict,
        ),
        rule(
            gram("PREP"),
            type("INT"),
            normalized("раз"),
            "в",
            type("INT"),
            "-",
            type("INT"),
            time_dict,
        ),
        rule(
            type("INT"),
            normalized("раз").optional(),
            "в",
            type("INT"),
            dictionary({"-", "–"}).optional(),
            type("INT").optional(),
            time_dict,
        ),
        rule(SEASONS, type("INT"), time_dict),
        rule(time_dict, type("INT"), "-", type("INT")),
        rule(normalized("последний"), time_dict),
        rule(gram("NUMR"), time_dict),
        rule(YEAR_PART, type("INT"), dictionary({"-", "–"}).optional(), "х"),
        rule(
            type("INT"),
            dictionary({"-", "–"}).optional(),
            dictionary({"ти", "х"}).optional(),
            time_units,
            normalized("назад").optional(),
        ),
        rule(type("INT"), time_dict, DAYTIME.optional(), type("DATE").optional()),
        rule(type("INT"), ",", type("INT"), DAYTIME, type("DATE")),
        rule(type("INT"), DAYTIME, type("DATE")),
        rule(
            dictionary({"через", "спустя"}),
            or_(type("INT"), normalized("пол")).optional(),
            time_units,
        ),
        rule(type("INT"), "и", type("INT"), time_dict),
        # c по
        rule("с", YEARFULL, time_dict, "по", YEARFULL, time_dict),
        rule(caseless("с"), or_(type("DATE"), type("TIME")), "по", type("DATE")),
        # YEARFULL
        rule(or_(MONTHS, SHORT_MONTHS, SEASONS), YEARFULL, time_dict.optional()),
        rule(YEARFULL, normalized("г").optional(), gram("PREP"), type("TIME")),
        rule(YEARFULL, dictionary({"-", ",", "–"}), YEARFULL, time_dict),
        rule(YEARFULL),
        # PREP
        rule(gram("PREP"), DAYTIME, type("DATE")),
        rule(
            gram("PREP"),
            YEAR_PART,
            YEARFULL,
            ",",
            YEAR_PART,
            YEARFULL,
            normalized("год").optional(),
        ),
        rule(gram("PREP"), YEAR_PART, YEARFULL, normalized("год").optional()),
        rule(
            gram("PREP"),
            MONTHS,
            YEARFULL,
            time_dict.optional(),
            gram("PREP"),
            MONTHS,
            YEARFULL,
            time_dict,
        ),
        rule(gram("PREP"), MONTHS, YEARFULL, time_dict),
        rule(gram("PREP"), YEAR_PART, YEARFULL),
        rule(
            gram("PREP"), MONTHS, dictionary({"-", "и", "–"}), MONTHS, YEARFULL, time_dict
        ),
        rule(gram("PREP"), normalized("нескольких"), normalized("раз"), "в", time_units),
        rule(gram("PREP"), MONTHS, or_(normalized("месяцев"), YEARFULL).optional()),
        # DATE_DATE
        rule(type("DATE"), dictionary({"-", "–"}), type("DATE")),
        # TIME_TIME
        rule(type("TIME"), dictionary({"-", "–"}), type("TIME")),
        # TIME_DATE
        rule(
            type("TIME"),
            or_(DAYTIME, dictionary({"-", "и", "–"})),
            type("DATE").optional(),
            time_dict.optional(),
        ),
        rule(type("TIME"), type("DATE")),
        # DATE_TIME
        rule(type("DATE"), "-", type("TIME")),
        rule(type("DATE"), gram("PREP"), type("TIME")),
        # TIME
        rule(type("TIME"), MONTHS, YEARFULL, time_dict),
        rule(type("TIME"), or_(time_dict, time_units)),
        rule(type("TIME")),
        # DATE
        rule(type("DATE"), time_dict.optional(), DAYTIME.optional()),
        # DAYTIME
        rule(DAYTIME, type("DATE").optional()),
        # time_events
        rule(time_events, "в", type("TIME")),
        rule(time_events, DAYTIME.optional()),
        # caseless("в")
        rule(
            caseless("в"),
            dictionary({"год", "месяц", "неделя", "день", "час", "полугода", "сутки"}),
        ),
        rule(
            caseless("в"),
            normalized("течение"),
            type("INT"),
            normalized("последних"),
            time_units,
        ),
        rule(
            caseless("в"),
            normalized("течение"),
            normalized("многих").optional(),
            time_units,
        ),
        # time_units
        rule(time_units, normalized("назад")),
        rule(dictionary({"год", "месяц", "неделя", "день", "час", "полугода", "сутки"})),
        # simple rules
        rule(YEARFULL),
        rule("сегодня"),
        rule(time_regular),
        morph_pipeline(["до сегодняшнего дня"]),
        morph_pipeline(["месяц"]),
        morph_pipeline(["в настоящее время"]),
        morph_pipeline(["во время сна"]),
        morph_pipeline(["в последние несколько месяцев"]),
        morph_pipeline(["за день до этого"]),
    )

    parser_time = Parser(TIME_EXP_RULE, tokenizer=tokenizer)
    
    TIME_EXPR = list()
    for sent in sentences:
        time_expr = list()
        for match in parser_time.findall(sent):
            s = " ".join([_.value for _ in match.tokens])
            if s not in ["в г", "г", "года"]:
                time_expr.append(s)
        TIME_EXPR.append(time_expr)

    if save:
        d = {"sentence": sentences, "time_expressions": TIME_EXPR}
        df = pd.DataFrame(data=d)
        df.to_csv("result.csv")

    return TIME_EXPR