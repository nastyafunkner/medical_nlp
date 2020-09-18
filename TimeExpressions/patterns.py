import re
import spacy
from spacy.tokens import Doc, Span
from spacy.matcher import PhraseMatcher, Matcher
from spacy.pipeline import EntityRuler

SEASONS = ["лето", "зима", "весна", "осень"]
DAYTIME = ["день", "утро", "вечер", "ночь"]
YEAR_PART = ["конец", "начало", "середина"]
time_unit = ["год", "месяц", "неделя", "день", "час", "минута", "полугод", "сутки", "мин", "лет", "г", "мес", "ч", "л",'г.', 'полгода']
time_events = ["сегодня", "вчера", "позавчера"]
time_regular = ["ежедневно", "ежемесячно", "еженедельно", "ежегодно"]
MONTHS = ["янва","январь","февраль","март","апрель","мая","июнь","июль","август","сентябрь","октябрь","ноябрь","декабрь","Январь","Февраль","Март","Апрель","Мая","Июнь","Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь","янв","фев","мар","апр","май","ин","ил","авг","сен","окт","нояб","дек"]

interpret_dict = {"лето": "01.06.", "зима": "01.12.", "весна": "01.03.", "осень": "01.09.", "конец": "01.12.",
    "начало": "01.01.", "середина": "01.06.", "январь": "01.", "февраль": "02.", "март": "03.", "апрель": "04.",
    "мая": "05.", "июнь": "06.", "июль": "07.", "август": "08.", "сентябрь": "09.", "октябрь": "10.",
    "ноябрь": "11.", "декабрь": "12.", "янва": "01.", "фев": "02.", "мар": "03.", "апр": "04.", "май": "05.",
    "ин": "06.", "ил": "07.", "авг": "08.", "сен": "09.", "окт": "10.", "нояб": "11.", "дек": "12.",
    "вечер": "21.00 ", "утро": "09.00 ", "день": "15.00 ", "ночь": "03.00 ",
}

day = r'\b([0-9]|[0-2][0-9]|3[0-1])\b'
yearfull = r"\b(19[0-9][0-9]|20[0-9][0-9])\b"
date = r'([0-3]\d[-][0-3]\d[.][0-1]\d[.][0-2]\d{3})|([0-3]\d[.][0-1]\d[.][0-2]\d{3})|([0-3]\d[.][0-1]\d[.]\d\d)|(\d[.][0-1]\d[.]\d\d)|([0-1]\d[.][0-2]\d{3})|(/d[.][0-2]\d[.]\d\d)|([0-3]\d[.][0-1]\d[ ][0-2]\d{3})'
time = r'([0-2][0-9][-.,][0-5][0-9])|([0-9][.-][0-5][0-9])'

