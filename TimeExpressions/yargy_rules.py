from dateutil.relativedelta import relativedelta
from yargy import Parser, and_, or_, rule
from yargy.pipelines import morph_pipeline
from yargy.predicates import caseless, dictionary, gram, gte, lte, normalized, type
from yargy.tokenizer import MorphTokenizer, TokenRule

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
time_regular = dictionary({"ежедневно", "ежемесячно", "еженедельно", "ежегодно",})

interpret_dict = {
    "лето": "01.06.",
    "зима": "01.12.",
    "весна": "01.03.",
    "осень": "01.09.",
    "конец": "01.12.",
    "начало": "01.01.",
    "середина": "01.06.",
    "январь": "01.",
    "февраль": "02.",
    "март": "03.",
    "апрель": "04.",
    "мая": "05.",
    "июнь": "06.",
    "июль": "07.",
    "август": "08.",
    "сентябрь": "09.",
    "октябрь": "10.",
    "ноябрь": "11.",
    "декабрь": "12.",
    "янва": "01.",
    "фев": "02.",
    "мар": "03.",
    "апр": "04.",
    "май": "05.",
    "ин": "06.",
    "ил": "07.",
    "авг": "08.",
    "сен": "09.",
    "окт": "10.",
    "нояб": "11.",
    "дек": "12.",
    "вечер": "21.00 ",
    "утро": "09.00 ",
    "день": "15.00 ",
    "ночь": "03.00 ",
}

relative_dict = {
    "год": relativedelta(years=1),
    "месяц": relativedelta(months=1),
    "полгода": relativedelta(months=6),
    "полугод": relativedelta(months=6),
    "неделя": relativedelta(weeks=1),
    "день": relativedelta(days=1),
    "сутки": relativedelta(days=1),
    "сегодня": relativedelta(days=0),
    "вчера": relativedelta(days=1),
    "позавчера": relativedelta(days=2),
    "час": relativedelta(hours=1),
}

