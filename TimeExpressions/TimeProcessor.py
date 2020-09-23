import re
from datetime import datetime

import dateparser
import rutimeparser
import stanza
from dateparser.search import search_dates
from dateutil.relativedelta import relativedelta
from deeppavlov import build_model
from spacy.pipeline import EntityRuler
from spacy.tokens import Doc, Span
from spacy_stanza import StanzaLanguage
from TimeExpressions.patterns import interpret_dict, patterns

import logging
import os
import warnings

import tensorflow as tf

config = tf.ConfigProto()
config.gpu_options.allow_growth = True

class TimeProcessor:
    """Processing time expression
    This class includes methods for parsing time expression data for future mining.
    It includes methods normalization of time expressions, getting stamps and finding events.
    Results are available through attributes ent.text (time expression), ent._.timestamp, ent._.normal_form, ent._.event.
    Parameters
    ----------
    download : bool, (default=True)
        Flag, which allows to download Stanza and DeepPavlov model.
    normalize : bool, (default=True)
        Flag, which allows to normalize time expressions.
    event : bool, (default=True)
        Flag, which allows to parse events for time expressions.
    log : bool, (default=False)
        Flag, which allows logging.

    Examples
    --------
    >>> from TimeExpessions.TimeProcessor import TimeProcessor
    >>> time_processor = TimeProcessor()
    >>> doc = time_processor.process(['Около трех лет назад у пациента синусовый ритм был восстановлен ЭИТ.'],
    ...            date = ['2010-12-22 18:13:14'],
    ...            birthday = ['1981-06-25 18:11:43'])
    >>> ([(ent.text, ent._.timestamp, ent._.normal_form, ent._.event) for ent in doc[0].ents])

    [('Около трех лет назад',
      1,
      datetime.date(2007, 12, 22),
      'восстановлен синусовый ритм')]
    """

    def __init__(self, download=True, normalize=True, event=True, log=False):

        if not log:
            warnings.filterwarnings("ignore")
            warnings.filterwarnings(action="ignore", module="tensorflow")
            tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
            tf.autograph.set_verbosity(0)
            logging.disable(logging.WARNING)
            os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

        if download:
            stanza.download('ru')

        self.snlp = stanza.Pipeline(lang="ru", processors='tokenize')
        self.nlp = StanzaLanguage(self.snlp)
        self.ruler = EntityRuler(self.nlp)
        self.ruler.add_patterns(patterns)
        self.nlp.add_pipe(self.ruler)

        self.Span = Span
        self.Span.set_extension("timestamp", getter=self.get_timestamp, force=True)
        if normalize:
            self.Span.set_extension("normal_form", getter=self.get_normal_form, force=True)
        if event:
            self.Span.set_extension("event", getter=self.get_event, force=True)

        self.model = build_model("ru_syntagrus_joint_parsing", download=download)
        print('Initialization complete!')

    def doc_from_conllu(self, vocab, lines):
        """
        Convert conllu string to spacy doc
        With release of Spacy 3.0 this function can be replaced by build-in method.
        Parameters
        ----------
        vocab : Spacy vocab
            Spacy model vocabulary.
        lines : list
            Sentence in CONLL-U.
            
        Returns
        -------
        result : Spacy doc
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

    def get_timestamp(self, span):
        """
            Get stamp of time expressions.
            The fucntion checks rules, which found time expression and return time stamp.
            Parameters
            ----------
            span : Spacy Span
                Time expression.
            Returns
            -------
            stamp : int
                Stamp of time expression:
                1 - once-time
                2 - continious
                3 - repeatable
                4 - relative
        """
        if span.ent_id_ in ["rule_yearfull", 'rule_in_part_yearfull_part_yearfull', 'rule_yearfull_g_prep_time', 'rule_day_month', 'rule_part_month',
                            'rule_around_int_unit_ago', 'rule_int_unit_ago', 'rule_around_int_unit_ago', 'rule_int_unit_daytime', 'rule_int_daytime_date',
                            'rule_date_prep_time', 'rule_num_num_year', 'rule_date_year', 'rule_time_year', 'rule_time_unit', 'rule_event_in_time',
                            'rule_time_hour_date', 'rule_int_dash_int_hour_date', 'rule_in_month_yearfull', 'rule_time_daytime_date', 'rule_daytime_date',
                            'rule_date_daytime', 'rule_daytime_date', 'rule_int_dash_int_hour', 'rule_date', 'rule_around_time', 'rule_time', 'rule_around_int_h_unit_ago',
                            'rule_around_int_unit_ago', 'rule_around_numr_unit_ago', 'rule_int_and_int_unit', 'rule_num_yearfull', 'rule_event_daytime',
                            'rule_events', 'rule_in_age_int_unit', 'rule_unit_int_ago', 'rule_numr_unit_ago', 'rule_unit_ago', 'rule_day_before', 'rule_in_month_dash_month_yearfull_unit']:
                return 1
        if span.ent_id_ in ["rule_in_part_yearfull_part_yearfull", 'rule_from_yearfull_unit_till_yearfull_unit', 'rule_from_yearfull_unit_till_yearfull_unit', 
                            'rule_from_time_till_date', 'rule_yearfull_yearfull_unit', 'rule_last_int_dash_int_unit',
                            'rule_last_unit', 'rule_from_int_h_unit', 'rule_prep_part_int_dash_h', 'rule_from_int_dash_ti_unit', 'rule_prep_time_dash_time',
                            'rule_prep_time_dash_date', 'rule_around_int_unit', 'rule_around_numr_unit', 'rule_more_int_unit', 'rule_dur_last_int_com_unit',
                            'rule_in_last_numr_unit', 'rule_dur_last_unit', 'rule_dur_int_last_unit', 'rule_dur_int_h_unit', 'rule_dur_last_int_h_unit',
                            'rule_dur_last_adj_unit', 'rule_dur_int_dash_int_unit', 'rule_dur_int_unit', 'rule_dur_numr_unit', 'rule_dur_many_unit',
                            'rule_dur_unit', 'rule_last_int_unit', 'rule_numr_unit', 'rule_int_month', 'rule_month', 'rule_per_day',
                            'rule_now', 'rule_before_today', 'rule_dur_last_numr_com_unit']:
                return 2
        if span.ent_id_ in ["rule_prep_int_times_in_int_dash_int_unit", 'rule_int_dash_int_times_in_unit', 'rule_int_times_in_int_unit', 'rule_sev_times_in_unit',
                            'rule_regular']:
                return 3
        if span.ent_id_ in ["rule_thr_int_dash_int_unit", 'rule_aft_half_unit', 'rule_aft_unit', 'rule_thr_num_unit', 'rule_thr_int_unit', 'rule_aft_int_unit',
                            'rule_this_year']:
                return 4
        if span.ent_id_.startswith('rule_prep'):
            if span[0].text.lower() in ['с', 'до']:
                return 2
            else:
                return 1

    def pre_process_expr(self, span):
        """
        Preprocess time expressions for parsers.
        Parameters
        ----------
        span : Space Span
            Time expression.
        Returns
        -------
        processed_expr : str
            Lemma of time expression without preps and verbs.
            For words such 'утро','вечер','ночь', 'лет' save the case.
            Remove stop words such 'год', 'месяц', 'день'.
        """
        processed_expr = list()
        for word in span:
            if (
                (word.pos_ not in ["PREP", "ADP", "VERB"])
                and (word.lemma_.strip() not in ["год", "месяц", "день", 'около', 'течение', 'более', 'Более'])
                and (str(word) not in ["-", "ти", "х"])
            ):
                if word.lemma_.strip() in ["утро", "вечер", "ночь"]:
                    processed_expr.append(str(word))
                else:
                    processed_expr.append(word.lemma_.strip())
            if str(word) == "лет":
                processed_expr.append(str(word))

        return processed_expr

    def get_normal_form(self, span):
        """
        Normalize time expressions.
        The function uses dateparser and rutimeparser packages for normalizing the most common time expressions.
        For particullar time expression it checks rules, which found expression
        and uses special preprocessing for dateparser and rutimeparser packages
        or apply its own method of normalization.
        Parameters
        ----------
        span : Spacy Span
            Time expression.
        Returns
        -------
        normal_form : datetime
            Normal form of time expression.
        """
        now = datetime.strptime('1990-01-01', "%Y-%m-%d")
        processed_expr_span = self.pre_process_expr(span)
        processed_expr = " ".join(processed_expr_span)
        lemma_span = [w.lemma_ for w in span]
        lemma = ' '.join(lemma_span)
        normal_form = list()

        if span.ent_id_ in ["rule_prep_int_times_in_int_dash_int_unit", 'rule_int_dash_int_times_in_unit', 'rule_int_times_in_int_unit', 'rule_sev_times_in_unit',
                            'rule_regular', "rule_thr_int_dash_int_unit", 'rule_aft_half_unit', 'rule_aft_unit', 'rule_thr_num_unit', 'rule_thr_int_unit', 
                            'rule_aft_int_unit','rule_this_year']:
            return None

        elif span.ent_id_ in ['rule_around_int_unit_ago', 'rule_around_numr_unit_ago']:
            normal_form = rutimeparser.parse(processed_expr, now=self.date)

        elif span.ent_id_ in ['rule_int_unit_ago', 'rule_numr_unit_ago']:
            try:
                normal_form = rutimeparser.parse(lemma, now=self.date)
            except ValueError:
                normal_form = dateparser.parse(lemma, settings={"RELATIVE_BASE": self.date})

        elif span.ent_id_ in ["rule_dur_int_unit", 'rule_dur_numr_unit', 'rule_around_int_unit']:
            expression = " ".join(span.text.split()[-2:]) + " назад"
            expression = expression.replace(' г ', ' год ')
            try:
                normal_form.append(rutimeparser.parse(expression, now=self.date))
            except ValueError:
                normal_form.append(
                    dateparser.parse(expression, settings={"RELATIVE_BASE": self.date})
                )
            normal_form.append(self.date)

        elif span.ent_id_ in [
                "rule_dur_last_int_h_unit",
                "rule_more_int_unit",
                "rule_dur_int_h_unit",
                "rule_dur_last_int_unit",
                "rule_dur_int_last_unit",
                'rule_dur_last_int_com_unit',
                'rule_dur_last_adj_unit',
                'rule_more_int_unit'
            ]:
                digit = int(re.findall(r'\d+', lemma)[0])
                expression = str(digit) + " " + lemma_span[-1] + " назад"
                normal_form.append(
                    dateparser.parse(expression, settings={"RELATIVE_BASE": self.date})
                )
                normal_form.append(self.date)

        elif span.ent_id_ in ['rule_dur_last_numr_com_unit', 'rule_last_int_unit']:
            expression = " ".join(lemma_span[-2:]) + " назад"
            try:
                normal_form.append(rutimeparser.parse(expression, now=self.date))
            except ValueError:
                normal_form.append(
                    dateparser.parse(expression, settings={"RELATIVE_BASE": self.date})
                )
            normal_form.append(self.date)

        elif span.ent_id_ in ['rule_prep_season_yearfull', 'rule_prep_part_yearfull']:
            try:
                normal_form = datetime.strptime(interpret_dict[processed_expr_span[-2]] + processed_expr_span[-1], "%d.%m.%Y")
            except (KeyError, ValueError):
                pass

        elif span.ent_id_ in ['rule_prep_numr_unit', 'rule_prep_int_unit']:
            if lemma_span[0] in ['через', 'несколько', 'спустя', 'черза']:
                return None

            try:
                years = int(re.findall(r'\d+', lemma)[0])
                if lemma_span[-1] in ["год", "лет"] and self.birthday and years < 1900:
                    normal_form = self.birthday + relativedelta(years=years)
            except IndexError:
                pass

        elif span.ent_id_ == "rule_prep_month":
            normal_form = datetime.strptime(interpret_dict[processed_expr_span[0]] + str(self.date)[:4], "%m.%Y")

        elif span.ent_id_ in "rule_events":
            normal_form = dateparser.parse(
                processed_expr,
                settings={"PREFER_DAY_OF_MONTH": "first", "RELATIVE_BASE": self.date},
            )

        elif span.ent_id_ == "rule_unit_ago": 
            lemma = lemma.lower().replace('около', '')
            normal_form = rutimeparser.parse(lemma, now=self.date)

        elif span.ent_id_ in ["rule_dur_last_unit", "rule_last_unit"]: 
            expression = lemma_span[-1] + " назад"
            try:
                normal_form.append(rutimeparser.parse(expression, now=self.date))
            except ValueError:
                normal_form.append(dateparser.parse(expression, settings={"RELATIVE_BASE": self.date}))
            normal_form.append(self.date)

        if not normal_form: 
            normal_form = dateparser.parse(
                processed_expr,
                settings={"PREFER_DAY_OF_MONTH": "first", "RELATIVE_BASE": now},
            )

        if not normal_form:
            normal_form = search_dates(
                processed_expr,
                settings={"PREFER_DAY_OF_MONTH": "first", "RELATIVE_BASE": now},
            )
            if normal_form:
                for i in range(len(normal_form)):
                    normal_form[i] = normal_form[i][1]

        if not normal_form:
            try:
                normal_form = rutimeparser.parse(processed_expr, now=now)
            except ValueError:
                pass

        if isinstance(normal_form, datetime):
            normal_form = normal_form.date()
        elif isinstance(normal_form, list) and len(normal_form) == 1:
            normal_form = normal_form[0].date()
        return normal_form

    def find_event(self, doc, expr, exprs):
        """
        Find event for particular time expression.
        Parameters
        ----------
        doc : Spacy doc
            Parsed sentence.
        expr : Spacy span
            Time expression for which you want to find the event.
        exprs : tuple
            Tuple of time expresions.

        Returns
        -------
        event : list
            Time event.
        """
        root = [token for token in doc if token.head == token][0]
        event = list()
        time_root = expr.root

        # поиск придаточного предложения
        internal_sent = list()
        end = None
        if time_root.text != root.text:
            for child in root.children:
                if (
                    child.dep_ in ["conj", "parataxis", "acl:relcl", "advcl"]
                    and len(list(child.children)) > 0
                    and not list(child.children)[0].is_bracket
                ):
                    if not end:
                        end = list(child.subtree)[0].i
                    int_sent = Span(
                        doc, list(child.subtree)[0].i, list(child.subtree)[-1].i + 1
                    )
                    internal_sent.append(int_sent)
                    if (
                        expr.text in int_sent.text
                        and expr.text != int_sent.text
                        and int_sent.text != time_root.text
                        and doc.text[:-1] != int_sent.text
                    ):
                        return self.find_event(int_sent.as_doc(), expr, exprs)

        if end:
            if expr.text in Span(doc, 0, end).text:
                doc = Span(doc, 0, end).as_doc()
        elif doc[-1].pos_ == "PUNCT":
            doc = Span(doc, 0, len(doc) - 1).as_doc()
        root = [w for w in doc if w.head == w][0]
        try:
            all_expr = [w for ent in doc.ents for w in list(ent)]
        except ValueError:
            all_expr = expr
        time_root = expr.root

        if len(list(root.children)) == 1:
            child = list(root.children)[0]
            if not any(child.text == word.text for word in all_expr):
                root = child

        # Извлечение события, если оно внутри дерева образованного ВК
        if time_root and time_root.text != root.text:
            for w in time_root.subtree:
                if (
                    not any(w.text == word.text for word in all_expr)
                    and (w.tag_ not in ["CCONJ", "SCONJ", "PUNCT", "ADP", "PART"])
                    and (w.pos_ not in ["ADV"])
                    and (w.lemma_ not in ["год", "."])
                ):
                    event.append(w)

        if event:
            return event

        # если в предложении мало ветвей
        if len([i for i in root.children]) <= 2:
            for w in root.subtree:
                if (
                    not any(w.text == word.text for word in all_expr)
                    and (w.tag_ not in ["SCONJ", "PUNCT", "ADV"])
                    and (w.lemma_ not in ["год", "от"])
                ):
                    event.append(w)
            if event:
                return event

        # поиск необходимых типов связей
        if root.pos_ == "VERB":
            for child in root.children:
                if child.dep_ == "xcomp":
                    new_root = child
                    event.append(root)
                    for w in new_root.subtree:
                        event.append(w)

        cut = False
        for child in root.children:
            if child.dep_ in ["nsubj:pass", "nsubj"] and not event and child.text != expr.text:
                new_root = child
                if len(list(new_root.children)) > 1 and len(list(new_root.subtree)) > 8:
                    doc = Span(
                        doc, list(new_root.subtree)[0].i, list(new_root.subtree)[-1].i + 1
                    ).as_doc()
                    root = [w for w in doc if w.head == w][0]
                    cut = True
                    break
                if len(list(new_root.subtree)) == 1 and root.pos_ == "VERB":
                    if list(new_root.subtree)[0].lemma_ not in ["пациент", "пациентка"]:
                        event.append(root)
                        event.append(new_root)
                if len(list(new_root.subtree)) > 1:
                    if root.pos_ != "NOUN" and root.lemma_ != "принимать":
                        event.append(root)
                    for w in new_root.subtree:
                        if not any(w.text == word.text for word in all_expr):
                            event.append(w)
                    break

        if event:
            if len(event) == 1 and event[0].text == root.text:
                event = []
            else:
                return event

        # если в предложении много неглубоких ветвей
        words = list()
        for w in root.subtree:
            if (
                not any(w.text == word.text for word in all_expr)
                and (w.pos_ != "PUNCT")
                and (w.text != "х")
            ):
                words.append(w)

        if words and len(words) <= 3:
            event.extend(words)
            return event

        # если ВК внутри сложной конструкции, то разбиваем на конрукции попроще
        try:
            if (
                time_root
                and time_root.head.text != root.text
                and len(list(time_root.head.children)) > 1
                and not cut
            ):
                for w in doc:
                    if w.text == time_root.text:
                        time_root = w
                new_root = list(time_root.head.subtree)
                internal_sent = Span(doc, new_root[0].i, new_root[-1].i)
                return self.find_event(internal_sent.as_doc(), expr, exprs)
        except (IndexError, ZeroDivisionError):
            pass

        # все остальные случаи
        if not any(root.text == w.text for w in expr):
            event.append(root)

        new_root = None
        if root.n_rights:
            if not any(list(root.rights)[0].text == w.text for w in all_expr):
                new_root = list(root.rights)[0]

        if (root.n_lefts) and (not new_root):
            if not any(list(root.lefts)[0].text == w.text for w in all_expr):
                new_root = list(root.lefts)[0]

        if new_root:
            for w in list(new_root.subtree)[:5]:
                if (
                    not any(w.text == word.text for word in all_expr)
                    and (w.tag_ not in ["SCONJ", "PUNCT"])
                    and (w.lemma_ != "год")
                ):
                    event.append(w)

        return event


    def post_proccess(self, event):
        """
        Post process time events. 
        Remove punctiation, second parts of sentences, particullar preps and conjunctions.
        Parameters
        ----------
        span : Spacy Span
            Parsed sentence.

        Returns
        -------
        event : list
            Processed event.
        """
        while event[0].pos_ in ["CCONJ", "PUNCT", "PRON"] or event[0].lemma_ in ["по", "от", "после", "около"]:
            event = event[1:]
            if not event:
                break

        while (event) and (
            event[-1].pos_ in ["CCONJ", "PUNCT", "ADP"]
            or event[-1].lemma_ in ["где", "когда", "диагноз"]
            or event[-1].dep_ in ["conj", "parataxis", "acl:relcl", "advcl"]
        ):
            event = event[:-1]

        for word in event:
            if word.dep_ in ["conj", "parataxis", "acl:relcl", "advcl"]:
                if len(event) > len(list(word.subtree)):
                    [event.remove(w) for w in word.subtree if w in event]

        return event


    def get_event(self, span):
        """
        Extract event from spacy doc.
        Parameters
        ----------
        span : Spacy Span
            Parsed sentence.

        Returns
        -------
        result : list
            List of time events.
        """
        doc = span.doc
        exprs = doc.ents
        event = self.find_event(doc, span, exprs)
        if event:
            event = self.post_proccess(event)
        return " ".join([w.text for w in event])

    def dashrepl(self, matchobj):
        """
        Add spaces to dashes.
        Parameters
        ----------
        matchobj : re matchobj
            Pattern match.

        Returns
        -------
        sentence : str
            Processed sentence.
        """
        if "-" in matchobj.group(0):
            return matchobj.group(0).replace("-", " - ")
        else:
            return matchobj.group(0).replace("–", " – ")

    def pre_process_sentence(self, sentence):
        """
        Preprocess sentence.
        Add dots in the end. Add spaces to dashes.
        Parameters
        ----------
        sentence : str
            Original sentence.

        Returns
        -------
        sentence : str
            Processed sentence.
        """
        if sentence[-1] != ".":
            sentence = sentence + "."
        sentence = re.sub(r"[А-Яа-я][-–][А-Яа-я]", self.dashrepl, sentence)
        # devide '1998г' into two tokens  '1998' and 'г'
        sentence = re.sub(r"\dг", lambda x: x.group(0).replace("г", " г"), sentence)
        return sentence

    def process(self, sentence, date=None, birthday=None):
        """
        Process time expressions.
        Parameters
        ----------
        sentences : list, str
            List of sentences or sentence.
        date : list, str, datetime (default=None)
            List of dates of observation or date in string or datetime format.
        birth_date : list, str, datetime (default=None)
            List of birth dates or date in string or datetime format.
        Returns
        -------
        result : list
            List of parsed docs with time expressions, normal forms and stamps.
        """
        docs = list()
        parsed_sentences = list()

        if date is None:
            self.dates = datetime.now()
            self.dates = str(self.dates.strftime("%Y-%m-%d %H:%M:%S"))
            self.dates = [self.dates] * len(sentence)
        else:
            self.dates = date

        if birthday is None:
            self.birthdays = [None] * len(sentence)
        else:
            self.birthdays = birthday

        if isinstance(sentence, str):
            sentence = [sentence]
            date = [date]
            birthday = [birthday]

        for sent in range(len(sentence)):
            if len(sentence[sent]) == 0:
                sentence[sent] = '.'
                continue
            sentence[sent] = self.pre_process_sentence(sentence[sent])

        # Syntax parsing. It is best to parse in batches of 3-10 sentences. 
        # Otherwise, there may not be enough GPU memory or the parsing speed will be very slow.
        for i in range(0, len(sentence), 3):
            for parse in self.model(sentence[i:i + 3]):
                parsed_sentences.append(parse)

        for sent in range(len(sentence)):
            if len(sentence[sent]) == 0:
                continue
            if isinstance(date[sent], str):
                self.date = datetime.strptime(date[sent], "%Y-%m-%d %H:%M:%S")
            elif isinstance(date[sent], datetime):
                self.date = date[sent]
            elif isinstance(date[sent], type(None)):
                self.date = datetime.now()
            else:
                raise TypeError("date must be str, datetime or Nonetype")

            if isinstance(birthday[sent], str):
                self.birthday = datetime.strptime(birthday[sent], "%Y-%m-%d")
            elif isinstance(birthday[sent], datetime):
                self.birthday = birthday[sent]
            elif isinstance(birthday[sent], type(None)):
                self.birthday = None
            else:
                raise TypeError("birthday must be str, datetime or Nonetype")

            self.doc = self.doc_from_conllu(self.nlp.vocab, parsed_sentences[sent].split("\n"))
            self.ruler(self.doc)
            docs.append(self.doc)
        return docs