patterns = [
    # несколько лет
    {"label": "EXPR", "pattern": [{"LEMMA": {"IN": ["несколько"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_dur_numr_unit"},
    # с 2005 года по 2009 год
    {"label": "EXPR", "pattern": [{"LOWER": 'с'}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": time_unit}}, {"LOWER": 'по'}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_from_yearfull_unit_till_yearfull_unit"},
    # в конце 2009 , начале 2010
    {"label": "EXPR", "pattern": [{"LOWER": 'в'}, {"LEMMA": {"IN": YEAR_PART}}, {"TEXT": {"REGEX": yearfull}}, {"TEXT": ','}, {"LEMMA": {"IN": YEAR_PART}}, {"TEXT": {"REGEX": yearfull}}], "id": "rule_in_part_yearfull_part_yearfull"},
    # с 08.06.10 по 22.06.10
    {"label": "EXPR", "pattern": [{"LOWER": 'с'}, {"TEXT": {"REGEX": date}}, {"LOWER": 'по'}, {"TEXT": {"REGEX": date}}], "id": "rule_from_yearfull_unit_till_yearfull_unit"},
    # С 08.06 по 10.06.08
    {"label": "EXPR", "pattern": [{"LOWER": 'с'}, {"TEXT": {"REGEX": time}}, {"LOWER": 'по'}, {"TEXT": {"REGEX": date}}], "id": "rule_from_time_till_date"},
    # 2011 г в 17-00
    {"label": "EXPR", "pattern": [{"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": ['год']}, "OP": "?"}, {"POS": {"IN": ["ADP"]}}, {"TEXT": {"REGEX": time}}], "id": "rule_yearfull_g_prep_time"},
    # 1976 - 1978 гг
    {"label": "EXPR", "pattern": [{"TEXT": {"REGEX": yearfull}}, {"TEXT": {"IN": ["–", "-"]}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_yearfull_yearfull_unit"},
    # В конце 2010
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}}, {"LEMMA": {"IN": YEAR_PART}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": ['год']}, "OP": "?"}], "id": "rule_prep_part_yearfull"},
    # В марте - апреле 2010 года
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}}, {"LEMMA": {"IN": MONTHS}}, {"TEXT": {"IN": ["–", "-"]}}, {"LEMMA": {"IN": MONTHS}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": ['год']}, "OP": "?"}], "id": "rule_prep_month_month_yearfull_unit"},
    # с 1-10 марта 2010 года
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}}, {"IS_DIGIT": True}, {"TEXT": {"IN": ["–", "-"]}}, {"IS_DIGIT": True}, {"LEMMA": {"IN": MONTHS}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": ['год']}, "OP": "?"}], "id": "rule_prep_int_dash_int_month_yearfull_unit"},
    # В марте и апреле 2010 года
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}}, {"LEMMA": {"IN": MONTHS}}, {"TEXT": "и"}, {"LEMMA": {"IN": MONTHS}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": ['год']}, "OP": "?"}], "id": "rule_prep_month_month_yearfull_unit"},
    # В марте-апреле 2010 года special for DP
    {"label": "EXPR", "pattern": [{"LEMMA": "в"}, {"POS": {"IN": ["NOUN"]}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": ['год']}, "OP": "?"}], "id": "rule_in_month_dash_month_yearfull_unit"},
    # с 9 мая 2010
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"TEXT": {"REGEX": day}}, {"LEMMA": {"IN": MONTHS}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": ['год']}, "OP": "?"}], "id": "rule_prep_day_month_yearfull"},
    # С декабря 2009 по май 2010 года
    {"label": "EXPR", "pattern": [{"LOWER": 'с'}, {"LEMMA": {"IN": MONTHS}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": ['год']}, "OP": "?"}, {"LOWER": 'по'}, {"LEMMA": {"IN": MONTHS}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": ['год']}, "OP": "?"}], "id": "rule_prep_month_yearfull_prep_month_yearfull_unit"},
    # август 2008 г 
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"LEMMA": {"IN": MONTHS}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": ['год']}, "OP": "?"}], "id": "rule_prep_month_yearfull_unit"},
    # Зимой 2010
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"LEMMA": {"IN": SEASONS}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": ['год']}, "OP": "?"}], "id": "rule_prep_season_yearfull"},
    # 7 июля
    {"label": "EXPR", "pattern": [{"TEXT": {"REGEX": day}}, {"LEMMA": {"IN": MONTHS}}], "id": "rule_day_month"},
    # С конца января 2011
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}}, {"LEMMA": {"IN": YEAR_PART}}, {"LEMMA": {"IN": MONTHS}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": ['год']}, "OP": "?"}], "id": "rule_prep_part_month_yearfull"},
    # начало января
    {"label": "EXPR", "pattern": [{"LEMMA": {"IN": YEAR_PART}}, {"LEMMA": {"IN": MONTHS}}], "id": "rule_part_month"},
    # последние 3 - 4 дня
    {"label": "EXPR", "pattern": [{"LEMMA": {"IN": ["последний"]}}, {"IS_DIGIT": True}, {"TEXT": {"IN": ["–", "-"]}}, {"IS_DIGIT": True}, {"LEMMA": {"IN": time_unit}}], "id": "rule_last_int_dash_int_unit"},
    # через 1 - 2 месяца
    {"label": "EXPR", "pattern": [{"LOWER": {"IN": ["через", "спустя"]}}, {"IS_DIGIT": True}, {"TEXT": {"IN": ["–", "-"]}}, {"IS_DIGIT": True}, {"LEMMA": {"IN": time_unit}}], "id": "rule_thr_int_dash_int_unit"},
    # до 1 раза в 1 - 2 месяца
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"IS_DIGIT": True, "OP": "?"}, {"LEMMA": {"IN": ["раз", "р"]}, "OP": "?"}, {"TEXT": "в"}, {"IS_DIGIT": True}, {"TEXT": {"IN": ["–", "-"]}}, {"IS_DIGIT": True}, {"LEMMA": {"IN": time_unit}}], "id": "rule_prep_int_times_in_int_dash_int_unit"},
    # 2 - 3 раза в год
    {"label": "EXPR", "pattern": [{"IS_DIGIT": True}, {"TEXT": {"IN": ["–", "-"]}}, {"IS_DIGIT": True}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"},  {"LEMMA": {"IN": time_unit}}], "id": "rule_int_dash_int_times_in_unit"},
    # 2 - 3 в год special for DP
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["NUM"]}}, {"TEXT": "в"},  {"LEMMA": {"IN": time_unit}}], "id": "rule_int_dash_int_times_in_unit"},
    # 1 раз в 6 мес
    {"label": "EXPR", "pattern": [{"IS_DIGIT": True, "OP": "?"}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"POS": {"IN": ["NUM"]}, "OP": "?"}, {"LEMMA": {"IN": time_unit}}], "id": "rule_int_times_in_int_unit"},
    # Последний месяц
    {"label": "EXPR", "pattern": [{"LEMMA": {"IN": ["последний"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_last_unit"},
    # с 90 х годов
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"IS_DIGIT": True}, {"TEXT": "х"}, {"LEMMA": {"IN": ["год"]}}], "id": "rule_from_int_h_unit"},
    # конца 80 - х STAMP continious
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"LEMMA": {"IN": YEAR_PART}}, {"IS_DIGIT": True}, {"TEXT": {"IN": ["–", "-"]}}, {"TEXT": "х"}, {"LEMMA": {"IN": ["год"]}, "OP": "?"}], "id": "rule_prep_part_int_dash_h"},
    # с 12 - ти лет
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"IS_DIGIT": True}, {"TEXT": {"IN": ["–", "-"]}}, {"TEXT": "ти"}, {"LEMMA": {"IN": ["год"]}, "OP": "?"}], "id": "rule_from_int_dash_ti_unit"},
    # Около 5 лет назад
    {"label": "EXPR", "pattern": [{"LEMMA": {"IN": ["около"]}}, {"IS_DIGIT": True}, {"LEMMA": {"IN": ["год"]}}, {"TEXT": "назад"}], "id": "rule_around_int_unit_ago"},
    # 3 года назад
    {"label": "EXPR", "pattern": [{"IS_DIGIT": True}, {"LEMMA": {"IN": ["год"]}}, {"TEXT": "назад"}], "id": "rule_int_unit_ago"},
    # около 2 часов ночи 17.12.2010
    {"label": "EXPR", "pattern": [{"LEMMA": {"IN": ["около"]}}, {"IS_DIGIT": True}, {"LEMMA": {"IN": ["час"]}}, {"LEMMA": {"IN": DAYTIME}}, {"TEXT": {"REGEX": date}}], "id": "rule_around_int_unit_ago"},
    # 9 ч утра
    {"label": "EXPR", "pattern": [{"IS_DIGIT": True}, {"LEMMA": {"IN": ["час"]}}, {"LEMMA": {"IN": DAYTIME}}], "id": "rule_int_unit_daytime"},
    # с утра 04.09.2010
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}}, {"LEMMA": {"IN": DAYTIME}}, {"TEXT": {"REGEX": date}}], "id": "rule_prep_daytime_unit"},
    # 8 , 00 утра 26.01.10
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["NUM"]}}, {"LEMMA": {"IN": DAYTIME}}, {"TEXT": {"REGEX": date}}], "id": "rule_int_daytime_date"},
    # 28.12.10 в 08.30
    {"label": "EXPR", "pattern": [{"TEXT": {"REGEX": date}}, {"POS": {"IN": ["ADP"]}}, {"TEXT": {"REGEX": time}}], "id": "rule_date_prep_time"},
    # 12.10.2011 года special for Stanza
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["NUM"]}},{"POS": {"IN": ["NUM"]}},{"LEMMA": {"IN": ["год"]}}], "id": "rule_num_num_year"},
    # 12.10.2011 года
    {"label": "EXPR", "pattern": [{"TEXT": {"REGEX": date}}, {"LEMMA": {"IN": ["год"]}}], "id": "rule_date_year"},
    # 12.10 года
    {"label": "EXPR", "pattern": [{"TEXT": {"REGEX": time}}, {"LEMMA": {"IN": ["год"]}}], "id": "rule_time_year"},
    # 12.10 часов
    {"label": "EXPR", "pattern": [{"TEXT": {"REGEX": time}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_time_unit"},
    # с 4.06 – 17.06
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"TEXT": {"REGEX": time}}, {"TEXT": {"IN": ["–", "-"]}}, {"TEXT": {"REGEX": time}}], "id": "rule_prep_time_dash_time"},
    # С 6.12. - 10.12.2010
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"TEXT": {"REGEX": time}}, {"TEXT": ".", "OP": "?"}, {"TEXT": {"IN": ["–", "-"]}}, {"TEXT": {"REGEX": date}}], "id": "rule_prep_time_dash_date"},
    # сегодня в 16.00
    {"label": "EXPR", "pattern": [{"LEMMA": {"IN": time_events}}, {"TEXT": "в"}, {"TEXT": {"REGEX": time}}], "id": "rule_event_in_time"},
    # 10-00 часов 17.12.2010
    {"label": "EXPR", "pattern": [{"TEXT": {"REGEX": time}}, {"LEMMA": {"IN": ['час']}}, {"TEXT": {"REGEX": date}}, {"LEMMA": {"IN": ["год"]}, "OP": "?"}], "id": "rule_time_hour_date"},
    # 10-00 часов 17.12.2010 special for stanza
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["NUM"]}}, {"TEXT": "-"}, {"POS": {"IN": ["NUM"]}}, {"LEMMA": {"IN": ['час']}}, {"POS": {"IN": ["NUM"]}}, {"POS": {"IN": ["NUM"]}}, {"LEMMA": {"IN": ["год"]}, "OP": "?"}], "id": "rule_time_hour_date"},
    # 10-00 часов 17.12.2010
    {"label": "EXPR", "pattern": [{"IS_DIGIT": True}, {"TEXT": {"IN": ["–", "-"]}}, {"IS_DIGIT": True}, {"LEMMA": {"IN": ['час']}}, {"TEXT": {"REGEX": date}}, {"LEMMA": {"IN": ["год"]}, "OP": "?"}], "id": "rule_int_dash_int_hour_date"},
    # с 23.00 21.12.2010
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"TEXT": {"REGEX": time}}, {"TEXT": {"REGEX": date}}], "id": "rule_prep_time_date"},
    # с 23-00 21.12.2010
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"POS": {"IN": ["NUM"]}}, {"TEXT": "-"}, {"POS": {"IN": ["NUM"]}}, {"LEMMA": {"IN": ["год"]}}], "id": "rule_prep_num_dash_num_year"},
    # В ноябре месяце 
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"LEMMA": {"IN": MONTHS}}, {"LEMMA": {"IN": ["месяц"]}}], "id": "rule_in_month_yearfull"},
    # до декабря 2009
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"LEMMA": {"IN": MONTHS}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": ["год", 'г.']}, "OP": "?"}], "id": "rule_prep_month_yearfull"},
    # с1960х годов special for DP
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}}, {"POS": {"IN": ["ADJ"]}}, {"LEMMA": {"IN": ["год"]}}], "id": "rule_prep_int_h_unit"},
    # В апреле
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}}, {"LEMMA": {"IN": MONTHS}}], "id": "rule_prep_month"},
    # 5.00 утра 24.01.2011
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"TEXT": {"REGEX": time}}, {"LEMMA": {"IN": DAYTIME}}, {"TEXT": {"REGEX": date}}], "id": "rule_time_daytime_date"},
    # вечером 28.12.2010
    {"label": "EXPR", "pattern": [{"LEMMA": {"IN": DAYTIME}}, {"TEXT": {"REGEX": date}}], "id": "rule_daytime_date"},
    # 23.12.2010 утром
    {"label": "EXPR", "pattern": [{"TEXT": {"REGEX": date}}, {"LEMMA": {"IN": DAYTIME}}], "id": "rule_date_daytime"},
    # вечером 28.12.2010 special for stanza
    {"label": "EXPR", "pattern": [{"LEMMA": {"IN": DAYTIME}}, {"POS": {"IN": ["NUM"]}}, {"POS": {"IN": ["NUM"]}}], "id": "rule_daytime_date"},
    # 23.12.2010 утром special for stanza
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["NUM"]}}, {"POS": {"IN": ["NUM"]}}, {"LEMMA": {"IN": DAYTIME}}], "id": "rule_date_daytime"},
    # 11-00 часов
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["NUM"]}}, {"TEXT": "-"}, {"POS": {"IN": ["NUM"]}}, {"LEMMA": {"IN": ['час']}}], "id": "rule_int_dash_int_hour"},
    # 17.09.2008
    {"label": "EXPR", "pattern": [{"TEXT": {"REGEX": date}}], "id": "rule_date"},
    # около 23.30
    {"label": "EXPR", "pattern": [{"LOWER": "около", "OP": "?"},{"TEXT": {"REGEX": time}}], "id": "rule_around_time"},
    # 23.30
    {"label": "EXPR", "pattern": [{"TEXT": {"REGEX": time}}], "id": "rule_time"},
    # 23.30 special for stanza
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"POS": {"IN": ["NUM"]}}, {"TEXT": "-"}, {"TEXT": {"REGEX": time}}], "id": "rule_prep_num_dash_time"},
    # до нескольких раз в месяц
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"LEMMA": {"IN": ["несколько"]}}, {"LEMMA": {"IN": ["раз"]}}, {"TEXT": "в"}, {"LEMMA": {"IN": time_unit}}], "id": "rule_sev_times_in_unit"},
    # спустя пол часа
    {"label": "EXPR", "pattern": [{"LOWER": "спустя"}, {"LEMMA": {"IN": ["пол"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_aft_half_unit"},
    # спустя год
    {"label": "EXPR", "pattern": [{"LOWER": "спустя"}, {"LEMMA": {"IN": time_unit}}], "id": "rule_aft_unit"},
    # через два часа
    {"label": "EXPR", "pattern": [{"LOWER": "через"}, {"POS": {"IN": ["NUM"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_thr_num_unit"},
    # около 4-х лет назад
    {"label": "EXPR", "pattern": [{"LOWER": "около"}, {"POS": {"IN": ["NUM"]}}, {"TEXT": "-"}, {"TEXT": "х"}, {"LEMMA": {"IN": time_unit}}, {"TEXT": "назад"}], "id": "rule_around_int_h_unit_ago"},
    # около 4-х лет назад (for stanza)
    {"label": "EXPR", "pattern": [{"LOWER": "около"}, {"POS": {"IN": ["ADJ"]}}, {"LEMMA": {"IN": time_unit}}, {"TEXT": "назад"}], "id": "rule_around_int_h_unit_ago"},
    # Около 5 лет назад
    {"label": "EXPR", "pattern": [{"LOWER": "около"}, {"IS_DIGIT": True}, {"LEMMA": {"IN": time_unit}}, {"TEXT": "назад"}], "id": "rule_around_int_unit_ago"},
    # Около семи лет назад
    {"label": "EXPR", "pattern": [{"LOWER": "около"}, {"POS": {"IN": ["NUM"]}}, {"LEMMA": {"IN": time_unit}}, {"TEXT": "назад"}], "id": "rule_around_numr_unit_ago"},
    # через 2 часа
    {"label": "EXPR", "pattern": [{"LOWER": "через"}, {"IS_DIGIT": True}, {"LEMMA": {"IN": time_unit}}], "id": "rule_thr_int_unit"},
    # Около 5 лет
    {"label": "EXPR", "pattern": [{"LOWER": "около"}, {"IS_DIGIT": True}, {"LEMMA": {"IN": time_unit}}], "id": "rule_around_int_unit"},
    # Около семи лет
    {"label": "EXPR", "pattern": [{"LOWER": "около"}, {"POS": {"IN": ["NUM"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_around_numr_unit"},
    # спустя 2 суток
    {"label": "EXPR", "pattern": [{"LOWER": "спустя"}, {"IS_DIGIT": True}, {"LEMMA": {"IN": time_unit}}], "id": "rule_aft_int_unit"},
    # 2005 и 2010 годах
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"TEXT": {"REGEX": yearfull}}, {"TEXT": "и"}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_int_and_int_unit"},
    # с 1993 года
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_prep_yearfull_unit"},
    # с 1993
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"TEXT": {"REGEX": yearfull}}], "id": "rule_prep_yearfull"},
    # с 51 лет
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"IS_DIGIT": True}, {"LEMMA": {"IN": time_unit}}], "id": "rule_prep_int_unit"},
    # c 02.2009 год
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}}, {"POS": {"IN": ["NUM", "PROPN"]}},{"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": ["год"]}, "OP": "?"}], "id": "rule_prep_num_yearfull"},
    # 02.2009 год
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["NUM", "PROPN"]}},{"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": ["год"]}, "OP": "?"}], "id": "rule_num_yearfull"},
    # 2009 год
    {"label": "EXPR", "pattern": [{"TEXT": {"REGEX": yearfull}}, {"LEMMA": {"IN": ["год"]}, "OP": "?"}], "id": "rule_yearfull"},
    # ежедневно
    {"label": "EXPR", "pattern": [{"LEMMA": {"IN": time_regular}}], "id": "rule_regular"},
    # сегодня утром
    {"label": "EXPR", "pattern": [{"LEMMA": {"IN": time_events}}, {"LEMMA": {"IN": DAYTIME}}], "id": "rule_event_daytime"},
    # сегодня
    {"label": "EXPR", "pattern": [{"LEMMA": {"IN": time_events}}], "id": "rule_events"},
    # более 15 лет
    {"label": "EXPR", "pattern": [{"LEMMA": {"IN": ["более"]}}, {"IS_DIGIT": True}, {"LEMMA": {"IN": time_unit}}], "id": "rule_more_int_unit"},
    # в возрасте 70 лет
    {"label": "EXPR", "pattern": [{"LOWER": "в"}, {"LEMMA": {"IN": ["возраст"]}}, {"IS_DIGIT": True}, {"LEMMA": {"IN": time_unit}}], "id": "rule_in_age_int_unit"},
    # в течение последних 1 , 5 месяцев
    {"label": "EXPR", "pattern": [{"LOWER": "в"}, {"LEMMA": {"IN": ["течение"]}}, {"LEMMA": {"IN": ["последний"]}}, {"POS": {"IN": ["INT"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_dur_last_int_com_unit"},
    # в течение последних пяти месяцев
    {"label": "EXPR", "pattern": [{"LOWER": "в"}, {"LEMMA": {"IN": ["течение"]}}, {"LEMMA": {"IN": ["последний"]}}, {"POS": {"IN": ["NUM"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_dur_last_numr_com_unit"},
    # в последние несколько дней
    {"label": "EXPR", "pattern": [{"LOWER": "в"}, {"LEMMA": {"IN": ["последний"]}}, {"POS": {"IN": ["NUM"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_in_last_numr_unit"},
    # в течении последнего месяца
    {"label": "EXPR", "pattern": [{"LOWER": "в"}, {"LEMMA": {"IN": ["течение"]}}, {"LEMMA": {"IN": ["последний"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_dur_last_unit"},
    # В течение 2 последних месяцев
    {"label": "EXPR", "pattern": [{"LOWER": "в"}, {"LEMMA": {"IN": ["течение"]}}, {"POS": {"IN": ["NUM"]}}, {"LEMMA": {"IN": ["последний"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_dur_int_last_unit"},
    # в течении 4 - х лет
    {"label": "EXPR", "pattern": [{"LOWER": "в"}, {"LEMMA": {"IN": ["течение"]}}, {"POS": {"IN": ["NUM"]}}, {"TEXT": "-"}, {"TEXT": "х"}, {"LEMMA": {"IN": time_unit}}], "id": "rule_dur_int_h_unit"},
    # в течении последних 4 - х лет
    {"label": "EXPR", "pattern": [{"LOWER": "в"}, {"LEMMA": {"IN": ["течение"]}}, {"LEMMA": {"IN": ["последний"]}}, {"POS": {"IN": ["NUM"]}}, {"TEXT": "-"}, {"TEXT": "х"}, {"LEMMA": {"IN": time_unit}}], "id": "rule_dur_last_int_h_unit"},
     # в течении последних 4-х лет
    {"label": "EXPR", "pattern": [{"LOWER": "в"}, {"LEMMA": {"IN": ["течение"]}}, {"LEMMA": {"IN": ["последний"]}}, {"POS": {"IN": ["ADJ"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_dur_last_adj_unit"},
    # в течение 5 - 7 минут
    {"label": "EXPR", "pattern": [{"LOWER": "в"}, {"LEMMA": {"IN": ["течение"]}}, {"IS_DIGIT": True}, {"TEXT": {"IN": ["–", "-"]}}, {"IS_DIGIT": True}, {"LEMMA": {"IN": time_unit}}], "id": "rule_dur_int_dash_int_unit"},
    # в течение 5 лет
    {"label": "EXPR", "pattern": [{"LOWER": "в"}, {"LEMMA": {"IN": ["течение"]}}, {"IS_DIGIT": True}, {"LEMMA": {"IN": time_unit}}], "id": "rule_dur_int_unit"},
    # в течение 5-7 минут special for DP
    {"label": "EXPR", "pattern": [{"LOWER": "в"}, {"LEMMA": {"IN": ["течение"]}}, {"POS": {"IN": ["NUM"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_dur_numr_unit"},
    # в течение нескольких лет
    {"label": "EXPR", "pattern": [{"LOWER": "в"}, {"LEMMA": {"IN": ["течение"]}}, {"LEMMA": {"IN": ["несколько"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_dur_numr_unit"},
    # В течение многих лет
    {"label": "EXPR", "pattern": [{"LOWER": "в"}, {"LEMMA": {"IN": ["течение"]}}, {"LEMMA": {"IN": ["много"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_dur_many_unit"},
    # В течение многих лет
    {"label": "EXPR", "pattern": [{"LOWER": "в"}, {"LEMMA": {"IN": ["течение"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_dur_unit"},
    # последних 3 дней
    {"label": "EXPR", "pattern": [{"LEMMA": {"IN": ["последний"]}}, {"POS": {"IN": ["NUM"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_last_int_unit"},
    # лет 20 назад
    {"label": "EXPR", "pattern": [{"LEMMA": {"IN": time_unit}}, {"IS_DIGIT": True}, {"LEMMA": {"IN": ["назад"]}}], "id": "rule_unit_int_ago"},
    # несколько дней назад
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["NUM"]}}, {"LEMMA": {"IN": time_unit}}, {"LEMMA": {"IN": ["назад"]}}], "id": "rule_numr_unit_ago"},
    # с 12-ти лет
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"POS": {"IN": ["NUM"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_prep_numr_unit"},
    # несколько месяцев
    {"label": "EXPR", "pattern": [{"POS": {"IN": ["NUM"]}}, {"LEMMA": {"IN": time_unit}}], "id": "rule_numr_unit"},
    # 3 месяца
    {"label": "EXPR", "pattern": [{"IS_DIGIT": True}, {"LEMMA": {"IN": time_unit}}], "id": "rule_int_month"},
    # несколько дней назад
    {"label": "EXPR", "pattern": [{"LEMMA": {"IN": time_unit}}, {"LEMMA": {"IN": ["назад"]}}], "id": "rule_unit_ago"},
    # месяц
    {"label": "EXPR", "pattern": [{"LEMMA": {"IN": ["около"]}, "OP": "?"}, {"LEMMA": {"IN": ["месяц"]}}], "id": "rule_month"},
    # за сутки
    {"label": "EXPR", "pattern": [{"LOWER": "за"}, {"TEXT": "сутки"}], "id": "rule_per_day"},
    # за день до этого
    {"label": "EXPR", "pattern": [{"LOWER": "за"}, {"TEXT": "день"}, {"TEXT": "до"}, {"TEXT": "этого"}], "id": "rule_day_before"},
    # в настоящее время
    {"label": "EXPR", "pattern": [{"LOWER": "в"}, {"TEXT": "настоящее"}, {"TEXT": "время"}], "id": "rule_now"},
    # С этого же года
    {"label": "EXPR", "pattern": [{"LOWER": "С"}, {"TEXT": "этого"}, {"TEXT": "же"}, {"TEXT": "года"}], "id": "rule_this_year"},
    # до сегодняшнего дня
    {"label": "EXPR", "pattern": [{"LOWER": "до"}, {"TEXT": "сегодняшнего"}, {"TEXT": "дня"}], "id": "rule_before_today"},
    
]