TIME_EXP_RULE = or_(
    # с 2005 года по 2009 год
    rule(caseless("с"), YEARFULL, time_units, "по", YEARFULL, time_units).named(
        "rule_from_yearfull_unit_till_yearfull_unit"
    ),
    # в конце 2009 , начале 2010
    rule(caseless("в"), YEAR_PART, YEARFULL, ",", YEAR_PART, YEARFULL).named(
        "rule_in_part_yearfull_part_yearfull"
    ),
    # с 08.06.10 по 22.06.10
    rule(caseless("с"), type("DATE"), "по", type("DATE")).named(
        "rule_from_date_till_date"
    ),
    # С 08.06 по 10.06.08
    rule(caseless("с"), type("TIME"), "по", type("DATE")).named(
        "rule_from_time_till_date"
    ),
    # 2011 г в 17-00 only once
    rule(YEARFULL, normalized("г").optional(), gram("PREP"), type("TIME")).named(
        "rule_yearfull_g_prep_time"
    ),
    # 1976 - 1978 гг
    rule(YEARFULL, dictionary({"–", "-"}), YEARFULL, time_units).named(
        "rule_yearfull_yearfull_unit"
    ),
    # с начала 2000
    rule(caseless("с"), YEAR_PART, YEARFULL).named("rule_from_part_yearfull"),
    # В конце 2010
    rule(caseless("в"), YEAR_PART, YEARFULL).named("rule_in_part_yearfull"),
    # В конце 2010
    rule(gram("PREP"), YEAR_PART, YEARFULL).named("rule_prep_part_yearfull"),
    # В марте - апреле 2010 года
    rule(
        gram("PREP"), MONTHS, dictionary({"–", "-"}), MONTHS, YEARFULL, time_units
    ).named("rule_prep_month_month_yearfull_unit"),
    # в мае и июле 2010 года
    rule(gram("PREP"), MONTHS, "и", MONTHS, YEARFULL, time_units).named(
        "rule_prep_month_and_month_yearfull_unit"
    ),
    # с 9 мая 2010
    rule(caseless("с"), DAY, MONTHS, YEARFULL).named("rule_from_day_month_yearfull"),
    # 2 декабря 2010
    rule(DAY, MONTHS, YEARFULL).named("rule_day_month_yearfull"),
    # С декабря 2009 по май 2010 года
    rule(
        gram("PREP"),
        MONTHS,
        YEARFULL,
        time_units.optional(),
        gram("PREP"),
        MONTHS,
        YEARFULL,
        time_units,
    ).named("rule_prep_month_yearfull_prep_month_yearfull_unit"),
    # с апреля 2010 года
    rule(caseless("с"), MONTHS, YEARFULL, time_units).named(
        "rule_from_month_yearfull_unit"
    ),
    # В мае 2009 года
    rule(caseless("в"), MONTHS, YEARFULL, time_units).named(
        "rule_in_month_yearfull_unit"
    ),
    # от июня 2009 г
    rule(gram("PREP"), MONTHS, YEARFULL, time_units).named(
        "rule_prep_month_yearfull_unit"
    ),
    # август 2008 г
    rule(MONTHS, YEARFULL, time_units).named("rule_month_yearfull_unit"),
    # Зимой 2010
    rule(SEASONS, YEARFULL).named("rule_season_yearfull"),
    # июнь 2009
    rule(MONTHS, YEARFULL).named("rule_month_yearfull"),
    # 7 июля
    rule(DAY, MONTHS).named("rule_day_month"),
    # С конца января 2011
    rule(caseless("с"), YEAR_PART, MONTHS, YEARFULL, time_units.optional()).named(
        "rule_from_part_month_yearfull"
    ),
    # В конце июня 2010 года
    rule(caseless("в"), YEAR_PART, MONTHS, YEARFULL, time_units.optional()).named(
        "rule_in_part_month_yearfull"
    ),
    # конец февраля 2011 г
    rule(YEAR_PART, MONTHS, YEARFULL, time_units.optional()).named(
        "rule_part_month_yearfull"
    ),
    # начала января STAMP continious
    rule(YEAR_PART, MONTHS, time_units.optional()).named("rule_part_month"),
    # последние 3 - 4 дня
    rule(
        normalized("последний"),
        type("INT"),
        dictionary({"–", "-"}),
        type("INT"),
        time_units,
    ).named("rule_last_int_dash_int_unit"),
    # через 1 - 2 месяца
    rule(
        or_(caseless("через"), caseless("спустя")),
        type("INT"),
        dictionary({"–", "-"}),
        type("INT"),
        time_units,
    ).named("rule_thr_int_dash_int_unit"),
    # 1 раз в 6 мес
    rule(type("INT"), "раз", "в", or_(type("INT"), gram("NUMR")), time_units).named(
        "rule_int_times_in_int_unit"
    ),
    # раз в шесть месяцев
    rule("раз", "в", or_(type("INT"), gram("NUMR")), time_units).named(
        "rule_times_in_int_unit"
    ),
    # 1 раза в месяц – 2 месяца only once
    rule(
        type("INT"),
        normalized("раз"),
        "в",
        time_units,
        dictionary({"–", "-"}),
        type("INT"),
        time_units,
    ).named("rule_int_times_in_unit_dash_int_unit"),
    # 2 р в день
    rule(type("INT"), normalized("р"), "в", time_units).named("rule_times_in_unit"),
    # 2 раза в день
    rule(
        or_(type("INT"), gram("NUMR"), normalized("один")).optional(),
        normalized("раз"),
        "в",
        time_units,
    ).named("rule_times_in_unit"),
    # 2 - 3 раза в год
    rule(
        type("INT"),
        dictionary({"–", "-"}),
        type("INT"),
        normalized("раз"),
        "в",
        time_units,
    ).named("rule_int_dash_int_times_in_unit"),
    # 2 - 3 в месяц
    rule(type("INT"), dictionary({"–", "-"}), type("INT"), "в", time_units).named(
        "rule_int_dash_int_in_unit"
    ),
    # до 1 раза в 1 - 2 месяца
    rule(
        gram("PREP"),
        type("INT"),
        normalized("раз"),
        "в",
        type("INT"),
        dictionary({"–", "-"}),
        type("INT"),
        time_units,
    ).named("rule_prep_int_times_in_int_dash_int_unit"),
    # 1 раз в 2 - 3 дня
    rule(
        type("INT"),
        normalized("раз"),
        "в",
        type("INT"),
        dictionary({"–", "-"}),
        type("INT"),
        time_units,
    ).named("rule_int_times_in_int_dash_int_unit"),
    # С осени 2005 г
    rule(caseless("с"), SEASONS, type("INT"), time_units).named(
        "rule_from_season_int_unit"
    ),
    # Осенью 2010 года
    rule(SEASONS, type("INT"), time_units).named("rule_season_int_unit"),
    # лет 7 - 8
    rule(time_units, type("INT"), dictionary({"–", "-"}), type("INT")).named(
        "rule_unit_int_dash_int"
    ),
    # [Последний месяц
    rule(normalized("последний"), time_units).named("rule_last_unit"),
    # с 90 х годов
    rule(caseless("с"), type("INT"), "х", time_units).named("rule_from_int_h_unit"),
    # 1990 х годах STAMP only once
    rule(type("INT"), "х", time_units).named("rule_int_h_unit"),
    # конца 80 - х STAMP continious
    rule(YEAR_PART, type("INT"), dictionary({"–", "-"}).optional(), "х").named(
        "rule_part_int_dash_h"
    ),
    # с 12 - ти лет
    rule(caseless("с"), type("INT"), dictionary({"–", "-"}), "ти", time_units).named(
        "rule_from_int_dash_ti_unit"
    ),
    # 20 - ти лет STAMP continious
    rule(type("INT"), dictionary({"–", "-"}).optional(), "ти", time_units).named(
        "rule_int_dash_ti_unit"
    ),
    # Около 5 лет назад
    rule(normalized("около"), type("INT"), time_units, "назад").named(
        "rule_around_int_unit_ago"
    ),
    # 3 года назад
    rule(type("INT"), time_units, "назад").named("rule_int_unit_ago"),
    # около 2 часов ночи 17.12.2010
    rule(normalized("около"), type("INT"), time_units, DAYTIME, type("DATE")).named(
        "rule_int_unit_daytime_date"
    ),
    # 9 ч утра
    rule(type("INT"), time_units, DAYTIME).named("rule_int_unit_daytime"),
    # с утра 04.09.2010 STAMP continious
    rule(gram("PREP"), DAYTIME, type("DATE")).named("rule_prep_daytime_unit"),
    # 8 , 00 утра 26.01.10
    rule(type("INT"), ",", type("INT"), DAYTIME, type("DATE")).named(
        "rule_int_com_int_daytime_date"
    ),
    # 10 утра 21.12.2010
    rule(type("INT"), DAYTIME, type("DATE")).named("rule_int_daytime_date"),
    # 28.12.10 в 08.30
    rule(type("DATE"), gram("PREP"), type("TIME")).named("rule_date_prep_time"),
    # 12.10 года
    rule(type("TIME"), normalized("год")).named("rule_time_year"),
    # 11-00 часов
    rule(type("TIME"), time_units).named("rule_time_unit"),
    # с 4.06 – 17.06
    rule(
        caseless("с"),
        type("TIME"),
        dictionary({"."}).optional(),
        dictionary({"–", "-"}),
        type("TIME"),
    ).named("rule_from_time_dash_time"),
    # 10.00 - 11.00 only once
    rule(
        type("TIME"), dictionary({"."}).optional(), dictionary({"–", "-"}), type("TIME")
    ).named("rule_time_dash_time"),
    # С 6.12 . - 10.12.2010
    rule(
        caseless("с"),
        type("TIME"),
        dictionary({"."}).optional(),
        dictionary({"–", "-"}),
        type("DATE"),
    ).named("rule_from_time_dash_date"),
    # 7.12 - 17.12.04 only once
    rule(
        type("TIME"), dictionary({"."}).optional(), dictionary({"–", "-"}), type("DATE")
    ).named("rule_time_dash_date"),
    # сегодня в 16.00
    rule(time_events, "в", type("TIME")).named("rule_event_in_time"),
    # 10-00 часов 17.12.2010
    rule(type("TIME"), normalized("часов"), type("DATE").optional()).named(
        "rule_time_hour_date"
    ),
    # с 23-00 21.12.2010
    rule(caseless("с"), type("TIME"), type("DATE")).named("rule_from_time_date"),
    # в 11.00 24.12.10
    rule(caseless("в"), type("TIME"), type("DATE")).named("rule_in_time_date"),
    # 04-00 27.02.2011
    rule(type("TIME"), type("DATE")).named("rule_time_date"),
    # С апреля 2010
    rule(caseless("с"), MONTHS, or_(normalized("месяц"), YEARFULL)).named(
        "rule_from_month_yearfull"
    ),
    # В ноябре месяце
    rule(caseless("в"), MONTHS, or_(normalized("месяц"), YEARFULL)).named(
        "rule_in_month_yearfull"
    ),
    # до декабря 2009
    rule(gram("PREP"), MONTHS, or_(normalized("месяц"), YEARFULL)).named(
        "rule_prep_month_yearfull"
    ),
    # В апреле
    rule(gram("PREP"), MONTHS).named("rule_prep_month"),
    # 5.00 утра 24.01.2011
    rule(type("TIME"), DAYTIME, type("DATE").optional()).named(
        "rule_time_daytime_date"
    ),
    # вечером 28.12.2010
    rule(DAYTIME, type("DATE")).named("rule_daytime_date"),
    # 23.12.2010 утром
    rule(type("DATE"), DAYTIME).named("rule_date_daytime"),
    # 11-00 часов
    rule(type("TIME"), time_units).named("rule_time_unit"),
    # 17.09.2008
    rule(type("DATE").named("rule_date")),
    # 23.30
    rule(type("TIME")).named("rule_time"),
    # до нескольких раз в месяц
    rule(
        gram("PREP"), normalized("нескольких"), normalized("раз"), "в", time_units
    ).named("rule_sev_times_in_unit"),
    # спустя пол часа only once
    rule(caseless("спустя"), normalized("пол"), time_units).named("rule_aft_half_unit"),
    # через 5 минут
    rule(caseless("через"), type("INT"), time_units).named("rule_thr_int_unit"),
    # rule_around_int_h_unit_ago
    rule(
        caseless("около"),
        type("INT"),
        dictionary({"–", "-"}).optional(),
        "х",
        time_units,
        "назад",
    ).named("rule_around_int_h_unit_ago"),
    # Около 5 лет назад
    rule(caseless("около"), type("INT"), time_units, "назад").named(
        "rule_around_int_unit_ago"
    ),
    # Через четыре дня
    rule(caseless("через"), gram("NUMR"), time_units).named("rule_thr_numr_unit"),
    # Около семи лет назад
    rule(caseless("около"), gram("NUMR"), time_units, "назад").named(
        "rule_around_numr_unit_ago"
    ),
    # около пяти лет
    rule(caseless("около"), gram("NUMR"), time_units).named("rule_around_numr_unit"),
    # около 6 лет
    rule(caseless("около"), type("INT"), time_units).named("rule_around_int_unit"),
    # спустя 2 суток
    rule(caseless("спустя"), type("INT").optional(), time_units).named(
        "rule_aft_int_unit"
    ),
    # 2005 и 2010 годах
    rule(type("INT"), "и", type("INT"), time_units).named("rule_int_and_int_unit"),
    # с 1993 года
    rule(caseless("с"), YEARFULL, time_units).named("rule_from_yearfull_unit"),
    # В 2004 г
    rule(caseless("в"), YEARFULL, time_units).named("rule_in_yearfull_unit"),
    # с 51 лет
    rule(caseless("с"), type("INT"), time_units).named("rule_from_int_unit"),
    # в 49 лет
    rule(caseless("в"), type("INT"), time_units).named("rule_in_int_unit"),
    # rule_yearfull
    rule(YEARFULL).named("rule_yearfull"),
    # ежедневно
    rule(time_regular).named("rule_regular"),
    # сегодня утром
    rule(time_events, DAYTIME).named("rule_event_daytime"),
    # Сегодня
    rule(time_events).named("rule_events"),
    # более 15 лет
    rule(normalized("более"), type("INT"), time_units).named("rule_more_int_unit"),
    # в возрасте 70 лет
    rule(
        caseless("в"), normalized("возрасте").optional(), type("INT"), time_units
    ).named("rule_in_age_int_unit"),
    # в течение последних 1 , 5 месяцев
    rule(
        caseless("в"),
        normalized("течение"),
        normalized("последних"),
        type("INT"),
        ",",
        type("INT"),
        time_units,
    ).named("rule_dur_last_int_com_unit"),
    # в последние несколько дней
    rule(caseless("в"), normalized("последних"), gram("NUMR"), time_units).named(
        "rule_in_last_numr_unit"
    ),
    # В последние 2 недели
    rule(caseless("в"), normalized("последних"), type("INT"), time_units).named(
        "rule_in_last_int_unit"
    ),
    # в течении последнего месяца
    rule(
        caseless("в"), normalized("течение"), normalized("последних"), time_units
    ).named("rule_dur_last_unit"),
    # В течение 2 последних месяцев only once
    rule(
        caseless("в"),
        normalized("течение"),
        type("INT"),
        normalized("последних"),
        time_units,
    ).named("rule_dur_int_last_unit"),
    # в течении последних 5 лет
    rule(
        caseless("в"),
        normalized("течение"),
        normalized("последних"),
        type("INT"),
        time_units,
    ).named("rule_dur_last_int_unit"),
    # в течении последних пяти месяцев
    rule(
        caseless("в"),
        normalized("течение"),
        normalized("последних"),
        gram("NUMR"),
        time_units,
    ).named("rule_dur_last_numr_unit"),
    # в течении 4 - х лет
    rule(
        caseless("в"),
        normalized("течение"),
        type("INT"),
        dictionary({"–", "-"}).optional(),
        "х",
        time_units,
    ).named("rule_dur_int_h_unit"),
    # в течении последних 4 - х месяцев
    rule(
        caseless("в"),
        normalized("течение"),
        normalized("последних"),
        type("INT"),
        dictionary({"–", "-"}).optional(),
        "х",
        time_units,
    ).named("rule_dur_last_int_h_unit"),
    # в течение 5 - 7 минут
    rule(
        caseless("в"),
        normalized("течение"),
        type("INT"),
        dictionary({"–", "-"}),
        type("INT"),
        time_units,
    ).named("rule_dur_int_dash_int_unit"),
    # в течение 25-28 лет
    rule(caseless("в"), normalized("течение"), type("TIME"), time_units).named(
        "rule_dur_time_unit"
    ),
    # в течении 5 лет
    rule(caseless("в"), normalized("течение"), type("INT"), time_units).named(
        "rule_dur_int_unit"
    ),
    # в течение нескольких лет
    rule(caseless("в"), normalized("течение"), gram("NUMR"), time_units).named(
        "rule_dur_numr_unit"
    ),
    # В течение многих лет
    rule(caseless("в"), normalized("течение"), normalized("многих"), time_units).named(
        "rule_dur_many_unit"
    ),
    # В течение месяца
    rule(caseless("в"), normalized("течение"), time_units).named("rule_dur_unit"),
    # 90 - х годах
    rule(type("INT"), dictionary({"–", "-"}), "х", time_units).named(
        "rule_int_dash_h_unit"
    ),
    # последних 3 дней
    rule(caseless("в"), normalized("последних"), type("INT"), time_units).named(
        "rule_last_int_unit"
    ),
    # последних трех дней
    rule(normalized("последних"), gram("NUMR"), time_units).named(
        "rule_last_numr_unit"
    ),
    # лет 20 назад
    rule(time_units, type("INT"), "назад").named("rule_unit_int_ago"),
    # несколько дней назад
    rule(gram("NUMR"), time_units, "назад").named("rule_numr_unit_ago"),
    # несколько месяцев
    rule(gram("NUMR"), time_units).named("rule_numr_unit"),
    # 3 месяца
    rule(type("INT"), normalized("месяц")).named("rule_int_month"),
    # год назад
    rule(time_units, normalized("назад")).named("rule_unit_ago"),
    morph_pipeline(["С этого же года"]).named("rule_this_year"),
    morph_pipeline(["до сегодняшнего дня"]).named("rule_before_today"),
    morph_pipeline(["за сутки"]).named("rule_per_day"),
    morph_pipeline(["месяц"]).named("rule_month"),
    morph_pipeline(["в настоящее время"]).named("rule_now"),
    morph_pipeline(["за день до этого"]).named("rule_day_before"),
)

