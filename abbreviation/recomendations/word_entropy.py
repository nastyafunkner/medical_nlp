import math


class WordEntropyCounter:
    def __init__(self, letter_freq_dict):
        self.letter_freq_dict = letter_freq_dict

    def _entropy(self, p):
        return -p * math.log(p)

    def word_entropy(self, word):
        entr = 0

        for i in range(1, len(word)):
            entr += self._entropy(self.letter_freq_dict[word[i]][word[i - 1]])

        mean_entr = entr / (len(word) - 1)

        return (entr + mean_entr) / 2

    def to_file(self, path):
        with open(path, 'w') as f:
            f.write(str(self.letter_freq_dict))

    def from_file(path):
        with open(path, 'r') as f:
            letter_freq_dict = eval(f.read())

        return WordEntropyCounter(letter_freq_dict)