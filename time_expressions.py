#!/usr/bin/env python
# coding: utf-8

import stanza
import dateparser
import rutimeparser
from datetime import datetime
from spacy_stanza import StanzaLanguage
from dateparser.search import search_dates
from yargy import Parser, and_, not_, or_, rule
from yargy.pipelines import morph_pipeline
from yargy.predicates import caseless, dictionary, gram, gte, in_, lte, normalized, type
from yargy.tokenizer import MorphTokenizer, TokenRule

# Add types for date and time in yargy
DATE_RULE = TokenRule(
    "DATE",
    "([0-3]\d[-][0-3]\d[.][0-1]\d[.][0-2]\d{3})|([0-3]\d[.][0-1]\d[.][0-2]\d{3})|([0-3]\d[.][0-1]\d[.]\d\d)|(\d[.][0-1]\d[.]\d\d)|([0-1]\d[.][0-2]\d{3})|(/d[.][0-2]\d[.]\d\d)|([0-3]\d[.][0-1]\d[ ][0-2]\d{3})",
)

TIME_RULE = TokenRule(
    "TIME", "([0-2][0-9][.,-][0-5][0-9])(?=\D)|([0-9][.-][0-5][0-9])(?=\D)"
)

tokenizer = MorphTokenizer()
tokenizer = tokenizer.add_rules(TIME_RULE)
tokenizer = tokenizer.add_rules(DATE_RULE)

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
        "янв",
        "фев",
        "мар",
        "апр",
        "май",
        "ин",
        "ил",
        "авг",
        "сен",
        "окт",
        "нояб",
        "дек",
    }
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
        "г",
        "мес",
        "ч",
        "л",
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


def extract(sentences):
    """
    Extract time expressions from list of sentences
    sentences - list of sentences
    return - list of time expressions
    """

    # Rules for time expressions
    TIME_EXP_RULE = or_(
        rule(DAY, MONTHS, YEARFULL.optional()),
        rule(
            YEAR_PART,
            MONTHS,
            or_(time_units, YEARFULL).optional(),
            time_units.optional(),
        ),
        rule(
            gram("PREP").optional(),
            type("INT"),
            dictionary({"-", ",", "–"}),
            type("INT"),
            dictionary({"-", ",", "–"}),
            type("INT"),
            time_units,
        ),
        rule(
            normalized("через").optional(),
            type("INT"),
            dictionary({"-", ",", "–"}),
            type("INT"),
            or_(time_units, time_units),
        ),
        rule("раз", "в", or_(type("INT"), gram("NUMR")), time_units),
        rule(
            or_(type("INT"), gram("NUMR"), normalized("один")).optional(),
            dictionary({"раз", "р"}),
            "в",
            time_units,
            dictionary({"-", "–"}).optional(),
            type("INT").optional(),
            time_units.optional(),
        ),
        rule(type("INT"), time_units, "в", time_units),
        rule(
            type("INT"),
            dictionary({"-", "–"}),
            type("INT"),
            normalized("раз").optional(),
            "в",
            time_units,
        ),
        rule(
            gram("PREP").optional(),
            type("INT"),
            normalized("раз"),
            "в",
            type("INT"),
            dictionary({"-", "–"}).optional(),
            type("INT").optional(),
            time_units,
        ),
        rule(SEASONS, type("INT"), time_units),
        rule(time_units, type("INT"), dictionary({"-", "–"}), type("INT")),
        rule(normalized("последний"), time_units),
        rule(
            gram("PREP").optional(),
            normalized("течении").optional(),
            normalized("последних").optional(),
            gram("NUMR"),
            time_units,
            normalized("назад").optional(),
        ),
        rule(YEAR_PART, type("INT"), dictionary({"-", "–"}).optional(), "х"),
        rule(
            gram("PREP").optional(),
            normalized("течении").optional(),
            normalized("последних").optional(),
            type("INT"),
            dictionary({"-", "–"}).optional(),
            dictionary({"ти", "х"}).optional(),
            time_units,
            normalized("назад").optional(),
        ),
        rule(
            gram("PREP").optional(),
            normalized("течении").optional(),
            type("INT"),
            time_units,
            DAYTIME.optional(),
            type("DATE").optional(),
            normalized("назад").optional(),
        ),
        rule(type("INT"), ",", type("INT"), DAYTIME, type("DATE")),
        rule(type("INT"), DAYTIME, type("DATE")),
        rule(
            dictionary({"через", "спустя"}),
            or_(type("INT"), normalized("пол")).optional(),
            time_units,
        ),
        rule(type("INT"), "и", type("INT"), time_units),
        # c по
        rule("с", YEARFULL, time_units, "по", YEARFULL, time_units),
        rule(caseless("с"), or_(type("DATE"), type("TIME")), "по", type("DATE")),
        # YEARFULL
        rule(or_(MONTHS, SEASONS), YEARFULL, time_units.optional()),
        rule(YEARFULL, normalized("г").optional(), gram("PREP"), type("TIME")),
        rule(YEARFULL, dictionary({"-", ",", "–"}), YEARFULL, time_units),
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
            time_units.optional(),
            gram("PREP"),
            MONTHS,
            YEARFULL,
            time_units,
        ),
        rule(gram("PREP"), MONTHS, YEARFULL, time_units),
        rule(gram("PREP"), YEAR_PART, YEARFULL),
        rule(
            gram("PREP"),
            MONTHS,
            dictionary({"-", "и", "–"}),
            MONTHS,
            YEARFULL,
            time_units,
        ),
        rule(
            gram("PREP"), normalized("нескольких"), normalized("раз"), "в", time_units
        ),
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
            time_units.optional(),
        ),
        rule(type("TIME"), type("DATE")),
        # DATE_TIME
        rule(type("DATE"), "-", type("TIME")),
        rule(type("DATE"), gram("PREP"), type("TIME")),
        # DATE
        rule(
            gram("PREP").optional(),
            type("DATE"),
            time_units.optional(),
            DAYTIME.optional(),
        ),
        # TIME
        rule(type("TIME"), MONTHS, YEARFULL, time_units),
        rule(type("TIME"), or_(time_units, time_units)),
        rule(type("TIME")),
        # DAYTIME
        rule(DAYTIME, type("DATE").optional()),
        # time_events
        rule(time_events, "в", type("TIME")),
        rule(time_events, DAYTIME.optional()),
        # caseless("в")
        rule(
            caseless("в"),
            normalized("последние").optional(),
            normalized("несколько").optional(),
            dictionary({"год", "месяц", "неделя", "день", "час", "полугода", "сутки"}),
        ),
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
        rule(
            gram("PREP").optional(),
            normalized("течении").optional(),
            dictionary({"год", "месяц", "неделя", "день", "час", "полугода", "сутки"}),
        ),
        # simple rules
        rule(YEARFULL),
        rule("сегодня"),
        rule(time_regular),
        morph_pipeline(["до сегодняшнего дня"]),
        morph_pipeline(["месяц"]),
        morph_pipeline(["в настоящее время"]),
        morph_pipeline(["во время сна"]),
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

    return TIME_EXPR