parser_time = Parser(TIME_EXP_RULE, tokenizer=tokenizer)

once_rules = [
    "rule_in_part_yearfull_part_yearfull",
    "rule_prep_part_yearfull",
    "rule_yearfull_g_prep_time",
    "rule_in_part_yearfull",
    "rule_prep_month_month_yearfull_unit",
    "rule_prep_month_and_month_yearfull_unit",
    "rule_day_month_yearfull",
    "rule_in_month_yearfull_unit",
    "rule_prep_month_yearfull_unit",
    "rule_month_yearfull_unit",
    "rule_season_yearfull",
    "rule_month_yearfull",
    "rule_day_month",
    "rule_in_part_month_yearfull",
    "rule_part_month_yearfull",
    "rule_season_int_unit",
    "rule_int_h_unit",
    "rule_around_int_unit_ago",
    "rule_int_unit_ago",
    "rule_int_unit_daytime_date",
    "rule_int_unit_daytime",
    "rule_int_com_int_daytime_date",
    "rule_int_daytime_date",
    "rule_date_prep_time",
    "rule_time_unit",
    "rule_event_in_time",
    "rule_time_hour_date",
    "rule_in_time_date",
    "rule_time_date",
    "rule_in_month_yearfull",
    "rule_prep_month",
    "rule_time_daytime_date",
    "rule_daytime_date",
    "rule_date_daytime",
    "rule_time_unit",
    "rule_date",
    "rule_time",
    "rule_around_int_h_unit_ago",
    "rule_around_int_unit_ago",
    "rule_thr_numr_unit",
    "rule_around_numr_unit_ago",
    "rule_int_and_int_unit",
    "rule_in_yearfull_unit",
    "rule_yearfull",
    "rule_event_daytime",
    "rule_events",
    "rule_in_age_int_unit",
    "rule_int_dash_h_unit",
    "rule_numr_unit_ago",
    "rule_unit_ago",
    "rule_day_before",
    "rule_now",
    "rule_unit_int_ago",
    "rule_time_year",
]

