from datetime import datetime
from itertools import islice

import dateparser
import rutimeparser
import stanza
from dateparser.search import search_dates
from dateutil.relativedelta import relativedelta
from spacy_stanza import StanzaLanguage

from TimeExpressions.yargy_rules import interpret_dict, parser_time, relative_dict, rule_stamps


class TimeProcessor:
    """Processing time expression
    This class includes methods for parsing time expression data for future mining.
    It includes methods normalization of timestapms and getting stamps.
    Parameters
    ----------
    model : Spacy model, (default=None)
        Define which model will be used for tokenization and lemmatization

    Examples
    --------
    >>> from TimeExpessions.TimeProcessor import TimeProcessor
    >>> time_processor = TimeProcessor()
    >>> time_processor.process(['Около трех лет назад у пациента синусовый ритм был восстановлен ЭИТ.'],
    ...            date = ['2010-12-22 18:13:14'],
    ...            birth_date = ['1981-06-25 18:11:43'])
    {'expression': [['Около трех лет назад']],
     'normal_form': [[datetime.datetime(2007, 12, 22, 18, 13, 14)]],
     'stamp': [[1]]}
    """

    def __init__(self, model=None):

        if model is None:
            snlp = stanza.Pipeline(lang="ru")
            self.nlp = StanzaLanguage(snlp)
        else:
            self.nlp = model

    def get_stapm(self, expression, rule):
        """
        get stamp of time expressions.
        Parameters
        ----------
        expression : str
            Time expression.
        rule: str:
            Rule which found time expression.
        Returns
        -------
        stamp : int
            Stamp of time expression:
            1 - once-time
            2 - continious
            3 - repeatable
            4 - relative
        """
        stamp = None
        if rule in rule_stamps["once_rules"]:
            stamp = 1
        elif rule in rule_stamps["continious_rules"]:
            stamp = 2
        elif rule in rule_stamps["repeatable_rules"]:
            stamp = 3
        elif rule in rule_stamps["relative_rules"]:
            stamp = 4
        return stamp

    def lemma(self, expressions):
        """
        Lemmatize time expressions.
        Parameters
        ----------
        expression : str
            Time expression.
        Returns
        -------
        normal_form : str
            Lemma of time expression without preps and verbs.
        """
        normal_expr = list()
        for word in self.nlp(expressions):
            if word.pos_ not in ["PREP", "ADP", "VERB"]:
                normal_expr.append(word.lemma_.strip())

        return normal_expr

    def pre_proccess(self, expressions):
        """
        Preprocess time expressions for parsers.
        Parameters
        ----------
        expression : str
            Time expression.
        Returns
        -------
        normal_form : str
            Lemma of time expression without preps and verbs.
            For words such 'утро','вечер','ночь', 'лет' save the case.
            Remove stop words such 'год', 'месяц', 'день'.
        """
        normal_expr = list()
        for word in self.nlp(expressions):
            if (
                (word.pos_ not in ["PREP", "ADP", "VERB"])
                and (word.lemma_.strip() not in ["год", "месяц", "день"])
                and (str(word) not in ["-", "ти", "х"])
            ):
                if word.lemma_.strip() in ["утро", "вечер", "ночь"]:
                    normal_expr.append(str(word))
                else:
                    normal_expr.append(word.lemma_.strip())
            if str(word) == "лет":
                normal_expr.append(str(word))

        normal_expr = " ".join(normal_expr)
        return normal_expr

    def normalize(self, expression, rule, date, birth_date):
        """
        Normalize time expressions.
        Parameters
        ----------
        expression : str
            Time expression.
        rule : str
            Rule which found time expression.
        date : datetime,
            Date of observation.
        birth_date : datetime,
            Birth date.
        Returns
        -------
        normal_form : str
            Normal form of time expression.
        """
        normal_expr = self.pre_proccess(expression)
        date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        normal_form = list()
        s = normal_expr.split()

        if rule in [
            "rule_in_yearfull_unit",
            "rule_from_yearfull_unit",
            "rule_yearfull",
        ]:
            date = datetime.strptime("2010-01-01", "%Y-%m-%d")
            normal_form = dateparser.parse(
                normal_expr,
                settings={"PREFER_DAY_OF_MONTH": "first", "RELATIVE_BASE": date},
            )
        elif rule is "rule_from_yearfull_unit":
            lem = self.lemma(expression)
            normal_form.append(date - relative_dict[lem[-1]])
            normal_form.append(date)
        elif rule == "rule_dur_int_unit":
            s = " ".join(s[-2:]) + " назад"
            try:
                normal_form.append(rutimeparser.parse(expression, now=date))
            except:
                normal_form.append(
                    dateparser.parse(s, settings={"RELATIVE_BASE": date})
                )
            normal_form.append(date)
        elif rule == "rule_around_int_unit":
            s = " ".join(s[-2:]) + " назад"
            normal_form.append(dateparser.parse(s, settings={"RELATIVE_BASE": date}))
            normal_form.append(date)
        #         elif rule in ["rule_from_int_unit", 'rule_from_int_dash_ti_unit'] and birth_date:
        #             birth_date = datetime.strptime(str(birth_date)[:10], '%Y-%m-%d')
        #             years = [int(s) for s in normal_expr.split() if s.isdigit()][0]
        #             normal_form = birth_date + relativedelta(years=years)
        elif rule in ["rule_season_int_unit", "rule_from_season_int_unit"]:
            normal_form = datetime.strptime(interpret_dict[s[0]] + s[1], "%d.%m.%Y")
        elif rule in [
            "rule_dur_last_int_h_unit",
            "rule_more_int_unit",
            "rule_dur_int_h_unit",
            "rule_dur_last_int_unit",
            "rule_dur_int_last_unit",
        ]:
            lem = self.lemma(expression)
            digit = [int(s) for s in normal_expr.split() if s.isdigit()][0]
            expression = str(digit) + " " + lem[-1] + " назад"
            normal_form.append(
                dateparser.parse(expression, settings={"RELATIVE_BASE": date})
            )
            normal_form.append(date)
        elif (
            rule
            in [
                "rule_in_int_unit",
                "rule_in_age_int_unit",
                "rule_from_int_unit",
                "rule_from_int_dash_ti_unit",
            ]
            and birth_date
        ):
            if s[-1] in ["год", "лет"]:
                birth_date = datetime.strptime(str(birth_date)[:10], "%Y-%m-%d")
                years = [int(s) for s in normal_expr.split() if s.isdigit()][0]
                normal_form = date - relativedelta(years=years)
        elif rule == "rule_prep_month":
            normal_form = datetime.strptime(
                interpret_dict[s[0]] + str(date)[:4], "%m.%Y"
            )
        elif rule == "rule_events":
            lem = self.lemma(expression)
            normal_form = date - relative_dict[lem[-1]]
        elif rule in ["rule_dur_unit", "rule_last_unit", "rule_dur_last_unit"]:
            lem = self.lemma(expression)
            expression = lem[-1] + " назад"
            try:
                normal_form.append(rutimeparser.parse(expression, now=date))
            except:
                normal_form.append(
                    dateparser.parse(expression, settings={"RELATIVE_BASE": date})
                )
            normal_form.append(date)
        elif rule == "rule_dur_last_numr_unit":
            lem = self.lemma(expression)
            expression = " ".join(lem[-2:]) + " назад"
            try:
                normal_form.append(rutimeparser.parse(expression, now=date))
            except:
                normal_form.append(
                    dateparser.parse(expression, settings={"RELATIVE_BASE": date})
                )
            normal_form.append(date)
        elif rule == "rule_dur_last_numr_unit":
            lem = self.lemma(expression)
            try:
                expression = " ".join(lem[-2:]) + " назад"
                normal_form = dateparser.parse(
                    expression, settings={"RELATIVE_BASE": date}
                )
            except:
                pass
        elif rule == "rule_prep_month_month_yearfull_unit":
            digit = [int(s) for s in normal_expr.split() if s.isdigit()][0]
            normal_form.append(
                datetime.strptime(interpret_dict[s[0]] + str(digit), "%m.%Y")
            )
            normal_form.append(
                datetime.strptime(interpret_dict[s[1]] + str(digit), "%m.%Y")
            )
        elif rule in ["rule_from_part_yearfull", "rule_in_part_yearfull"]:
            normal_form.append(
                datetime.strptime(interpret_dict[s[0]] + s[1], "%d.%m.%Y")
            )
        elif rule == "rule_from_date_till_date":
            normal_form.append(dateparser.parse(s[0]))
            normal_form.append(dateparser.parse(s[1]))
        elif rule in rule_stamps["relative_rules"] + rule_stamps["repeatable_rules"] + [
            "rule_this_year",
            "rule_time_unit",
            "rule_time",
        ]:
            return normal_form
        elif rule in ["rule_prep_daytime_unit", "rule_daytime_date"]:
            lem = self.lemma(expression)
            expression = expression.split()
            try:
                normal_form.append(
                    datetime.strptime(
                        interpret_dict[lem[0]] + " " + expression[-1], "%H.%M %d.%m.%Y"
                    )
                )
            except:
                normal_form.append(
                    datetime.strptime(
                        interpret_dict[lem[0]] + " " + expression[-1], "%H.%M %d.%m.%y"
                    )
                )
        elif rule == "rule_time_year":
            try:
                normal_form.append(datetime.strptime(s[0], "%m.%y"))
            except:
                pass
        elif rule == "rule_int_unit_ago":
            normal_form = dateparser.parse(
                expression,
                settings={"PREFER_DAY_OF_MONTH": "first", "RELATIVE_BASE": date},
            )
        elif rule == "rule_around_numr_unit_ago":
            lem = " ".join(self.lemma(expression))
            normal_form = rutimeparser.parse(lem, now=date)

        if not normal_form:
            normal_form = dateparser.parse(
                normal_expr,
                settings={"PREFER_DAY_OF_MONTH": "first", "RELATIVE_BASE": date},
            )

        if not normal_form:
            normal_form = search_dates(
                normal_expr,
                settings={"PREFER_DAY_OF_MONTH": "first", "RELATIVE_BASE": date},
            )
            if normal_form:
                for i in range(len(normal_form)):
                    normal_form[i] = normal_form[i][1]

        if not normal_form:
            try:
                normal_form = rutimeparser.parse(normal_expr, now=date)
            except:
                pass

        return normal_form

    def process(self, sentences, date=None, birth_date=None):
        """
        Process time expressions.
        Parameters
        ----------
        sentences : list
            List of sentences.
        date : list
            List of dates of observation.
        birth_date : list, (default=None)
            List of birth dates.
        Returns
        -------
        result : dict
            Dict with time expressions, normal forms and stamps.
        """
        
        if date is None:
            date = datetime.now()
            date = str(date.strftime("%Y-%m-%d %H:%M:%S"))
            date = [date] * len(sentences)
            
        if birth_date is None:
            birth_date = [None] * len(sentences)
        
        TIME_EXPR = list()
        NORMAL_FORMS = list()
        STAMPS = list()
        for sent in range(len(sentences)):
            time_expr = list()
            normal_forms = list()
            stamps = list()
            if sentences[sent][-1] != ".":
                sentences[sent] = sentences[sent] + "."
            for match in parser_time.findall(sentences[sent]):
                s = " ".join([_.value for _ in match.tokens])
                if s not in ["в г", "г", "года", "лет"]:
                    time_expr.append(s)
                    rule_name = next(islice(match.tree.walk(), 1, None)).label
                    stamps.append(self.get_stapm(s, rule_name))
                    normal_forms.append(
                        self.normalize(s, rule_name, date[sent], birth_date[sent])
                    )

            TIME_EXPR.append(time_expr)
            NORMAL_FORMS.append(normal_forms)
            STAMPS.append(stamps)

        result = {"expression": TIME_EXPR, "normal_form": NORMAL_FORMS, "stamp": STAMPS}

        return result
