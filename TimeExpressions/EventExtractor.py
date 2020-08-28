import re

import spacy
from spacy.tokens import Doc
import stanza
from spacy_stanza import StanzaLanguage
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span



class EventExtractor:
    """Extract time eents
    This class includes methods for extracting time events.
    Parameters
    ----------
    model : Spacy model, (default=None)
        Define which model will be used for converting to spacy doc.

    Examples
    --------
    >>> from TimeExpessions.EventExtractor import EventExtractor
    >>> event_extractor = EventExtractor()
    >>> event_extractor.extract(parsed_sentences, [['в течении 5 лет'], ['с 1993 года']])

    [['Болеет СД 2 типа'], ['перенесла гинекологическую операцию']]
    """

    def __init__(self, model=None):

        if model is None:
            snlp = stanza.Pipeline(lang="ru")
            self.nlp = StanzaLanguage(snlp)
        else:
            self.nlp = model
            
    def doc_from_conllu(self, vocab, lines):
        """
        Convert conllu string to spacy doc
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

    def pre_proccess(self, doc, exprs):
        """
        Preprocess time expressions.
        Parameters
        ----------
        doc : Spacy doc
            Parsed sentence.
        exprs : list
            List of time expresions.
            
        Returns
        -------
        result : list
            List of time expresions.
        """
        for i in range(len(exprs)):
            exprs[i] = exprs[i].replace(" - ", "-")
            exprs[i] = exprs[i].replace(" х ", "х ")

        for word in doc:
            if word.text == "г.":
                for i in range(len(exprs)):
                    if exprs[i] in (" ".join([w.text for w in word.subtree])[:-1]):
                        exprs[i] = " ".join([w.text for w in word.subtree])
                        break
                break
        return exprs


    def find_event(self, doc, expr, exprs):
        """
        Find event for particular time expression.
        Parameters
        ----------
        doc : Spacy doc
            Parsed sentence.
        expr : list
            Time expression for which you want to find the event.
        exprs : list
            List of time expresions.
            
        Returns
        -------
        result : list
            Time event.
        """
        all_expr = " ".join(exprs)
        complex_sent = 0
        root = [token for token in doc if token.head == token][0]
        time_root = None
        event = list()

        # поиск придаточного предложения
        internal_sent = Span(doc, 0, 0)
        for child in root.children:
            if (len(list(child.children)) > 0) and (child.text not in all_expr):
                start = next(child.children)
                if start.tag_ == "PUNCT" and start.i != 0:
                    complex_sent = 1
                    internal_sent = Span(doc, start.i, len(doc))
                    break

        if expr in internal_sent.text:
            return self.find_event(internal_sent.as_doc(), expr, exprs)

        # поиск корня ВК
        matcher = PhraseMatcher(self.nlp.vocab)
        patterns = [self.nlp(expr)]
        matcher.add("TIME_EXPRESSION", patterns)
        matches = matcher(doc)
        if matches:
            time_expr = Span(doc, matches[0][1], matches[0][2])
            time_root = time_expr.root
        else:
            match = re.search(expr, doc.text)
            if match:
                time_expr = doc.char_span(match.start(), match.end())
                time_root = time_expr.root

        # если ВК внутри сложной конструкции, то разбиваем на конрукции попроще
        if (
            time_root
            and len([i for i in root.children]) == 2
            and time_root != root
            and time_root.head != root
        ):
            child = list(root.children)[0]
            if len(list(child.children)) > 0:
                start = list(child.children)[0]
                internal_sent = Span(doc, start.i, len(doc))
                if internal_sent.as_doc().text != doc.text:
                    return self.find_event(internal_sent.as_doc(), expr, exprs)

        # Извлечение события, если оно внутри дерева образованного ВК
        if time_root and time_root != root:
            for w in time_root.subtree:
                if (
                    (w.text not in all_expr)
                    and (w.tag_ not in ["CCONJ", "SCONJ", "PUNCT", "ADP", "PART"])
                    and (w.pos_ not in ["ADV"])
                    and (w.lemma_ != "год")
                    and (w not in internal_sent)
                ):
                    event.append(w.text)

        if event:
            return " ".join(event)

        # если в предложении много неглубоких ветвей
        words = list()
        for w in root.subtree:
            if (
                (w.text not in all_expr)
                and (w.tag_ not in ["SCONJ", "PUNCT", "ADP"])
                and ((w not in internal_sent))
                and (w.lemma_ != "год")
            ):
                words.append(w.text)

        if words and len(words) <= 3:
            event.extend(words)
            return " ".join(event)

        # если в предложении мало ветвей
        if len([i for i in root.children]) <= 3 + complex_sent:
            stop_tokens = list()
            if (
                any([i in internal_sent.text for i in exprs])
                or len([i for i in root.children]) == 4
            ):
                stop_tokens = internal_sent
            for w in root.subtree:
                if (
                    (w.text not in all_expr)
                    and (w.tag_ not in ["SCONJ", "PUNCT"])
                    and ((w not in stop_tokens))
                    and (w.lemma_ != "год")
                ):
                    event.append(w.text)
            if event:
                return " ".join(event)

        # поиск необходимых типов связей
        for child in root.children:
            if child.dep_ in ["nsubj:pass", "nsubj"]:
                new_root = child
                if len(list(new_root.subtree)) > 1:
                    if len(list(new_root.subtree)) < 5:
                        event.append(root.text)
                    for w in new_root.subtree:
                        if len(list(new_root.subtree)) > 5:
                            if (w != new_root) and (w.dep_ in ["nsubj:pass", "nsubj"]):
                                event.append(w.text)
                                event.append(w.head.text)
                        else:
                            event.append(w.text)
                    break

        if event:
            return " ".join(event)

        # если ВК внутри сложной конструкции, то разбиваем на конрукции попроще
        if time_root and time_root.head != root and len(list(time_root.head.children)) > 1:
            new_root = list(time_root.head.subtree)
            internal_sent = Span(doc, new_root[0].i, new_root[-1].i)
            return self.find_event(internal_sent.as_doc(), expr, exprs)

        # все остальные случаи
        if root.text not in expr:
            event.append(root.text)

        new_root = None
        if root.n_rights:
            if list(root.rights)[0].text not in all_expr:
                new_root = list(root.rights)[0]

        if (root.n_lefts) and (not new_root):
            if list(root.lefts)[0].text not in all_expr:
                new_root = list(root.lefts)[0]

        if new_root:
            for w in list(new_root.subtree)[:5]:
                if (
                    (w.text not in all_expr)
                    and (w.tag_ not in ["SCONJ", "PUNCT"])
                    and (w.lemma_ != "год")
                ):
                    event.append(w.text)

        return " ".join(event)


    def get_event(self, doc, exprs):
        """
        Extract event from spacy doc.
        Parameters
        ----------
        doc : Spacy doc
            Parsed sentence.
        exprs : list
            List of time expresions.
            
        Returns
        -------
        result : list
            List of time events.
        """
        events = list()
        exprs = self.pre_proccess(doc, exprs)
        for expr in exprs:
            events.append(self.find_event(doc, expr, exprs))

        return events

    def extract(self, sentences_parsed, expressions):
        """
        Extract time event according to time expression.
        Parameters
        ----------
        sentences_parsed : list
            List of sentences in CONLL-U format.
        expressions : list
            List of time expressions.
            
        Returns
        -------
        result : list
            Time events.
        """
        
        EVENTS = list()
        for i in range(len(sentences_parsed)):
            doc = self.doc_from_conllu(self.nlp.vocab, sentences_parsed[i].split("\n"))
            exprs = expressions[i]
            EVENTS.append(self.get_event(doc, exprs))
            
        return EVENTS