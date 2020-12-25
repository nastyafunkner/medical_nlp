from spacy.pipeline import EntityRuler
from spacy.tokens import Doc, Span
from spacy.vocab import Vocab
from spacy.language import Language
import pandas as pd

from negations.neg_patterns import patterns_part, patterns

import sys
sys.path.append("..")
from utils import doc_from_conllu

negations = ['не', 'нет', 'отрицать', 'отсутствовать', 'без', 'избегать', 'отказаться']
conj = ["conj", "parataxis", "acl:relcl", "advcl"]

class Negator:
    """
    This class includes methods for searching negations in sentences.
    It includes methods of splitting complex sentences.
    Results are available through attributes  ent._.neg_expr, ent._.neg_ent.

    Examples
    --------
    >>> from syntax.parser import Parser
    >>> from negations import negations
    >>> negator = negations.Negator()
    >>> parser = Parser()
    >>> doc = negator.process(sentence=['Около трех лет назад у пациента синусовый ритм был восстановлен ЭИТ.'],
    ...            parser = parser)
    >>> ([(ent._.neg_expr, ent._.neg_ent) for ent in doc[0].ents])

    [('Около трех лет назад',
      1,
      datetime.date(2007, 12, 22),
      'восстановлен синусовый ритм')]
    """

    def __init__(self):

        self.nlp = Language(Vocab())
        self.ruler = EntityRuler(self.nlp)
        self.ruler.add_patterns(patterns_part)
        self.ruler.add_patterns(patterns)
        self.nlp.add_pipe(self.ruler)

        self.Span = Span
        self.Doc = Doc

        self.Span.set_extension("neg_expr", getter=self.get_negated_expressions, force=True)
        self.Span.set_extension("neg_ent", getter=self.get_negated_ent, force=True)

    def get_negated_expressions(self, span):
        """
        Extract negated expressions from spacy doc.
        Parameters
        ----------
        span : Spacy Span
            Parsed sentence.

        Returns
        -------
        result : list
            list of negated entities.
        """
        doc = span.doc
        if span.label_ == "NEG_PART":
            neg_expr = self.find_negated_expressions(doc, span[0])
            return neg_expr
        return span

    def get_negated_ent(self, span):
        """
        Extract negated entity from spacy doc.
        Parameters
        ----------
        span : Spacy Span
            Parsed sentence.

        Returns
        -------
        result : list
            list of negated entities.
        """
        ent = span._.neg_expr
        result = []
        for word in ent:
            if word.lemma_ not in negations and word.tag_ != 'VERB':
                result.append(word)

        return result

    def split_sentence(self, word, sent, negation):
        """
        Split complex sentence into simple sentences and return part,
        where current word is located
        Parameters
        ----------
        word : Spacy.token
            current word
        sent : Spacy.doc
            parsed sentence
        negation : Spacy.token
            current negation part

        Returns
        -------
        word : Spacy.token
            current word in new sentence
        sent : Spacy.doc
            new simple sentence
        negation : Spacy.token
            current negation part in new sentence
        """
        internal_sent = list(word.subtree)
        if internal_sent[0].dep_ == 'punct':
            internal_sent.remove(internal_sent[0])
        index_list = [w.i for w in internal_sent]
        min_i = min(index_list)
        max_i = max(index_list)
        new_sent = Span(sent, min_i, max_i+1).as_doc()
        head = [w for w in new_sent if w.text == word.text][0]
        negation = [w for w in new_sent if w.text == negation.text][0]

        return new_sent, head, negation

    def find_negated_expressions(self, sent, negation):
        """
        Find negated_expression for particular negation part.
        Parameters
        ----------
        sent : Spacy doc
            Parsed sentence.
        negation : Spacy span
            negation part for which you want to find the expression.

        Returns
        -------
        result : list
            negated expression.
        """
        head = negation.head
        filter = lambda root, excp: [w for w in root.children if (w.dep_ != 'punct') and (w != excp)]

        if negation.lemma_ in ['отрицать', 'отказаться', 'нет']:
            for child in negation.children:
                if child.dep_ in ['nsubj', 'nsubj:pass', 'obj']:
                    return [negation] + list(child.subtree)
            for child in negation.children:
                if child.dep_ in ['obl']:
                    return [negation] + list(child.subtree)

        for child in head.children:
            if child.dep_ in ['nsubj', 'nsubj:pass', 'obj']:
                if 'conj' not in [w.dep_ for w in child.children]:
                    return [negation, head] + list(child.subtree)
                else:
                    return [negation, head, child]

        if head.dep_ in conj:
            sent, head, negation = self.split_sentence(head, sent, negation)
            head = [i for i in sent if i.text == head.text][0]

        for word in head.subtree:
            if word.dep_ in conj:
                indexes = [w.i for w in word.subtree]
                if max(indexes) < head.i:
                    sent = Span(sent, max(indexes)+1, len(sent)).as_doc()
                elif min(indexes) > head.i:
                    sent = Span(sent, 0, min(indexes)).as_doc()
                head = [w for w in sent if w.text == head.text][0]
                negation = [w for w in sent if w.text == negation.text][0]
                break

        if head.pos_ == 'NOUN':
            if len(list(head.children)) == 1:
                return [negation, head, head.head] + filter(head.head, head)
            for child in head.children:
                if child.dep_ in ['nsubj', 'nsubj:pass', 'obj']:
                    return [negation, head, child]

        if len(list(head.children)) < 3:
            return [w for w in head.subtree if w.dep_ not in ['conj', 'punct']]

        return [negation, head]

    def convert_to_dataframe(self, docs):
        """
        Present spacy docs in pandas dataframe format
        Parameters
        ----------
        docs : list
            list of parsed sentences

        Returns
        -------
        sentence : Pandas DataFrame
            Table of parsed sentences.
        """
        sentences, neg_expr, neg_ent = [], [], []

        for doc in docs:
            sentences.append(str(doc))

            neg_expr.append([' '.join([i.text for i in ent._.neg_expr if (i is not None) and (i.tag_ != 'PUNCT')]) for ent in doc.ents])
            neg_ent.append([' '.join([i.text for i in ent._.neg_ent]) for ent in doc.ents])

        for i in range(len(neg_ent)):
            for j in range(len(neg_ent[i])):
                if neg_ent[i][j] =='':
                    neg_ent[i][j] = ' None'
            neg_ent[i] = ', '.join(neg_ent[i])

        neg_expr = [', '.join(expr) for expr in neg_expr]

        df = pd.DataFrame({'sentence': sentences, 'neg_expr': neg_expr, 'neg_ent': neg_ent})

        return df

    def process(self, parsed_sentences=None, sentence=None, parser=None, to_dataframe=False):
        """
        Process time expressions.
        Parameters
        ----------
        sentence : list, str
            List of sentences or sentence, used if parsed_sentences is not None.
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

        if parsed_sentences == None:
            parsed_sentences = parser.parse(sentence)

        for sent in range(len(parsed_sentences)):
            if len(sentence[sent]) == 0:
                continue

            self.doc = doc_from_conllu(
                self.nlp.vocab, parsed_sentences[sent].split("\n"))
            self.ruler(self.doc)
            docs.append(self.doc)

        if to_dataframe == True:
            return self.convert_to_dataframe(docs)

        return docs