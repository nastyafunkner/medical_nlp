from datetime import date, datetime
from dateutil.relativedelta import relativedelta

strptime = datetime.strptime

SEASONS = {"лето": '15.07.', "зима": '15.01.', "весна": '15.04.', "осень": '15.10.'}
DAYTIME = {"день": 0, "утро": 0, "вечер": 12, "ночь": 0}
DAYTIMEH = {"день": '12', "утро": '07', "вечер": '18', "ночь": '03'}
YEAR_PART = {"конец": '15.11.', "начало": '15.02.', "середина": '01.07.'}
MONTH_PART = {"конец": '28', "начало": '01', "середина": '15'}
time_unit = ["год", "месяц", "неделя", "день", "час", "полугод", "сутки", "мин", "лет", "г", "мес", "ч", "л",'г.', 'полгода', "минута"]
time_events = {"сегодня": 0, "вчера": 1, "позавчера": 2}
time_regular = ["ежедневно", "ежемесячно", "еженедельно", "ежегодно"]
MONTHS = {"январь": '15.01.',"февраль": '15.02.',"март": '15.03.',"апрель": '15.04.',"мая": '15.05.',"июнь": '15.06.',"июль": '15.07.',"август": '15.08.',"сентябрь": '15.09.',
    "октябрь": '15.10.',"ноябрь": '15.11.',"декабрь": '15.12.',"янв": '15.01.',"фев": '15.02.',"мар": '15.03.',"апр": '15.04.',"май": '15.05.',"ин": '15.06.',"ил": '15.07.',
    "авг": '15.08.',"сен": '15.09.',"окт": '15.10.',"нояб": '15.11.',"дек": '15.12.'}

triangle = [-1,0,1]
trapezoid = [-1,0,0,1]
fuzzy_triangle = [-2,0,2]
delta_day = relativedelta(days=1)
delta_hour = relativedelta(hours=1)
delta_year = relativedelta(years=1)
delta_month = relativedelta(months=1)
delta_halfyear = relativedelta(months=6)
delta_week = relativedelta(weeks=1)
range_r = r'\d[-–]\d'

relative_dict = {'год':'years', 'час':'hours', 'день':'days', 'неделя':'weeks', 'месяц':'months', 'мес':'months','сутки':'days', 'минута':'minutes'}
delta_dict = {'год':relativedelta(years=1), 'час':relativedelta(hours=1), 'день':relativedelta(days=1), 
              'сутки':relativedelta(days=1), 'неделя':relativedelta(weeks=1), 'месяц':relativedelta(months=1),
              'минута':relativedelta(minutes=1)}
unit = ['день', 'час', 'неделя', 'год', 'месяц', 'сутки']
digit1d = {'один': 1,'два': 2,'три': 3,'четыре': 4,'пять': 5,'шесть': 6,'семь': 7,'восемь': 8,'девять': 9, 'десять': 10}
fuzzy_words = ['около','примерно','приблизительно', 'почти', 'где-то']

day = r'(?:[12][0-9]|3[01]|0?[1-9])'
month = r'(?:10|11|12|0[1-9])'
year4d = r'(?:19[1-9][0-9]|20[0-9][0-9])'
year2d = r'(?:\d\d)'
hour = r'(?:[01][0-9]|2[0-3]|[0-9])'
minute = r'(?:[0-5][0-9])'

shortdate = r'(^{}[.-/,]{}[.-/,]{}$)'.format(day,month,year2d)
date = r'(^{}[.-/,]{}[.-/,]{}$)'.format(day,month,year4d)
date_my4d = r'(^{}[.-/]{}$)'.format(month,year4d)
date_my2d = r'(^{}[.-/]{}$)'.format(month,year2d)

time = r'(^{}[-.:-]{}$)'.format(hour,minute)
yearfull = r'^{}$'.format(year4d)

