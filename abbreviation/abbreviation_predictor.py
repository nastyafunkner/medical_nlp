import re
import warnings

from abbreviation.recomendations.word_entropy import WordEntropyCounter


class AbbreviationPredictor:
    def __init__(self):
        pass

    def predict(self, word):
        raise NotImplementedError

    def __repr__(self):
        return '{}()'.format(type(self).__name__)


class EntropyVoter(AbbreviationPredictor):
    def __init__(self, wec: WordEntropyCounter, limit):
        self._wec = wec
        self._limit = limit

    def predict(self, word):
        word = word.lower()
        word = re.sub('[^а-я]', '', word)
        word = ' ' + word.strip() + ' '

        try:
            entr = self._wec.word_entropy(word)
            return entr < self._limit
        except:
            return False


class DictVoter(AbbreviationPredictor):
    def __init__(self, set_of_word: set):
        if not isinstance(set_of_word, set):
            warnings.warn('лучше передать set для скорости работы', Warning)

        self._set_of_word = set_of_word

    def predict(self, word):
        return not word.lower() in self._set_of_word


class VotingAbbreviationClassifier(AbbreviationPredictor):
    def __init__(self):
        self.voters = {}

    def add_voter(self, name, voter):
        assert isinstance(voter, AbbreviationPredictor)

        self.voters[name] = voter

    def delete_voter(self, name):
        if name in self.voters:
            del self.voters[name]
        else:
            raise ValueError('Нет такого предиктора')

    def predict(self, word):
        count = 0

        for name, voter in self.voters.items():
            pred = voter.predict(word)

            count += pred

        return count > len(self.voters) // 2