continious_rules = [
    "rule_from_yearfull_unit_till_yearfull_unit",
    "rule_from_date_till_date",
    "rule_from_time_till_date",
    "rule_yearfull_yearfull_unit",
    "rule_from_part_yearfull",
    "rule_prep_part_yearfull",
    "rule_from_day_month_yearfull",
    "rule_prep_month_yearfull_prep_month_yearfull_unit",
    "rule_from_month_yearfull_unit",
    "rule_from_part_month_yearfull",
    "rule_part_month",
    "rule_last_int_dash_int_unit",
    "rule_from_season_int_unit",
    "rule_unit_int_dash_int",
    "rule_last_unit",
    "rule_from_int_h_unit",
    "rule_part_int_dash_h",
    "rule_from_int_dash_ti_unit",
    "rule_int_dash_ti_unit",
    "rule_prep_daytime_unit",
    "rule_from_time_dash_time",
    "rule_time_dash_time",
    "rule_from_time_dash_date",
    "rule_time_dash_date",
    "rule_from_time_date",
    "rule_from_month_yearfull",
    "rule_prep_month_yearfull",
    "rule_around_numr_unit",
    "rule_around_int_unit",
    "rule_from_yearfull_unit",
    "rule_from_int_unit",
    "rule_in_int_unit",
    "rule_more_int_unit",
    "rule_dur_last_int_com_unit",
    "rule_last_numr_unit",
    "rule_last_int_unit",
    "rule_dur_last_unit",
    "rule_dur_int_last_unit",
    "rule_dur_last_int_unit",
    "rule_dur_last_numr_unit",
    "rule_dur_int_h_unit",
    "rule_dur_last_int_h_unit",
    "rule_dur_int_dash_int_unit",
    "rule_dur_time_unit",
    "rule_dur_int_unit",
    "rule_dur_numr_unit",
    "rule_dur_many_unit",
    "rule_dur_unit",
    "rule_last_numr_unit",
    "rule_numr_unit",
    "rule_int_month",
    "rule_before_today",
    "rule_per_day",
    "rule_month",
    "rule_in_last_numr_unit",
    "rule_in_last_int_unit",
]

repeatable_rules = [
    "rule_int_times_in_int_unit",
    "rule_times_in_int_unit",
    "rule_int_times_in_unit_dash_int_unit",
    "rule_times_in_unit",
    "rule_int_dash_int_times_in_unit",
    "rule_int_dash_int_in_unit",
    "rule_prep_int_times_in_int_dash_int_unit",
    "rule_int_times_in_int_dash_int_unit",
    "rule_sev_times_in_unit",
    "rule_times_in_unit",
    "rule_regular",
]

relative_rules = [
    "rule_thr_int_dash_int_unit",
    "rule_aft_half_unit",
    "rule_thr_int_unit",
    "rule_aft_int_unit",
    "rule_this_year",
]

rule_stamps = {
    "once_rules": once_rules,
    "continious_rules": continious_rules,
    "repeatable_rules": repeatable_rules,
    "relative_rules": relative_rules,
}