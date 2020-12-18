from datetime import datetime
from deeppavlov import build_model
from spacy.pipeline import EntityRuler
from spacy.tokens import Doc, Span
from spacy.vocab import Vocab
from spacy.language import Language

from TimeExpressions import time_patterns
import sys
sys.path.append("..")
from utils import doc_from_conllu, convert_to_dataframe


class TimeProcessor:
    """Processing time expression
    This class includes methods for parsing time expression data for future mining.
    It includes methods normalization of time expressions, getting stamps and finding events.
    Results are available through attributes ent.text (time expression), ent._.timestamp, ent._.normal_form, ent._.event.
    Parameters
    ----------
    normalize : bool, (default=True)
        Flag, which allows to normalize time expressions.
    event : bool, (default=True)
        Flag, which allows to parse events for time expressions.

    Examples
    --------
    >>> from TimeExpessions.TimeProcessor import TimeProcessor
    >>> ffrom syntax.parser import Parser
    >>> fparser = Parser()
    >>> time_processor = TimeProcessor()
    >>> doc = time_processor.process(sentence=['Около трех лет назад у пациента синусовый ритм был восстановлен ЭИТ.'],
    ...            date = ['2010-12-22 18:13:14'],
    ...            birthday = ['1981-06-25 18:11:43'],
    ...            parser = parser)
    >>> ([(ent.text, ent._.timestamp, ent._.normal_form, ent._.event) for ent in doc[0].ents])

    [('Около трех лет назад',
      1,
      datetime.date(2007, 12, 22),
      'восстановлен синусовый ритм')]
    """

    def __init__(self, normalize=True, event=True):

        self.nlp = Language(Vocab())
        self.ruler = EntityRuler(self.nlp)

        self.rules = time_patterns.rules
        pattern = []
        for rule in self.rules:
            pattern.append(
                {"label": 'EXPR', "pattern": self.rules[rule]['pattern'], "id": rule})
        self.ruler.add_patterns(pattern)
        self.nlp.add_pipe(self.ruler)

        self.Span = Span
        self.Doc = Doc
        self.Span.set_extension("timestamp", default=None, force=True)
        if normalize:
            self.Doc.set_extension("date", default=None, force=True)
            self.Doc.set_extension("birthday", default=None, force=True)
            self.Span.set_extension("normal_form", default=None, force=True)
            self.Span.set_extension("form", default=None, force=True)
            self.Span.set_extension("uncertain", default=None, force=True)
        if event:
            self.Span.set_extension("event", getter=self.get_event, force=True)

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
                        doc, list(child.subtree)[0].i, list(
                            child.subtree)[-1].i + 1
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
                        doc, list(new_root.subtree)[0].i, list(
                            new_root.subtree)[-1].i + 1
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

    def get_uncertain(self, ent):
        """
        get uncertain for event using rules from petterns file.
        Parameters
        ----------
        ent : Spacy Entity
            Time expression.
        """

        r_uncertain = self.rules[ent.ent_id_]['uncertain']
        r_form = self.rules[ent.ent_id_]['form']
        norm = ent._.normal_form
        if ent._.form in [[-1, 0, 1], [None], [-2, 0, 2]]:
            if callable(r_uncertain):
                ent._.uncertain = [norm + r_uncertain(ent) * i for i in r_form]
            else:
                ent._.uncertain = [norm + r_uncertain *
                                   i for i in r_form if i is not None]
        else:
            if callable(r_uncertain):
                if type(r_uncertain(ent)) is list:
                    ent._.uncertain = [
                        norm[0] - r_uncertain(ent)[0]] + norm + [norm[1] + r_uncertain(ent)[1]]
                else:
                    ent._.uncertain = [
                        norm[0] - r_uncertain(ent)] + norm + [norm[1] + r_uncertain(ent)]
            else:
                if type(r_uncertain) is list:
                    ent._.uncertain = [norm[0] - r_uncertain[0]
                                       ] + norm + [norm[1] + r_uncertain[1]]
                else:
                    ent._.uncertain = [norm[0] - r_uncertain] + \
                        norm + [norm[1] + r_uncertain]

    def process(self, parsed_sentences=None, sentence=None, parser=None, date=None, birthday=None, to_dataframe=False):
        """
        Process time expressions.
        Parameters
        ----------
        sentence : list, str
            List of sentences or sentence, used if parsed_sentences is not None.
        date : list, str, datetime (default=None)
            List of dates of observation or date in string or datetime format.
        birth_date : list, str, datetime (default=None)
            List of birth dates or date in string or datetime format.
        to_dataframe : bool (default=False)
            Flag, which allows to convert result to dataframe.
        parser : object (default=None)
            Syntax parser, used if parsed_sentences is not None.
        parsed_sentences : list (default=None)
            List of parsed senteces, if they are already parsed in conllu format.
        Returns
        -------
        result : list
            List of parsed docs with time expressions, normal forms and stamps.
        """
        docs = list()

        if isinstance(sentence, str):
            sentence = [sentence]
            date = [date]
            birthday = [birthday]

        if parsed_sentences == None:
            parsed_sentences = parser.parse(sentence)

        if date is None:
            self.dates = datetime.now()
            self.dates = str(self.dates.strftime("%Y-%m-%d %H:%M:%S"))
            self.dates = [self.dates] * len(parsed_sentences)
        else:
            self.dates = date

        if birthday is None:
            self.birthdays = [None] * len(parsed_sentences)
        else:
            self.birthdays = birthday

        for sent in range(len(parsed_sentences)):
            if len(parsed_sentences[sent]) == 0:
                continue
            if isinstance(date[sent], str):
                self.date = datetime.strptime(
                    date[sent][:-3], "%Y-%m-%d %H:%M")
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

            self.doc = doc_from_conllu(
                self.nlp.vocab, parsed_sentences[sent].split("\n"))
            self.doc._.date = self.date
            self.doc._.birthday = self.birthday
            self.ruler(self.doc)
            for ent in self.doc.ents:
                ent._.normal_form = self.rules[ent.ent_id_]['norm'](ent)
                ent._.form = self.rules[ent.ent_id_]['form']
                ent._.timestamp = self.rules[ent.ent_id_]['stamp']
                self.get_uncertain(ent)
            docs.append(self.doc)

        if to_dataframe == True:
            return convert_to_dataframe(docs)

        return docs