def normalize(time_expressions):
    """
    normalize time expressions
    time expressions - list of time_expressions
    return - list of normalized time expressions
    """
    
    SEASONS_DATE = {"лето": '01.06.', "зима": '01.12.', "весна": '01.03.', "осень": '01.09.', "конец": '01.12.', "начало": '01.01.', "середина": '01.06.'}
    daytime = ["день", "утро", "вечер", "ночь",]
    YEAR_PART = dictionary({"конец", "начало", "середина", "лето", "зима", "весна", "осень"})
    MONTHS_DATE = {
        "январь": '01.',
        "февраль": '02.',
        "март": '03.',
        "апрель": '04.',
        "мая": '05.',
        "июнь": '06.',
        "июль": '07.',
        "август": '08.',
        "сентябрь": '09.',
        "октябрь": '10.',
        "ноябрь": '11.',
        "декабрь": '12.',
        "янв": '01.',
        "фев": '02.',
        "мар": '03.',
        "апр": '04.',
        "май": '05.',
        "ин": '06.',
        "ил": '07.',
        "авг": '08.',
        "сен": '09.',
        "окт": '10.',
        "нояб": '11.',
        "дек": '12.',
    }

    YEARFULLPART_RULE = rule(YEAR_PART, YEARFULL)
    YEARPART_RULE = rule(YEAR_PART, YEAR)
    MONTHS_RULE = rule(MONTHS, '-', MONTHS, YEARFULL)
    YEARS_RULE = rule(type('INT'), dictionary({"–", "-"}).optional(), normalized("ти").optional(), 'лет')

    rules = [YEARPART_RULE, YEARFULLPART_RULE, MONTHS_RULE,YEARS_RULE]
    
    snlp = stanza.Pipeline(lang="ru")
    nlp = StanzaLanguage(snlp)

    NORM_TIME_EXPR = list()
    for time_expression in time_expressions:
        norm_time_exps = list()
        if isinstance(time_expression, str):
            time_expression = [time_expression]
        for expr in time_expression:
            norm_time_exp = list()
            normal_expr = list()
            for word in nlp(expr):
                if (word.pos_ not in ['PREP', 'ADP', 'VERB']) and (word.lemma_.strip() not in ['год', 'месяц', 'день']):
                    if word.lemma_.strip() in daytime:
                        normal_expr.append(str(word))
                    else:
                        normal_expr.append(word.lemma_.strip())
                if str(word) == 'лет':
                    normal_expr.append(str(word))

            normal_expr = ' '.join(normal_expr)
            
            for r in rules:
                s = list()
                parser = Parser(r, tokenizer=tokenizer)
                for match in parser.findall(normal_expr):
                    s = [_.value for _ in match.tokens]
                    if r is YEARPART_RULE:
                        norm_time_exp.append(datetime.strptime(SEASONS_DATE[s[0]]+s[1], '%d.%m.%y'))
                    if r is YEARFULLPART_RULE:
                        norm_time_exp.append(datetime.strptime(SEASONS_DATE[s[0]]+s[1], '%d.%m.%Y'))
                    if r is MONTHS_RULE:
                        norm_time_exp.append(datetime.strptime(MONTHS_DATE[s[0]]+s[-1], '%m.%Y'))
                        norm_time_exp.append(datetime.strptime(MONTHS_DATE[s[2]]+s[-1], '%m.%Y'))
                    if r is YEARS_RULE and s:
                        norm_time_exp.append(None)
                        
            if not norm_time_exp:
                try:
                    norm_time_exp = dateparser.parse(normal_expr, settings={'PREFER_DAY_OF_MONTH': 'first'})
                except:
                    pass
                        
            if not norm_time_exp:
                try:
                    norm_time_exp = search_dates(normal_expr, settings={'PREFER_DAY_OF_MONTH': 'first'})
                    for i in range(len(norm_time_exp)):
                        norm_time_exp[i] = norm_time_exp[i][1]
                except:
                    pass
                
            if not norm_time_exp:
                try:
                    norm_time_exp = rutimeparser.parse(normal_expr)
                except:
                    pass
                    
            norm_time_exps.append(norm_time_exp)
        NORM_TIME_EXPR.append(norm_time_exps)

    return NORM_TIME_EXPR