rules = {
########## SIMPLE DATE RULES ##########
# '31.12.1997'
'r_date': {'pattern': [{"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime(ent[0].text, '%d.%m.%Y'), 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 1},
# '31.12.97'
'r_date_b': {'pattern': [{"TEXT": {"REGEX": shortdate}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime(ent[0].text, '%d.%m.%y'), 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 1},
# '12.1998'
'r_date_my4d': {'pattern': [{"TEXT": {"REGEX": date_my4d}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('15.{}'.format(ent[0].text), '%d.%m.%Y'), 
              'uncertain': delta_month,
              'form': triangle,
              'stamp': 1},
# '12.97'
'r_date_my2d': {'pattern': [{"TEXT": {"REGEX": date_my2d}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('15.{}'.format(ent[0].text), '%d.%m.%y'), 
              'uncertain': delta_month,
              'form': triangle,
              'stamp': 1},
# 'от 12.1998'
'r_ot_date_my4d': {'pattern': [{"LEMMA": 'от'}, {"TEXT": {"REGEX": date_my4d}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('15.{}'.format(ent[1].text), '%d.%m.%Y'), 
              'uncertain': delta_month,
              'form': triangle,
              'stamp': 1},
# 'от 12.97'
'r_ot_date_my2d': {'pattern': [{"LEMMA": 'от'}, {"TEXT": {"REGEX": date_my2d}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('15.{}'.format(ent[1].text), '%d.%m.%y'), 
              'uncertain': delta_month,
              'form': triangle,
              'stamp': 1},
# 'от 31.12.1997'
'r_ot_date': {'pattern': [{"LEMMA": 'от'}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime(ent[1].text, '%d.%m.%Y'), 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 1},
# 'от 31.12.97'
'r_ot_date_b': {'pattern': [{"LEMMA": 'от'}, {"TEXT": {"REGEX": shortdate}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime(ent[1].text, '%d.%m.%y'), 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 1},
# '13.01'
'r_date_short': {'pattern': [{"TEXT": {"REGEX": r'^{}[.]{}$'.format(day,month)}}], 
              'norm': lambda ent: strptime('{}.{}'.format(ent[0].text, ent.doc._.date.year), '%d.%m.%Y'), 
              'uncertain': relativedelta(days=1),
              'form': triangle,
              'stamp': 1},
# от 17.07
'r_ot_date_short': {'pattern': [{"LEMMA": 'от'}, {"TEXT": {"REGEX": r'^{}[.]{}$'.format(day,month)}}], 
              'norm': lambda ent: strptime('{}.{}'.format(ent[1].text, ent.doc._.date.year), '%d.%m.%Y'), 
              'uncertain': relativedelta(days=1),
              'form': triangle,
              'stamp': 1},
# '12.00 31.12.1997'
'r_time_date': {'pattern': [{"TEXT": {"REGEX": time}}, {"TEXT": {"REGEX": date}}], 
              'norm': lambda ent: strptime(ent.text, '%H.%M %d.%m.%Y'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# '12.00 31.12.97'
'r_time_shortdate': {'pattern': [{"TEXT": {"REGEX": time}}, {"TEXT": {"REGEX": shortdate}}], 
              'norm': lambda ent: strptime(ent.text, '%H.%M %d.%m.%Y'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# около 23.30
'r_around_time': {'pattern': [{"LEMMA": {"IN": fuzzy_words}}, {"TEXT": {"REGEX": time}}, {"LEMMA": 'час', "OP": "?"}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[1].text, ent.doc._.date.date()), '%H.%M %Y-%m-%d'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},

########## UNIT AGO ##########
# '10 лет назад'
'r_int_unit_ago': {'pattern': [{"_": {"is_digit": True}}, {"LEMMA": {"IN": unit}}, {"TEXT": "назад"}], 
              'norm': lambda ent: ent.doc._.date-relativedelta(**{relative_dict[ent[1].lemma_]:int(ent[0].text)}), 
              'uncertain': lambda ent: delta_dict[ent[1].lemma_],
              'form': triangle,
              'stamp': 1},  
# 'месяц назад'
'r_unit_ago': {'pattern': [{"LEMMA": {"IN": unit}}, {"TEXT": "назад"}], 
              'norm': lambda ent: ent.doc._.date-relativedelta(**{relative_dict[ent[0].lemma_]:1}), 
              'uncertain': lambda ent: delta_dict[ent[0].lemma_],
              'form': triangle,
              'stamp': 1},
# 'около месяц назад'
'r_around_unit_ago': {'pattern': [{"LEMMA": {"IN": fuzzy_words}},{"LEMMA": {"IN": unit}}, {"TEXT": "назад"}], 
              'norm': lambda ent: ent.doc._.date-relativedelta(**{relative_dict[ent[1].lemma_]:1}), 
              'uncertain': lambda ent: delta_dict[ent[1].lemma_],
              'form': triangle,
              'stamp': 1},
# 'десять лет назад'
'r_num_unit_ago': {'pattern': [{"LEMMA": {"IN": list(digit1d.keys())}}, {"LEMMA": {"IN": unit}}, {"TEXT": "назад"}],
              'norm': lambda ent: ent.doc._.date-relativedelta(**{relative_dict[ent[1].lemma_]:int(digit1d[ent[0].lemma_])}), 
              'uncertain': lambda ent: delta_dict[ent[1].lemma_],
              'form': triangle,
              'stamp': 1}, 
# 'около десяти лет назад'
'r_fuzzy_num_unit_ago': {'pattern': [{"LEMMA": {"IN": fuzzy_words}}, {"LEMMA": {"IN": list(digit1d.keys())}}, {"LEMMA": {"IN": unit}}, {"TEXT": "назад"}],
              'norm': lambda ent: ent.doc._.date-relativedelta(**{relative_dict[ent[2].lemma_]:int(digit1d[ent[1].lemma_])}), 
              'uncertain': lambda ent: delta_dict[ent[2].lemma_],
              'form': fuzzy_triangle,
              'stamp': 1},
# около полугода назад
'r_fuzzy_halfyear_ago': {'pattern': [{"LEMMA": {"IN": fuzzy_words}}, {"TEXT": "полугода"}, {"TEXT": "назад"}],
              'norm': lambda ent: ent.doc._.date-relativedelta(months=6), 
              'uncertain': lambda ent: relativedelta(months=1),
              'form': fuzzy_triangle,
              'stamp': 1},
# 'около 10 лет назад'
'r_fuzzy_int_unit_ago': {'pattern': [{"LEMMA": {"IN": fuzzy_words}}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": unit+['минута']}}, {"TEXT": "назад"}],
              'norm': lambda ent: ent.doc._.date-relativedelta(**{relative_dict[ent[2].lemma_]:int(ent[1].text)}), 
              'uncertain': lambda ent: delta_dict[ent[2].lemma_],
              'form': fuzzy_triangle,
              'stamp': 1},
# 'более 10 лет назад'
'r_more_int_unit_ago': {'pattern': [{"LEMMA": "более"}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": unit}}, {"TEXT": "назад"}],
              'norm': lambda ent: ent.doc._.date-relativedelta(**{relative_dict[ent[2].lemma_]:int(ent[1].text)}), 
              'uncertain': lambda ent: delta_dict[ent[2].lemma_],
              'form': fuzzy_triangle,
              'stamp': 1},
# лет 20 назад
'r_unit_int_ago': {'pattern': [{"LEMMA": {"IN": unit}}, {"_": {"is_digit": True}}, {"TEXT": "назад"}], 
              'norm': lambda ent: ent.doc._.date-relativedelta(**{relative_dict[ent[0].lemma_]:int(ent[1].text)}), 
              'uncertain': lambda ent: delta_dict[ent[0].lemma_],
              'form': triangle,
              'stamp': 1},  
# лет десять назад
'r_unit_num_ago': {'pattern': [{"LEMMA": {"IN": unit}}, {"LEMMA": {"IN": list(digit1d.keys())}}, {"TEXT": "назад"}],
              'norm': lambda ent: ent.doc._.date-relativedelta(**{relative_dict[ent[0].lemma_]:int(digit1d[ent[1].lemma_])}), 
              'uncertain': lambda ent: delta_dict[ent[0].lemma_],
              'form': triangle,
              'stamp': 1}, 
# несколько дней назад
'r_sev_unit_ago': {'pattern': [{"LEMMA": "несколько"}, {"LEMMA": {"IN": unit}}, {"TEXT": "назад"}],
              'norm': lambda ent: ent.doc._.date-relativedelta(**{relative_dict[ent[1].lemma_]:3}), 
              'uncertain': lambda ent: delta_dict[ent[1].lemma_]*3,
              'form': triangle,
              'stamp': 1},
# 1,5 года назад
'r_float_year_ago': {'pattern': [{"TEXT": {"REGEX": r'^\d[.,]\d$'}}, {"LEMMA": 'год'}, {"TEXT": "назад"}], 
              'norm': lambda ent: ent.doc._.date - relativedelta(years=int(ent[0].text[0]), months=6), 
              'uncertain': delta_year,
              'form': triangle,
              'stamp': 1},
# 1,5 месяца назад
'r_float_month_ago': {'pattern': [{"TEXT": {"REGEX": r'^\d[.,]\d$'}}, {"LEMMA": 'месяц'}, {"TEXT": "назад"}], 
              'norm': lambda ent: ent.doc._.date - relativedelta(months=int(ent[0].text[0]), days=15), 
              'uncertain': delta_month,
              'form': triangle,
              'stamp': 1},

########## ONCE EVENTS ##########
# в 11.00 24.12.10 г
'r_in_time_shortdate': {'pattern': [{"LEMMA": 'в'}, {"TEXT": {"REGEX": time}}, {"TEXT": {"REGEX": shortdate}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[1].text, ent[2].text), '%H.%M %d.%m.%y'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# 28.12.10 в 08.30
'r_shortdate_in_time_': {'pattern': [{"TEXT": {"REGEX": shortdate}}, {"LEMMA": 'в'}, {"TEXT": {"REGEX": time}}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[2].text, ent[0].text), '%H.%M %d.%m.%y'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# 26.07.2014 в 10.00
'r_date_in_time_': {'pattern': [{"TEXT": {"REGEX": date}}, {"LEMMA": 'в'}, {"TEXT": {"REGEX": time}}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[2].text, ent[0].text), '%H.%M %d.%m.%Y'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# 28.09.10 около 07:00
'r_shortdate_around_time_': {'pattern': [{"TEXT": {"REGEX": shortdate}}, {"LEMMA": 'около'}, {"TEXT": {"REGEX": time}}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[2].text, ent[0].text), '%H.%M %d.%m.%y'),
              'uncertain': delta_hour,
              'form': fuzzy_triangle,
              'stamp': 1},
# 28.09.2010 около 07:00
'r_date_around_time_': {'pattern': [{"TEXT": {"REGEX": date}}, {"LEMMA": 'около'}, {"TEXT": {"REGEX": time}}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[2].text, ent[0].text), '%H.%M %d.%m.%Y'), 
              'uncertain': delta_hour,
              'form': fuzzy_triangle,
              'stamp': 1},
# 30.09.2011 года приблизительно в 2:40
'r_date_year_around_time_': {'pattern': [{"TEXT": {"REGEX": date}}, {"LEMMA": 'год'}, {"LEMMA": {"IN": fuzzy_words}}, {"LEMMA": 'в'}, {"TEXT": {"REGEX": time}}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[4].text, ent[0].text), '%H.%M %d.%m.%Y'), 
              'uncertain': delta_hour,
              'form': fuzzy_triangle,
              'stamp': 1},
# 2005 год
'r_year4d_year': {'pattern': [{"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('01.07.{}'.format(ent[0].text), '%d.%m.%Y'), 
              'uncertain': delta_year,
              'form': triangle,
              'stamp': 1},
# 2011 г в 17-00 часов
'r_year4d_year_in_time': {'pattern': [{"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год'}, {"LEMMA": 'в'}, {"TEXT": {"REGEX": time}}, {"LEMMA": 'час', "OP": "?"}], 
              'norm': lambda ent: strptime('01.07.{}'.format(ent[0].text), '%d.%m.%Y'), 
              'uncertain': delta_year,
              'form': triangle,
              'stamp': 1},
# в 2005 год
'r_in_year4d_year': {'pattern': [{"LEMMA": {"IN": ['в', 'от']}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('01.07.{}'.format(ent[1].text), '%d.%m.%Y'), 
              'uncertain': delta_year,
              'form': triangle,
              'stamp': 1},
# в 2005 г
'r_in_year4d_year_a': {'pattern': [{"LEMMA": 'в'}, {"TEXT": {"REGEX": yearfull}}, {"TEXT": "г"}], 
              'norm': lambda ent: strptime('01.07.{}'.format(ent[1].text), '%d.%m.%Y'), 
              'uncertain': delta_year,
              'form': triangle,
              'stamp': 1},
# В конце 2010
'r_in_yearpart_year4d': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": {"IN": list(YEAR_PART.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{}{}'.format(YEAR_PART[ent[1].lemma_],ent[2].text), '%d.%m.%Y'), 
              'uncertain': relativedelta(days=45),
              'form': triangle,
              'stamp': 1},
# конец 2010
'r_yearpart_year4d': {'pattern': [{"LEMMA": {"IN": list(YEAR_PART.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{}{}'.format(YEAR_PART[ent[0].lemma_],ent[1].text), '%d.%m.%Y'), 
              'uncertain': relativedelta(days=45),
              'form': triangle,
              'stamp': 1},
# В марте - апреле 2010 года
'r_month_dash_month_yeard4d_year': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": '-'}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год'}], 
              'norm': lambda ent: strptime('{}{}'.format(MONTHS[ent[3].lemma_],ent[4].text), '%d.%m.%Y'),
              'uncertain': delta_month,
              'form': triangle,
              'stamp': 1},
# В марте и апреле 2010 года
'r_month_and_month_yeard4d_year': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": 'и'}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год'}], 
              'norm': lambda ent: strptime('{}{}'.format(MONTHS[ent[3].lemma_],ent[4].text), '%d.%m.%Y'), 
              'uncertain': delta_month,
              'form': triangle,
              'stamp': 1},
# август 2008 г 
'r_month_yeard4d_year': {'pattern': [{"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{}{}'.format(MONTHS[ent[0].lemma_],ent[1].text), '%d.%m.%Y'), 
              'uncertain': delta_month,
              'form': triangle,
              'stamp': 1},
# В мае 2009 года	
'r_in_month_yeard4d_year': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{}{}'.format(MONTHS[ent[1].lemma_],ent[2].text), '%d.%m.%Y'), 
              'uncertain': delta_month,
              'form': triangle,
              'stamp': 1},
# 1-10 марта 2010 г	
'r_range_month_year4d_year': {'pattern': [{"TEXT": {"REGEX": range_r}}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{}{}{}'.format(ent[0].text[:ent[0].text.find('-')], MONTHS[ent[1].lemma_][2:], ent[2].text), '%d.%m.%Y'), 
              'uncertain': delta_month,
              'form': triangle,
              'stamp': 1},
# от июня 2009 г	
'r_ot_month_yeard4d_year': {'pattern': [{"LEMMA": 'от'}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{}{}'.format(MONTHS[ent[1].lemma_],ent[2].text), '%d.%m.%Y'), 
              'uncertain': delta_month,
              'form': triangle,
              'stamp': 1},
# Зимой 2010 
'r_season_yeard4d_year': {'pattern': [{"LEMMA": {"IN": list(SEASONS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{}{}'.format(SEASONS[ent[0].lemma_], ent[1].text), '%d.%m.%Y'), 
              'uncertain': relativedelta(days=45),
              'form': triangle,
              'stamp': 1},
# 2 декабря 2010
'r_int_month_yeard4d_year': {'pattern': [{"_": {"is_digit": True}}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{}{}{}'.format(ent[0].text, MONTHS[ent[1].lemma_][2:], ent[2].text), '%d.%m.%Y'), 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 1},
# 7 июля
'r_int_month': {'pattern': [{"_": {"is_digit": True}}, {"LEMMA": {"IN": list(MONTHS.keys())}}], 
              'norm': lambda ent: strptime('{}{}{}'.format(ent[0].text, MONTHS[ent[1].lemma_][2], ent.doc._.date.year), '%d.%m.%Y'), 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 1},
# в конце января 2011
'r_in_monthpart_month_year4d': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": {"IN": list(YEAR_PART.keys())}}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{}{}{}'.format(MONTH_PART[ent[1].lemma_],MONTHS[ent[2].lemma_][2:], ent[3].lemma_), '%d.%m.%Y'), 
              'uncertain': relativedelta(days=15),
              'form': triangle,
              'stamp': 1},
# конец января 2011
'r_monthpart_month_year4d': {'pattern': [{"LEMMA": {"IN": list(YEAR_PART.keys())}}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{}{}{}'.format(MONTH_PART[ent[0].lemma_],MONTHS[ent[1].lemma_][2:], ent[2].lemma_), '%d.%m.%Y'), 
              'uncertain': relativedelta(days=15),
              'form': triangle,
              'stamp': 1},
# около 2 часов ночи 17.12.2010
'r_around_int_hour_daytime_date': {'pattern': [{"LEMMA": "около"}, {"_": {"is_digit": True}}, {"LEMMA": 'час'}, {"LEMMA": {"IN": list(DAYTIME.keys())}}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{} {}'.format(int(ent[1].text)+DAYTIME[ent[3].lemma_], ent[4].text), '%H %d.%m.%Y'), 
              'uncertain': delta_hour,
              'form': fuzzy_triangle,
              'stamp': 1},
# 2 ч ночи 17.12.2010
'r_int_h_daytime_date': {'pattern': [{"_": {"is_digit": True}}, {"TEXT": 'ч'}, {"LEMMA": {"IN": list(DAYTIME.keys())}}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[3].text, int(ent[0].text)+DAYTIME[ent[2].lemma_]), '%d.%m.%Y %H'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# около 2 ч ночи 17.12.2010
'r_around_int_h_daytime_date': {'pattern': [{"LEMMA": "около"}, {"_": {"is_digit": True}}, {"TEXT": 'ч'}, {"LEMMA": {"IN": list(DAYTIME.keys())}}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[4].text, int(ent[1].text)+DAYTIME[ent[3].lemma_]), '%d.%m.%Y %H'), 
              'uncertain': delta_hour,
              'form': fuzzy_triangle,
              'stamp': 1},
# 2 часа ночи 17.12.2010
'r_int_hour_daytime_date': {'pattern': [{"_": {"is_digit": True}}, {"LEMMA": 'час'}, {"LEMMA": {"IN": list(DAYTIME.keys())}}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[3].text, int(ent[0].text)+DAYTIME[ent[2].lemma_]), '%d.%m.%Y %H'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# около 2 ночи 17.12.2010
'r_around_int_daytime_date': {'pattern': [{"LEMMA": "около"}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": list(DAYTIME.keys())}}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[3].text, int(ent[1].text)+DAYTIME[ent[2].lemma_]), '%d.%m.%Y %H'), 
              'uncertain': delta_hour,
              'form': fuzzy_triangle,
              'stamp': 1},
# 2 ночи 17.12.2010
'r_int_daytime_date': {'pattern': [{"_": {"is_digit": True}}, {"LEMMA": {"IN": list(DAYTIME.keys())}}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[2].text, int(ent[0].text)+DAYTIME[ent[1].lemma_]), '%d.%m.%Y %H'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# в 4 ч утра
'r_in_int_h_daytime': {'pattern': [{"LEMMA": "в"}, {"_": {"is_digit": True}}, {"TEXT": 'ч'}, {"LEMMA": {"IN": list(DAYTIME.keys())}}], 
              'norm': lambda ent: strptime('{} {}'.format((str(ent.doc._.date))[:9], int(ent[1].text)+DAYTIME[ent[3].lemma_]), '%Y-%m-%d %H'),
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# 9 ч утра
'r_int_h_daytime': {'pattern': [{"_": {"is_digit": True}}, {"TEXT": 'ч'}, {"LEMMA": {"IN": list(DAYTIME.keys())}}], 
              'norm': lambda ent: strptime('{} {}'.format((str(ent.doc._.date))[:9], int(ent[0].text)+DAYTIME[ent[2].lemma_]), '%Y-%m-%d %H'),
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# 9 часов утра
'r_int_hour_daytime': {'pattern': [{"_": {"is_digit": True}}, {"LEMMA": 'час'}, {"LEMMA": {"IN": list(DAYTIME.keys())}}], 
              'norm': lambda ent: strptime('{} {}'.format((str(ent.doc._.date))[:9], int(ent[0].text)+DAYTIME[ent[2].lemma_]), '%Y-%m-%d %H'),
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# утром 17.12.2010
'r_daytime_date': {'pattern': [{"LEMMA": {"IN": list(DAYTIME.keys())}}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[1].text, DAYTIMEH[ent[0].lemma_]), '%d.%m.%Y %H'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# 17.12.2010 утром
'r_date_datetime': {'pattern': [{"TEXT": {"REGEX": date}}, {"LEMMA": {"IN": list(DAYTIME.keys())}}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[0].text, DAYTIMEH[ent[1].lemma_]), '%d.%m.%Y %H'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# 25.12.10 ночью
'r_shortdate_datetime': {'pattern': [{"TEXT": {"REGEX": shortdate}}, {"LEMMA": {"IN": list(DAYTIME.keys())}}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[0].text, DAYTIMEH[ent[1].lemma_]), '%d.%m.%y %H'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# 6.30 утра 20.12.2010 года
'r_time_daytime_date': {'pattern': [{"TEXT": {"REGEX": time}}, {"LEMMA": {"IN": list(DAYTIME.keys())}}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[2].text, ent[0].text), '%d.%m.%Y %H.%M')+relativedelta(hours=DAYTIME[ent[1].lemma_]), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# около 6.30 утра 20.12.2010 года
'r_around_time_daytime_date': {'pattern': [{"LEMMA": "около"}, {"TEXT": {"REGEX": time}}, {"LEMMA": {"IN": list(DAYTIME.keys())}}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[3].text, ent[1].text), '%d.%m.%Y %H.%M')+relativedelta(hours=DAYTIME[ent[2].lemma_]), 
              'uncertain': relativedelta(hours=2),
              'form': fuzzy_triangle,
              'stamp': 1},
# 12.10.2011 года в 8 часов утра
'r_date_in_time_daytime': {'pattern': [{"TEXT": {"REGEX": date}}, {"LEMMA": 'год'}, {"TEXT": "в"}, {"_": {"is_digit": True}}, {"LEMMA": 'час'}, {"LEMMA": {"IN": list(DAYTIME.keys())}}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[0].text, int(ent[3].text)+DAYTIME[ent[5].lemma_]), '%d.%m.%Y %H'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# сегодня в 16.00
'r_event_time': {'pattern': [{"LEMMA": {"IN": list(time_events.keys())}}, {"TEXT": "в"}, {"TEXT": {"REGEX": r'^{}.{}$'.format(hour,minute)}}], 
              'norm': lambda ent: strptime('{} {}'.format(ent.doc._.date.date()-delta_day*time_events[ent[0].lemma_], ent[2].text), '%Y-%m-%d %H.%M'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# сегодня около 11-00 часов
'r_event_around_time': {'pattern': [{"LEMMA": {"IN": list(time_events.keys())}}, {"TEXT": "около"}, {"TEXT": {"REGEX": time}}, {"LEMMA": 'час', "OP": "?"}], 
              'norm': lambda ent: strptime('{} {}'.format(ent.doc._.date.date()-delta_day*time_events[ent[0].lemma_], ent[2].text), '%Y-%m-%d %H.%M'), 
              'uncertain': delta_hour*2,
              'form': triangle,
              'stamp': 1},
# сегодня
'r_event': {'pattern': [{"LEMMA": {"IN": list(time_events.keys())}}], 
              'norm': lambda ent: strptime('{} 12.00'.format(ent.doc._.date.date()-delta_day*time_events[ent[0].lemma_]), '%Y-%m-%d %H.%M'), 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 1},
# в августе месяце 
'r_in_month': {'pattern': [{"LEMMA": 'в'},{"LEMMA": {"IN": list(MONTHS.keys())}}, {"LEMMA": 'месяц', "OP": "?"}], 
              'norm': lambda ent: strptime('{}{}'.format(MONTHS[ent[1].lemma_], ent.doc._.date.year), '%d.%m.%Y'), 
              'uncertain': delta_month,
              'form': triangle,
              'stamp': 1},
# сегодня в 4 ч утра
'r_event_in_time_daytime': {'pattern': [{"LEMMA": {"IN": list(time_events.keys())}}, {"TEXT": "в"}, {"_": {"is_digit": True}}, {"LEMMA": 'час'}, {"LEMMA": {"IN": list(DAYTIME.keys())}}], 
              'norm': lambda ent: strptime('{} {}'.format(ent.doc._.date.date()-delta_day*time_events[ent[0].lemma_], int(ent[2].text)+DAYTIME[ent[4].lemma_]), '%Y-%m-%d %H'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# Сегодня около 10 ч утра
'r_event_around_time_daytime': {'pattern': [{"LEMMA": {"IN": list(time_events.keys())}}, {"TEXT": "около"}, {"_": {"is_digit": True}}, {"LEMMA": 'час'}, {"LEMMA": {"IN": list(DAYTIME.keys())}}], 
              'norm': lambda ent: strptime('{} {}'.format(ent.doc._.date.date()-delta_day*time_events[ent[0].lemma_], int(ent[2].text)+DAYTIME[ent[4].lemma_]), '%Y-%m-%d %H'), 
              'uncertain': delta_hour,
              'form': fuzzy_triangle,
              'stamp': 1},
# сегодня в 4 ч утра
'r_event_in_time_daytime_a': {'pattern': [{"LEMMA": {"IN": list(time_events.keys())}}, {"TEXT": "в"}, {"_": {"is_digit": True}}, {"TEXT": 'ч'}, {"LEMMA": {"IN": list(DAYTIME.keys())}}], 
              'norm': lambda ent: strptime('{} {}'.format(ent.doc._.date.date()-delta_day*time_events[ent[0].lemma_], int(ent[2].text)+DAYTIME[ent[4].lemma_]), '%Y-%m-%d %H'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# Сегодня около 10 ч утра
'r_event_around_time_daytime_a': {'pattern': [{"LEMMA": {"IN": list(time_events.keys())}}, {"TEXT": "около"}, {"_": {"is_digit": True}}, {"TEXT": 'ч'}, {"LEMMA": {"IN": list(DAYTIME.keys())}}], 
              'norm': lambda ent: strptime('{} {}'.format(ent.doc._.date.date()-delta_day*time_events[ent[0].lemma_], int(ent[2].text)+DAYTIME[ent[4].lemma_]), '%Y-%m-%d %H'), 
              'uncertain': delta_hour,
              'form': fuzzy_triangle,
              'stamp': 1},
# в 4 ч утра
'r_in_time_daytime': {'pattern': [{"LEMMA": "в"}, {"_": {"is_digit": True}}, {"LEMMA": 'час'}, {"LEMMA": {"IN": list(DAYTIME.keys())}}], 
              'norm': lambda ent: strptime('{} {}'.format(ent.doc._.date.date(), int(ent[1].text)+DAYTIME[ent[3].lemma_]), '%Y-%m-%d %H'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# Около 11 часов дня
'r_around_time_daytime': {'pattern': [{"LEMMA": "около"}, {"_": {"is_digit": True}}, {"LEMMA": 'час'}, {"LEMMA": {"IN": list(DAYTIME.keys())}}], 
              'norm': lambda ent: strptime('{} {}'.format(ent.doc._.date.date(), int(ent[1].text)+DAYTIME[ent[3].lemma_]), '%Y-%m-%d %H'), 
              'uncertain': delta_hour,
              'form': fuzzy_triangle,
              'stamp': 1},
# 10-00 часов 17.12.2010 года
'r_time_h__date': {'pattern': [{"TEXT": {"REGEX": time}}, {"LEMMA": "час"}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[0].text, ent[2].text), '%H.%M %d.%m.%Y'),
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# около 10-00 часов 17.12.2010 года
'r_around_time_h_date': {'pattern': [{"LEMMA": "около"}, {"TEXT": {"REGEX": time}}, {"LEMMA": "час"}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{} {}'.format(ent[1].text, ent[3].text), '%H.%M %d.%m.%Y'),
              'uncertain': delta_hour,
              'form': fuzzy_triangle,
              'stamp': 1},
# сентябрь
'r_month': {'pattern': [{"LEMMA": {"IN": list(MONTHS.keys())}}], 
              'norm': lambda ent: strptime('{}{}'.format(MONTHS[ent[1].lemma_], ent.doc._.date.year), '%d-%m-%Y'), 
              'uncertain': delta_month,
              'form': triangle,
              'stamp': 1},
# от 24-25.11.2010
'r_ot_day_dash_date': {'pattern': [{"LEMMA": 'от'}, {"TEXT": {"REGEX": r'^{}[-–]{}.{}.{}$'.format(day,day,month,year4d)}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime(ent[1].text[ent[1].text.find('-')+1:], '%d.%m.%Y'), 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 1},
# от 10-13.09.11 г
'r_ot_day_dash_shortdate': {'pattern': [{"LEMMA": 'от'}, {"TEXT": {"REGEX": r'^{}[-–]{}.{}.{}$'.format(day,day,month,year2d)}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime(ent[1].text[ent[1].text.find('-')+1:], '%d.%m.%y'), 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 1},
# в 90-х годах
'r_in_int_h_year': {'pattern': [{"LEMMA": "в"}, {"_": {"is_digit": True}}, {"TEXT": {"IN": ['годах', 'годы']}}], 
              'norm': lambda ent: strptime('01.07.{}'.format(int(ent[1].text)+1905), '%d.%m.%Y'),
              'uncertain': relativedelta(years=5),
              'form': triangle,
              'stamp': 1},
# в 12.2013 г
'r_in_month_year': {'pattern': [{"LEMMA": 'в'}, {"TEXT": {"REGEX": r'^{}.{}$'.format(month,year4d)}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('15.{}'.format(ent[1].text), '%d.%m.%Y'), 
              'uncertain': delta_month,
              'form': triangle,
              'stamp': 1},
# 28.08.	
'r_day_month': {'pattern': [{"TEXT": {"REGEX": r'^{}.{}.$'.format(day,month)}}], 
              'norm': lambda ent: strptime('{}{}'.format(ent[0].text, ent.doc._.date.year), '%d.%m.%Y'), 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 1},
# от 06.04.	
'r_ot_day_month': {'pattern': [{"LEMMA": 'от'},{"TEXT": {"REGEX": r'^{}.{}.$'.format(day,month)}}], 
              'norm': lambda ent: strptime('{}{}'.format(ent[1].text, ent.doc._.date.year), '%d.%m.%Y'), 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 1},
# сегодня в 16.00
'r_event_from_time': {'pattern': [{"LEMMA": {"IN": list(time_events.keys())}}, {"TEXT": "с"}, {"TEXT": {"REGEX": r'^{}.{}$'.format(hour,minute)}}], 
              'norm': lambda ent: strptime(str(ent.doc._.date.date()-delta_day*time_events[ent[0].lemma_])+ent[2].text, '%Y-%m-%d%H.%M'), 
              'uncertain': delta_hour,
              'form': triangle,
              'stamp': 1},
# Сегодня 27.07.13 около 15 ч
'r_event_shortdate_around_time': {'pattern': [{"LEMMA": {"IN": list(time_events.keys())}}, {"TEXT": {"REGEX": shortdate}}, {"LEMMA": 'около'}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": ['час', 'часть']}, "OP": "?"}], 
              'norm': lambda ent: strptime(ent[1].text +' ' +ent[3].text, '%d.%m.%y %H'), 
              'uncertain': delta_hour,
              'form': fuzzy_triangle,
              'stamp': 1},

########## CONTINIOUS EVENTS ##########
# С середины августа
'r_from_monthpart_month': {'pattern': [{"LEMMA": 'с'}, {"LEMMA": {"IN": list(YEAR_PART.keys())}}, {"LEMMA": {"IN": list(MONTHS.keys())}}], 
              'norm': lambda ent: [strptime('{}.{}.{}'.format(MONTH_PART[ent[1].lemma_],MONTHS[ent[2].lemma_][3:5], ent.doc._.date.year), '%d.%m.%Y'), ent.doc._.date], 
              'uncertain': [relativedelta(days=15), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# с 9 мая 2010
'r_from_int_month_yeard4d_year': {'pattern': [{"LEMMA": 'с'}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime('{}.{}.{}'.format(ent[1].text, MONTHS[ent[2].lemma_][3:5], ent[3].text), '%d.%m.%Y'), ent.doc._.date], 
              'uncertain': [delta_day, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# c 1-10 марта 2010 г	
'r_from_range_month_year4d_year': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": range_r}}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime(ent[1].text[0]+MONTHS[ent[2].lemma_][2:]+ent[3].lemma_, '%d.%m.%Y'), ent.doc._.date], #
              'uncertain': [delta_month, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# С конца 2011
'r_from_yearpart_year4d': {'pattern': [{"LEMMA": 'с'}, {"LEMMA": {"IN": list(YEAR_PART.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime(YEAR_PART[ent[1].lemma_]+ent[2].text, '%d.%m.%Y'), ent.doc._.date], 
              'uncertain': [relativedelta(days=45), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# С конца января 2011
'r_from_monthpart_month_year4d': {'pattern': [{"LEMMA": 'с'}, {"LEMMA": {"IN": list(YEAR_PART.keys())}}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime('{}.{}.{}'.format(MONTH_PART[ent[1].lemma_],MONTHS[ent[2].lemma_][3:5], ent[3].lemma_), '%d.%m.%Y'), ent.doc._.date], 
              'uncertain': [relativedelta(days=15), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# с утра 04.09.2010
'r_from_daytime_date': {'pattern': [{"LEMMA": 'с'},{"LEMMA": {"IN": list(DAYTIME.keys())}}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime('{} {}'.format(ent[2].text, DAYTIMEH[ent[1].lemma_]), '%d.%m.%Y %H'), ent.doc._.date], 
              'uncertain': [delta_hour, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# с 23.00 21.12.2010
'r_from_time_date_a': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": r'^{}.{}$'.format(hour,minute)}}, {"TEXT": {"REGEX": date}}], 
              'norm': lambda ent: [strptime('{} {}'.format(ent[1].text, ent[2].text), '%H.%M %d.%m.%Y'), ent.doc._.date],
              'uncertain': [delta_hour, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# с 17.00 07.08.13
'r_from_time_shortdate': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": r'^{}.{}$'.format(hour,minute)}}, {"TEXT": {"REGEX": shortdate}}], 
              'norm': lambda ent: [strptime(ent.text[2:], '%H.%M %d.%m.%y'), ent.doc._.date], 
              'uncertain': [delta_hour, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# 'с 23-00 21.12.2010'
'r_from_time_date_b': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": r'^{}-{}$'.format(hour,minute)}}, {"TEXT": {"REGEX": date}}], 
              'norm': lambda ent: [strptime(ent.text[2:], '%H-%M %d.%m.%Y'), ent.doc._.date], 
              'uncertain': [delta_hour, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# 11.09.2010 с 20.00
'r_date_from_time': {'pattern': [{"TEXT": {"REGEX": date}}, {"LEMMA": 'с'}, {"TEXT": {"REGEX": time}}], 
              'norm': lambda ent: [strptime('{} {}'.format(ent[2].text, ent[0].text), '%H.%M %d.%m.%Y'), ent.doc._.date], 
              'uncertain': [delta_hour, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# 'с 21.12.2010'
'r_from_date': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime(ent[1].text, '%d.%m.%Y'), ent.doc._.date], 
              'uncertain': [delta_day, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# с 27.12.10
'r_from_shortdate': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": shortdate}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime(ent[1].text, '%d.%m.%y'), ent.doc._.date], 
              'uncertain': [delta_day, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# с 2010
'r_from_year4d_year': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime('01.07.{}'.format(ent[1].text), '%d.%m.%Y'), ent.doc._.date], 
              'uncertain': [delta_year, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# с 02.2009 год
'r_from_shortdate_year_a': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": r'^{}.{}$'.format(month,year4d)}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime('15.{}'.format(ent[1].text), '%d.%m.%Y'), ent.doc._.date], 
              'uncertain': [delta_month, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# с 02.98 год
'r_from_shortdate_year_b': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": r'^{}.{}$'.format(month,year2d)}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime('15.{}'.format(ent[1].text), '%d.%m.%Y'), ent.doc._.date], 
              'uncertain': [delta_year, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# с мая 2010
'r_from_month_yeard4d_year': {'pattern': [{"LEMMA": 'с'}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime('{}{}'.format(MONTHS[ent[1].lemma_], ent[2].text), '%d.%m.%Y'), ent.doc._.date], 
              'uncertain': [delta_month, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# С осени 2005 г 
'r_from_season_yeard4d_year': {'pattern': [{"LEMMA": 'с'}, {"LEMMA": {"IN": list(SEASONS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime(SEASONS[ent[1].lemma_]+ent[2].lemma_, '%d.%m.%Y'), ent.doc._.date], 
              'uncertain': [relativedelta(days=60), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# с сентября
'r_from_month': {'pattern': [{"LEMMA": 'с'}, {"LEMMA": {"IN": list(MONTHS.keys())}}], 
              'norm': lambda ent: [strptime('{}{}'.format(MONTHS[ent[1].lemma_], ent.doc._.date.year), '%d.%m.%Y'), ent.doc._.date], 
              'uncertain': [delta_month, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# Сегодня с 8 ч утра
'r_event_from_time_daytime_a': {'pattern': [{"LEMMA": {"IN": list(time_events.keys())}}, {"TEXT": "с"}, {"_": {"is_digit": True}}, {"LEMMA": 'час'}, {"LEMMA": {"IN": list(DAYTIME.keys())}}], 
              'norm': lambda ent: [strptime('{} {}'.format(str(ent.doc._.date.date()-delta_day*time_events[ent[0].lemma_]), int(ent[2].text)+DAYTIME[ent[4].lemma_]), '%Y-%m-%d %H'), ent.doc._.date], 
              'uncertain': [delta_hour, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# Сегодня с 8 утра
'r_event_from_time_daytime_b': {'pattern': [{"LEMMA": {"IN": list(time_events.keys())}}, {"TEXT": "с"}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": list(DAYTIME.keys())}}], 
              'norm': lambda ent: [strptime('{} {}'.format(str(ent.doc._.date.date()-delta_day*time_events[ent[0].lemma_]), int(ent[2].text)+DAYTIME[ent[3].lemma_]), '%Y-%m-%d %H'), ent.doc._.date], 
              'uncertain': [delta_hour, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},

########## BEFORE RULES ##########
# до 9 мая 2010
'r_before_int_month_yeard4d_year': {'pattern': [{"LEMMA": 'до'}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{}{}{}'.format(ent[1].text, MONTHS[ent[2].lemma_][2:], ent[3].text), '%d.%m.%Y'), 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 2},
# до 5-6 декабря 2009
'r_before_int_dash_int_month_yeard4d_year': {'pattern': [{"LEMMA": 'до'}, {"TEXT": {"REGEX": range_r}}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{}{}{}'.format(ent[1][0].text, MONTHS[ent[2].lemma_][2:], ent[3].text), '%d.%m.%Y'), 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 2},
# до сентября
'r_before_month': {'pattern': [{"LEMMA": 'до'}, {"LEMMA": {"IN": list(MONTHS.keys())}}], 
              'norm': lambda ent: strptime('{}{}'.format(MONTHS[ent[1].lemma_], ent.doc._.date.year), '%d.%m.%Y'), 
              'uncertain': delta_month,
              'form': triangle,
              'stamp': 2},
# до декабря 2009
'r_before_month_year': {'pattern': [{"LEMMA": 'до'}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{}{}'.format(MONTHS[ent[1].lemma_], ent[2].text), '%d.%m.%Y'), 
              'uncertain': delta_month,
              'form': triangle,
              'stamp': 2},
# до сегодняшнего дня
'r_before_today': {'pattern': [{"LEMMA": 'до'}, {"TEXT": "сегодняшнего"}, {"TEXT": "дня"}], 
              'norm': lambda ent: ent.doc._.date, 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 2},
# до 2006 года	
'r_before_int_yeard4d_year': {'pattern': [{"LEMMA": 'до'}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('01.07.{}'.format(ent[1].text), '%d.%m.%Y'),
              'uncertain': delta_year,
              'form': triangle,
              'stamp': 2},
# до 9.01.2011	
'r_before_date': {'pattern': [{"LEMMA": 'до'}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime(ent[1].text, '%d.%m.%Y'), 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 2},
# до 9.01.11	
'r_before_shortdate': {'pattern': [{"LEMMA": 'до'}, {"TEXT": {"REGEX": shortdate}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime(ent[1].text, '%d.%m.%y'), 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 2},
# к 29.12	
'r_before_day_month': {'pattern': [{"LEMMA": 'к'}, {"TEXT": {"REGEX": r'^{}.{}$'.format(day,month)}}], 
              'norm': lambda ent: strptime('{}.{}'.format(ent[1].text, ent.doc._.date.year), '%d.%m.%Y'), 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 2},
# до середины ноября 2011
'r_before_monthpart_month_year4d': {'pattern': [{"LEMMA": 'до'}, {"LEMMA": {"IN": list(YEAR_PART.keys())}}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: strptime('{}{}{}'.format(MONTH_PART[ent[1].lemma_],MONTHS[ent[2].lemma_][2:], ent[3].lemma_), '%d.%m.%Y'), 
              'uncertain': relativedelta(days=15),
              'form': triangle,
              'stamp': 1},

########## AGE RULES ##########
# с 12 - ти лет
'r_from_int_dash_ti_year': {'pattern': [{"LEMMA": 'с'}, {"_": {"is_digit": True}}, {"TEXT": {"IN": ["–", "-"]}}, {"LEMMA": "ти"}, {"TEXT": 'лет'}], 
              'norm': lambda ent: [ent.doc._.birthday + relativedelta(years=int(ent[1].text)), ent.doc._.date], 
              'uncertain': [delta_year, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# с 12 лет
'r_from_int_dash_year': {'pattern': [{"LEMMA": 'с'}, {"_": {"is_digit": True}}, {"TEXT": 'лет'}], 
              'norm': lambda ent: [ent.doc._.birthday + relativedelta(years=int(ent[1].text)), ent.doc._.date], 
              'uncertain': [delta_year, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в возрасте 70 лет
'r_in_age_int_year': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": 'возраст'}, {"_": {"is_digit": True}}, {"TEXT": 'лет'}], 
              'norm': lambda ent: [ent.doc._.birthday + relativedelta(years=int(ent[2].text)), ent.doc._.date], 
              'uncertain': [delta_year, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# с 30 - летнего возраста
'r_from_int_dash_year_age': {'pattern': [{"LEMMA": 'с'}, {"_": {"is_digit": True}}, {"TEXT": {"IN": ["–", "-"]}}, {"LEMMA": "летний"}, {"LEMMA": 'возраст'}], 
              'norm': lambda ent: [ent.doc._.birthday + relativedelta(years=int(ent[1].text)), ent.doc._.date], 
              'uncertain': [delta_year, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в 71 год
'r_in_int_year': {'pattern': [{"LEMMA": 'в'}, {"TEXT": {"REGEX": r'^\d\d$'}}, {"TEXT": {"IN": ['год', 'л', 'г', 'лет']}}], #  {"_": {"is_digit": True}}
              'norm': lambda ent: ent.doc._.birthday + relativedelta(years=int(ent[1].text)), 
              'uncertain': delta_year,
              'form': triangle,
              'stamp': 1},

########## DURING RULES ##########
# в течение 2 лет
'r_dur_int_unit': {'pattern': [{"LEMMA": {"IN": ['в', 'на']}}, {"LEMMA": {"IN": ['течение', 'протяжение']}}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(**{relative_dict[ent[3].lemma_]:int(ent[2].text)}), ent.doc._.date], 
              'uncertain': lambda ent: [relativedelta(**{relative_dict[ent[3].lemma_]:1}), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение 2-3 лет
'r_dur_range_unit': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "течение"}, {"TEXT": {"REGEX": range_r}}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(**{relative_dict[ent[3].lemma_]:int(ent[2].text[0])}), ent.doc._.date], 
              'uncertain': lambda ent: [relativedelta(**{relative_dict[ent[3].lemma_]:1}), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение двух лет
'r_dur_num_unit': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "течение"}, {"LEMMA": {"IN": list(digit1d.keys())}}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(**{relative_dict[ent[3].lemma_]:int(digit1d[ent[2].lemma_])}), ent.doc._.date], 
              'uncertain': lambda ent: [relativedelta(**{relative_dict[ent[3].lemma_]:1}), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение месяца
'r_dur_unit': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "течение"}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(**{relative_dict[ent[2].lemma_]:1}), ent.doc._.date], 
              'uncertain': lambda ent: [relativedelta(**{relative_dict[ent[2].lemma_]:1}), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение последних 2 лет
'r_dur_last_int_unit': {'pattern': [{"LEMMA": {"IN": ['в', 'на']}}, {"LEMMA": {"IN": ['течение', 'протяжение']}}, {"LEMMA": "последний"}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(**{relative_dict[ent[4].lemma_]:int(ent[3].text)}), ent.doc._.date], 
              'uncertain': lambda ent: [relativedelta(**{relative_dict[ent[4].lemma_]:1}), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение последних двух лет
'r_dur_last_num_unit': {'pattern': [{"LEMMA": {"IN": ['в', 'на']}}, {"LEMMA": {"IN": ['течение', 'протяжение']}}, {"LEMMA": "последний"}, {"LEMMA": {"IN": list(digit1d.keys())}}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(**{relative_dict[ent[4].lemma_]:int(digit1d[ent[3].lemma_])}), ent.doc._.date], 
              'uncertain': lambda ent: [relativedelta(**{relative_dict[ent[4].lemma_]:1}), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение последних 1,5 месяцев
'r_dur_last_float_month': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "течение"}, {"LEMMA": "последний"}, {"TEXT": {"REGEX": r'^\d[.,]\d$'}}, {"LEMMA": 'месяц'}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(months=int(ent[3].text[0]), days=15), ent.doc._.date], 
              'uncertain': [delta_month, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение последних 1,5 лет
'r_dur_last_float_year': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "течение"}, {"LEMMA": "последний"}, {"TEXT": {"REGEX": r'^\d[.,]\d$'}}, {"LEMMA": 'год'}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(years=int(ent[3].text[0]), months=6), ent.doc._.date], 
              'uncertain': [delta_year, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение последних нескольких лет
'r_dur_last_sev_year': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "течение"}, {"LEMMA": "последний"}, {"LEMMA": "несколько"}, {"LEMMA": 'год'}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(years=3), ent.doc._.date], 
              'uncertain': [delta_year, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение последних нескольких лет
'r_dur_last_sev_year_ad': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "течение"}, {"TEXT": "посл"}, {"TEXT": "неск"}, {"LEMMA": 'год'}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(years=3), ent.doc._.date], 
              'uncertain': [delta_year, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение 2 последних лет
'r_dur_int_last_unit': {'pattern': [{"LEMMA": {"IN": ['в', 'на']}}, {"LEMMA": {"IN": ['течение', 'протяжение']}}, {"_": {"is_digit": True}}, {"LEMMA": "последний"}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(**{relative_dict[ent[4].lemma_]:int(ent[2].text)}), ent.doc._.date], 
              'uncertain': lambda ent: [relativedelta(**{relative_dict[ent[4].lemma_]:1}), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение двух последних лет
'r_dur_num_last_unit': {'pattern': [{"LEMMA": {"IN": ['в', 'на']}}, {"LEMMA": {"IN": ['течение', 'протяжение']}}, {"LEMMA": {"IN": list(digit1d.keys())}}, {"LEMMA": "последний"}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(**{relative_dict[ent[4].lemma_]:int(digit1d[ent[2].lemma_])}), ent.doc._.date], 
              'uncertain': lambda ent: [relativedelta(**{relative_dict[ent[4].lemma_]:1}), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение 1,5 последних месяцев
'r_dur_float_last_month': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "течение"}, {"TEXT": {"REGEX": r'^\d[.,]\d$'}}, {"LEMMA": "последний"}, {"LEMMA": 'месяц'}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(months=int(ent[2].text[0]), days=15), ent.doc._.date], 
              'uncertain': [delta_month, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение 1,5 последних лет
'r_dur_float_last_year': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "течение"}, {"TEXT": {"REGEX": r'^\d[.,]\d$'}}, {"LEMMA": "последний"}, {"LEMMA": 'год'}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(years=int(ent[2].text[0]), months=6), ent.doc._.date], 
              'uncertain': [delta_year, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение 1,5 месяцев
'r_dur_float_month': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "течение"}, {"TEXT": {"REGEX": r'^\d[.,]\d$'}}, {"LEMMA": 'месяц'}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(months=int(ent[2].text[0]), days=15), ent.doc._.date], 
              'uncertain': [delta_month, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение 1,5 лет
'r_dur_float_year': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "течение"}, {"TEXT": {"REGEX": r'^\d[.,]\d$'}}, {"LEMMA": 'год'}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(years=int(ent[2].text[0]), months=6), ent.doc._.date], 
              'uncertain': [delta_year, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# Последние 1.5 недели
'r_last_float_unit': {'pattern': [{"LEMMA": "последний"}, {"TEXT": {"REGEX": r'^\d[.,]\d$'}}, {"LEMMA": {"IN": ["неделя", "день"]}}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(**{relative_dict[ent[2].lemma_]:int(float(ent[1].text.replace(',', '.')))}), ent.doc._.date], 
              'uncertain': [delta_year, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение последнего месяца
'r_dur_last_unit': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "течение"}, {"LEMMA": "последний"}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(**{relative_dict[ent[3].lemma_]:1}), ent.doc._.date], 
              'uncertain': lambda ent: [relativedelta(**{relative_dict[ent[3].lemma_]:1}), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение нескольких лет
'r_dur_sev_unit': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "течение"}, {"LEMMA": {"IN": ["несколько", "много"]}}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(**{relative_dict[ent[3].lemma_]:3}), ent.doc._.date], 
              'uncertain': lambda ent: [relativedelta(**{relative_dict[ent[3].lemma_]:3}), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в последние несколько дней
'r_dur_last_sev_unit': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "последний"}, {"LEMMA": "несколько"}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(**{relative_dict[ent[3].lemma_]:3}), ent.doc._.date], 
              'uncertain': lambda ent: [relativedelta(**{relative_dict[ent[3].lemma_]:3}), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# последних 2 лет
'r_last_int_unit': {'pattern': [{"LEMMA": "последний"}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": unit + ['мес']}}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(**{relative_dict[ent[2].lemma_]:int(ent[1].text)}), ent.doc._.date], 
              'uncertain': lambda ent: [relativedelta(**{relative_dict[ent[2].lemma_]:1}), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# последних двух лет
'r_last_num_unit': {'pattern': [{"LEMMA": "последний"}, {"LEMMA": {"IN": list(digit1d.keys())}}, {"LEMMA": {"IN": unit + ['мес']}}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(**{relative_dict[ent[2].lemma_]:int(digit1d[ent[1].lemma_])}), ent.doc._.date], 
              'uncertain': lambda ent: [relativedelta(**{relative_dict[ent[2].lemma_]:1}), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение полугода
'r_dur_halfyear': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "течение"}, {"TEXT": "полугода"}], 
              'norm': lambda ent: [ent.doc._.date - relativedelta(months=6), ent.doc._.date], 
              'uncertain': lambda ent: [relativedelta(months=1), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# в течение 5-7 минут
'r_dur_range_minute': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "течение"}, {"TEXT": {"REGEX": range_r}}, {"LEMMA": "минута"}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 4},

########## DEPENDENT EVENTS ##########
# через 1 - 2 месяца
'r_thr_int_dash_int_unit': {'pattern': [{"LEMMA": {"IN": ["через", "спустя"]}}, {"_": {"is_digit": True}}, {"TEXT": {"IN": ["–", "-"]}}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 4},
# через 1-2 месяца
'r_thr_range_unit': {'pattern': [{"LEMMA": {"IN": ["через", "спустя"]}}, {"TEXT": {"REGEX": range_r}}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 4},
# через 1 месяц
'r_thr_int_unit': {'pattern': [{"LEMMA": {"IN": ["через", "спустя"]}}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": unit + ['мес']}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 4},
# через 5 минут
'r_thr_int_minute': {'pattern': [{"LEMMA": {"IN": ["через", "спустя"]}}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": ['минута', 'мина']}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 4},
# через два месяц
'r_thr_num_unit': {'pattern': [{"LEMMA": {"IN": ["через", "спустя"]}}, {"LEMMA": {"IN": list(digit1d.keys())}}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 4},
# через месяц
'r_thr_unit': {'pattern': [{"LEMMA": {"IN": ["через", "спустя"]}}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 4},
# за день до этого
'r_unit_before': {'pattern': [{"LEMMA": "за"}, {"LEMMA": {"IN": unit}}, {"LEMMA": "до"}, {"LEMMA": "это"}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 4},
# через некоторое время
'r_thr_some_time': {'pattern': [{"LEMMA": {"IN": ["через", "спустя"]}}, {"LEMMA": "некоторый"}, {"LEMMA": "время"}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 4},
# через несколько дней
'r_thr_some_unit': {'pattern': [{"LEMMA": {"IN": ["через", "спустя"]}}, {"LEMMA": "несколько"}, {"LEMMA": {"IN": unit + ['минута']}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 4},
# спустя пол часа
'r_thr_half_unit': {'pattern': [{"LEMMA": {"IN": ["через", "спустя"]}}, {"TEXT": "пол"}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 4},
# С этого же года
'rule_this_unit': {'pattern': [{"LEMMA": "с"}, {"LEMMA": "этого"}, {"TEXT": "же"}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 4},
# С этого года
'rule_this_unit_a': {'pattern': [{"LEMMA": "с"}, {"LEMMA": "этого"}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 4},
# за 2 месяца
'r_za_int_unit': {'pattern': [{"LEMMA": "за"}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": ['день', 'час', 'неделя', 'месяц', 'сутки']}}],
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 4},
# после 13 лет
'r_after_int_unit': {'pattern': [{"LEMMA": "после"}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 4},

########## TRAPEZOID FORM ##########
# с 2005 года по 2009 год
'r_from_year4d_year_till_year4d_year': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год'}, {"TEXT": 'по'}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год'}], 
              'norm': lambda ent: [strptime('01.07.{}'.format(ent[1].text), '%d.%m.%Y'), strptime('01.07.{}'.format(ent[4].text), '%d.%m.%Y')], 
              'uncertain': delta_year,
              'form': trapezoid,
              'stamp': 2},
# С декабря 2008 года по март 2009 года
'r_from_month_year4d_year_till_month_year4d_year': {'pattern': [{"LEMMA": 'с'}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год'}, {"TEXT": 'по'}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год'}], 
              'norm': lambda ent: [strptime('{}{}'.format(MONTHS[ent[1].lemma_], ent[2].text), '%d.%m.%Y'), strptime('{}{}'.format(MONTHS[ent[5].lemma_],ent[6].text), '%d.%m.%Y')], 
              'uncertain': delta_month,
              'form': trapezoid,
              'stamp': 2},
# с 08.06.10 по 22.06.10
'r_from_shortdate_till_shortdate': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": shortdate}}, {"TEXT": 'по'}, {"TEXT": {"REGEX": shortdate}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime(ent[1].text, '%d.%m.%y'), strptime(ent[3].text, '%d.%m.%y')], 
              'uncertain': delta_day,
              'form': trapezoid,
              'stamp': 2},
# с 08.06.10 г по 22.06.10 г
'r_from_shortdate_till_shortdate_year': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": shortdate}}, {"LEMMA": 'год'}, {"TEXT": 'по'}, {"TEXT": {"REGEX": shortdate}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime(ent[1].text, '%d.%m.%y'), strptime(ent[4].text, '%d.%m.%y')], 
              'uncertain': delta_day,
              'form': trapezoid,
              'stamp': 2},
# с 08.06.2010 по 22.06.2010
'r_from_date_till_date': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": date}}, {"TEXT": 'по'}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime(ent[1].text, '%d.%m.%Y'), strptime(ent[3].text, '%d.%m.%Y')], 
              'uncertain': delta_day,
              'form': trapezoid,
              'stamp': 2},
# с 08.06.2010 г по 22.06.2010 г
'r_from_date_till_date_year': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год'}, {"TEXT": 'по'}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime(ent[1].text, '%d.%m.%Y'), strptime(ent[4].text, '%d.%m.%Y')], 
              'uncertain': delta_day,
              'form': trapezoid,
              'stamp': 2},
# С 08.06 по 10.06.08
'r_from_date_my2d_till_date': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": date_my2d}}, {"TEXT": 'по'}, {"TEXT": {"REGEX": shortdate}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime(ent[1].text+ent[3].text[-3:], '%d.%m.%y'), strptime(ent[3].text, '%d.%m.%y')], 
              'uncertain': delta_day,
              'form': trapezoid,
              'stamp': 2},
# с 08.06.10 - 22.06.10
'r_from_date_dash_date': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": shortdate}}, {"TEXT": {"IN": ["–", "-"]}}, {"TEXT": {"REGEX": shortdate}}], 
              'norm': lambda ent: [strptime(ent[1].text, '%d.%m.%y'), strptime(ent[3].text, '%d.%m.%y')], 
              'uncertain': delta_day,
              'form': trapezoid,
              'stamp': 2},
# 08.06.10 - 22.06.10
'r_date_dash_date': {'pattern': [{"TEXT": {"REGEX": shortdate}}, {"TEXT": {"IN": ["–", "-"]}}, {"TEXT": {"REGEX": shortdate}}], 
              'norm': lambda ent: [strptime(ent[0].text, '%d.%m.%y'), strptime(ent[2].text, '%d.%m.%y')], 
              'uncertain': delta_day,
              'form': trapezoid,
              'stamp': 2},
# с 4.06 – 17.06
'r_from_shortdate_dash_shortdate': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": r'^{}.{}$'.format(day,month)}}, {"TEXT": {"IN": ["–", "-"]}}, {"TEXT": {"REGEX": r'^{}.{}$'.format(day,month)}}], 
              'norm': lambda ent: [strptime(ent[1].text+'.'+str(ent.doc._.date.year), '%d.%m.%Y'), strptime(ent[3].text+'.'+str(ent.doc._.date.year), '%d.%m.%Y')], 
              'uncertain': delta_day,
              'form': trapezoid,
              'stamp': 2},
# С 6.12.-10.12.2010
'r_from_shortdate_dash_date': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": r'^{}.{}$'.format(day,month)}}, {"TEXT": {"IN": ["–", "-"]}}, {"TEXT": {"REGEX": date}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime('{}.{}'.format(ent[1].text, ent[3].text[-4:]), '%d.%m.%Y'), strptime(ent[3].text, '%d.%m.%Y')], 
              'uncertain': delta_day,
              'form': trapezoid,
              'stamp': 2},
# # С 1.12-21.12.10 года
'r_from_shortdate_dash_date_b': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": r'^{}.{}$'.format(day,month)}}, {"TEXT": {"IN": ["–", "-"]}}, {"TEXT": {"REGEX": shortdate}}, {"LEMMA": 'год', "OP": "?"}], 
              'norm': lambda ent: [strptime('{}.{}'.format(ent[1].text, ent[3].text[-2:]), '%d.%m.%y'), strptime(ent[3].text, '%d.%m.%y')], 
              'uncertain': delta_day,
              'form': trapezoid,
              'stamp': 2},
# 1976 - 1978 гг
'r_yead4d_dash_year4d_year': {'pattern': [{"TEXT": {"REGEX": yearfull}}, {"TEXT": {"IN": ["–", "-"]}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год'}], 
              'norm': lambda ent: [strptime('01.07.{}'.format(ent[0].text), '%d.%m.%y'), strptime('01.07.{}'.format(ent[2].text), '%d.%m.%y')], 
              'uncertain': delta_year,
              'form': trapezoid,
              'stamp': 2},
# с марта по апрель 2010 года
'r_from_month_till_month_year4d_year': {'pattern': [{"LEMMA": 'с'}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": 'по'}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год'}], 
              'norm': lambda ent: [strptime(MONTHS[ent[1].lemma_]+ent[4].text, '%d.%m.%Y'), strptime(MONTHS[ent[3].lemma_]+ent[4].text, '%d.%m.%Y')], 
              'uncertain': delta_month,
              'form': trapezoid,
              'stamp': 2},
# С декабря 2009 по май 2010 года
'r_from_month_year4d_till_month_year4d_year': {'pattern': [{"LEMMA": 'с'}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"TEXT": 'по'}, {"LEMMA": {"IN": list(MONTHS.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"LEMMA": 'год'}], 
              'norm': lambda ent: [strptime('{}{}'.format(MONTHS[ent[1].lemma_],ent[2].text), '%d.%m.%Y'), strptime('{}{}'.format(MONTHS[ent[4].lemma_],ent[5].text), '%d.%m.%Y')], 
              'uncertain': delta_month,
              'form': trapezoid,
              'stamp': 2},
# В последние 2 недели
'r_in_last_int_unit': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "последний"}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: [ent.doc._.date-delta_dict[ent[3].lemma_]*int(ent[2].lemma_), ent.doc._.date], 
              'uncertain': lambda ent: [delta_dict[ent[3].lemma_], relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# последние недели
'r_last_unit': {'pattern': [{"LEMMA": "последний"}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: [ent.doc._.date-delta_dict[ent[1].lemma_], ent.doc._.date], 
              'uncertain': lambda ent: [delta_dict[ent[1].lemma_], relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# последние 3 - 4 дня
'r_last_int_dash_int_unit': {'pattern': [{"LEMMA": "последний"}, {"_": {"is_digit": True}}, {"TEXT": {"IN": ["–", "-"]}}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: [ent.doc._.date-delta_dict[ent[4].lemma_]*int(ent[3].lemma_), ent.doc._.date], 
              'uncertain': lambda ent: [delta_dict[ent[4].lemma_], relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# последние 3-4 дня
'r_last_range_unit': {'pattern': [{"LEMMA": "последний"}, {"TEXT": {"REGEX": range_r}}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: [ent.doc._.date-delta_dict[ent[2].lemma_]*int(ent[1].lemma_[2]), ent.doc._.date], 
              'uncertain': lambda ent: [delta_dict[ent[2].lemma_], relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# 'более 10 лет'
'r_more_int_unit': {'pattern': [{"LEMMA": {"IN": ["более", "около"]}}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": unit}}],
              'norm': lambda ent: [ent.doc._.date-relativedelta(**{relative_dict[ent[2].lemma_]:int(ent[1].text)}), ent.doc._.date], 
              'uncertain': lambda ent: [delta_dict[ent[2].lemma_]*2, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# Около семи лет
'r_more_num_unit': {'pattern': [{"LEMMA": {"IN": ["более", "около"]}}, {"LEMMA": {"IN": list(digit1d.keys())}}, {"LEMMA": {"IN": unit}}],
              'norm': lambda ent: [ent.doc._.date-relativedelta(**{relative_dict[ent[2].lemma_]:digit1d[ent[1].lemma_]}), ent.doc._.date], 
              'uncertain': lambda ent: [delta_dict[ent[2].lemma_]*2, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# Около года
'r_around_unit': {'pattern': [{"LEMMA": {"IN": fuzzy_words}}, {"LEMMA": {"IN": unit}}],
              'norm': lambda ent: [ent.doc._.date-relativedelta(**{relative_dict[ent[1].lemma_]:1}), ent.doc._.date], 
              'uncertain': lambda ent: [delta_dict[ent[1].lemma_]*2, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# лет 7-8
'r_unit_range': {'pattern': [{"TEXT": "лет"}, {"TEXT": {"REGEX": range_r}}],
              'norm': lambda ent: [ent.doc._.date-relativedelta(**{relative_dict[ent[0].lemma_]:int(ent[1].text[0])}), ent.doc._.date], 
              'uncertain': lambda ent: [delta_dict[ent[0].lemma_]*1, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# лет 7
'r_unit_int': {'pattern': [{"TEXT": "лет"}, {"_": {"is_digit": True}}],
              'norm': lambda ent: [ent.doc._.date-relativedelta(**{relative_dict[ent[0].lemma_]:int(ent[1].text)}), ent.doc._.date], 
              'uncertain': lambda ent: [delta_dict[ent[0].lemma_]*1, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# за сутки
'r_za_unit': {'pattern': [{"LEMMA": "за"}, {"LEMMA": {"IN": unit}}],
              'norm': lambda ent: [ent.doc._.date-relativedelta(**{relative_dict[ent[1].lemma_]:1}), ent.doc._.date], 
              'uncertain': lambda ent: [delta_dict[ent[1].lemma_]*1, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# 3 месяца
'r_int_unit': {'pattern': [{"_": {"is_digit": True}}, {"LEMMA": {"IN": ['день', 'час', 'неделя', 'месяц', 'сутки']}}],
              'norm': lambda ent: [ent.doc._.date-relativedelta(**{relative_dict[ent[1].lemma_]:int(ent[0].text)}), ent.doc._.date], 
              'uncertain': lambda ent: [delta_dict[ent[1].lemma_], relativedelta(days=0)], #*int(ent[0].text)
              'form': trapezoid,
              'stamp': 2},
# два дня
'r_num_unit': {'pattern': [{"LEMMA": {"IN": list(digit1d.keys())}}, {"LEMMA": {"IN": ['день', 'час', 'неделя', 'месяц', 'сутки']}}],
              'norm': lambda ent: [ent.doc._.date-relativedelta(**{relative_dict[ent[1].lemma_]:int(digit1d[ent[0].lemma_])}), ent.doc._.date], 
              'uncertain': lambda ent: [delta_dict[ent[1].lemma_]*int(digit1d[ent[0].lemma_]), relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},
# 3 года
'r_int_year': {'pattern': [{"_": {"is_digit": True}}, {"TEXT": {"IN": ['года', 'лет']}}],
              'norm': lambda ent: [ent.doc._.date-relativedelta(**{relative_dict[ent[1].lemma_]:int(ent[0].text)}), ent.doc._.date], 
              'uncertain': lambda ent: [delta_dict[ent[1].lemma_]*1, relativedelta(days=0)],
              'form': trapezoid,
              'stamp': 2},

########## REPEATABLE RULES ##########
# '1 раз в мес'
'r_int_times_in_unit': {'pattern': [{"_": {"is_digit": True}}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# 'два раз в мес'
'r_num_times_in_unit': {'pattern': [{"LEMMA": {"IN": list(digit1d.keys())}}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# 'до 1 раз в мес'
'r_prep_int_times_in_unit': {'pattern': [{"LEMMA": {"IN": ["до", "около"]}}, {"_": {"is_digit": True}}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# 'до 1 раза в месяц – 2 месяца'
'r_prep_int_times_in_unit_dash_int_unit': {'pattern': [{"LEMMA": {"IN": ["до", "около"]}}, {"_": {"is_digit": True}}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"LEMMA": {"IN": time_unit}}, {"TEXT": {"IN": ["–", "-"]}}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# 'до двух раз в мес'
'r_prep_num_times_in_unit': {'pattern': [{"LEMMA": {"IN": ["до", "около"]}}, {"LEMMA": {"IN": list(digit1d.keys())}}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# 'до 1 раз в 3-4 дня'
'r_prep_int_times_in_range_unit': {'pattern': [{"LEMMA": {"IN": ["до", "около"]}}, {"_": {"is_digit": True}}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"TEXT": {"REGEX": range_r}}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# '1 раз в 3-4 дня'
'r_int_times_in_range_unit': {'pattern': [{"_": {"is_digit": True}}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"TEXT": {"REGEX": range_r}}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# 'один раз в 3-4 дня'
'r_num_times_in_range_unit': {'pattern': [{"LEMMA": {"IN": list(digit1d.keys())}}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"TEXT": {"REGEX": range_r}}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# '1-2 раз в мес'
'r_range_times_in_unit': {'pattern': [{"TEXT": {"REGEX": range_r}}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# 2-3 в месяц
'r_range_in_unit': {'pattern': [{"TEXT": {"REGEX": range_r}}, {"TEXT": "в"}, {"LEMMA": {"IN": unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# '1-2 раз в 6 мес'
'r_range_times_in_int_unit': {'pattern': [{"TEXT": {"REGEX": range_r}}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# '1-2 раз в шесть мес'
'r_range_times_in__numunit': {'pattern': [{"TEXT": {"REGEX": range_r}}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"LEMMA": {"IN": list(digit1d.keys())}}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# '1 раз в 6 мес'
'r_int_times_in_int_unit': {'pattern': [{"_": {"is_digit": True}}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# 'два раз в 6 мес'
'r_num_times_in_int_unit': {'pattern': [{"LEMMA": {"IN": list(digit1d.keys())}}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# '1 раз в шесть мес'
'r_int_times_in_num_unit': {'pattern': [{"_": {"is_digit": True}}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"LEMMA": {"IN": list(digit1d.keys())}}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# 'один раз в шесть мес'
'r_num_times_in_num_unit': {'pattern': [{"LEMMA": {"IN": list(digit1d.keys())}}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"LEMMA": {"IN": list(digit1d.keys())}}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# 1 раз в 6 мес - 8 мес
'r_int_times_in_int_unit_dash_int_unit': {'pattern': [{"_": {"is_digit": True}}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": time_unit}}, {"TEXT": {"IN": ["-", "–"]}}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# до 1 в 3 месяца
'r_before_int_in_int_unit': {'pattern': [{"LEMMA": "до"}, {"_": {"is_digit": True}}, {"TEXT": "в"}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# раз в мес
'r_times_in_unit': {'pattern': [{"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# раз в шесть мес
'r_times_in_num_unit': {'pattern': [{"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"LEMMA": {"IN": list(digit1d.keys())}}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# раз в 6 мес
'r_times_in_int_unit': {'pattern': [{"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"_": {"is_digit": True}}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# до нескольких раз в месяц | несколько раз в месяц
'r_prep_sev_times_in_unit': {'pattern': [{"POS": {"IN": ["ADP"]}, "OP": "?"}, {"LEMMA": 'несколько'}, {"TEXT": {"IN": ["раза", "раз", "р"]}}, {"TEXT": "в"}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# ежедневно
'r_regular': {'pattern': [{"LEMMA": {"IN": time_regular}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},
# 5 дней в неделю
'r_int_unit_in_unit': {'pattern': [{"_": {"is_digit": True}}, {"LEMMA": {"IN": time_unit}}, {"TEXT": "в"}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 3},

########## RULES WITHOUT NORMAL FORM ##########
# 'несколько лет'
'r_sev_years': {'pattern': [{"LEMMA": "несколько"}, {"LEMMA": {"IN": time_unit}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 2},
# с 16.00
'r_from_time': {'pattern': [{"LEMMA": 'с'}, {"TEXT": {"REGEX": time}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 2},
# В 9.00
'r_in_time': {'pattern': [{"LEMMA": 'в'}, {"TEXT": {"REGEX": time}}], 
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 1},
# На 3 день
'r_on_int_year': {'pattern': [{"LEMMA": 'на'}, {"_": {"is_digit": True}}, {"TEXT": {"IN": unit}}],
              'norm': lambda ent: None, 
              'uncertain': None,
              'form': [None],
              'stamp': 1},

########## OTHER RULES ##########
# в конце 2009 , начале 2010
'r_in_part_year4d_part_year4d': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": {"IN": list(YEAR_PART.keys())}}, {"TEXT": {"REGEX": yearfull}}, {"TEXT": ','}, {"LEMMA": {"IN": list(YEAR_PART.keys())}}, {"TEXT": {"REGEX": yearfull}}],
              'norm': lambda ent: strptime('{}{}'.format(YEAR_PART[ent[4].lemma_], ent[5].text), '%d.%m.%Y'), 
              'uncertain': relativedelta(days=45),
              'form': triangle,
              'stamp': 1},
# в настоящее время
'r_now': {'pattern': [{"LEMMA": 'в'}, {"LEMMA": "настоящий"}, {"LEMMA": "время"}],
              'norm': lambda ent: ent.doc._.date, 
              'uncertain': delta_day,
              'form': triangle,
              'stamp': 2},
}