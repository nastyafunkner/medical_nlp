import re

from abbreviation.abbreviation_predictor import AbbreviationPredictor


class AbbreviationExtractor:
    def __init__(self, base_corpus=None, abbr_predictor=None):
        self._base_corpus = base_corpus
        self._abbreviations = None

        if abbr_predictor:
            assert isinstance(abbr_predictor, AbbreviationPredictor)

        self._abbr_predictor = abbr_predictor

        self._init_abbreviations()

    def _init_abbreviations(self):
        if self.has_base_corpus:
            self._abbreviations = self._naive_extract_abbreviation(
                " ".join(self._base_corpus)
            )

    def upload_abbreviations(self, abbr_set):
        self._abbreviations = abbr_set

    def update_abbreviations(self, abbr_set):
        self._abbreviations += abbr_set

    @property
    def has_base_corpus(self):
        return hasattr(self, "_base_corpus") and not self._base_corpus is None

    def is_abbreviation(self, word):
        """
        Будем считать аббревиатурами слова, половина букв которого - заглавные
        Уберем случаи, когда слово может быть инициалом сотрудника
        """

        # убрать инициалы
        if re.fullmatch(r'[A-ZА-Я]\.[A-ZА-Я]\.?', word):
            return False

        upper_count = sum([l.isupper() for l in word])

        return upper_count > len(word) // 2 and len(word) > 1

    def _clean_abbr(self, word):
        """
        Убираем все символы кроме буквенных, а также точки и тире в начале и в конце
        """

        word = re.sub(r'[^A-ZА-Яа-я-a-z-\.]', '', word)

        while word[-1] in ['-', '.']:
            word = word[:-1]

        while word[0] in ['-', '.']:
            word = word[1:]

        return word.upper()

    def _naive_extract_abbreviation(self, text):
        """
        Достаем из текста слова, которые соответствуют функции is_abbreviation
        """

        text = text.replace(',', ' ')
        abbrs = filter(lambda word: self.is_abbreviation(word), text.split())
        abbrs = map(self._clean_abbr, abbrs)

        return list(abbrs)

    def _split_abbreviations(self, abbr, abbr_set):
        """
        Разделить самодостаточные аббревиатуры по знакам препинания
        """
        # Если без знаков препинания является аббревиатурой
        # ЭХО-КГ -> ЭХОКГ
        if re.sub(r'[\.|-]', '', abbr) in abbr_set:
            return [re.sub(r'[\.|-]', '', abbr)]

        # Если нет, то попытаемся достать новые аббревиатуры
        items = re.split(r'[-\.]', abbr)

        new_abbrs = []
        found = False

        # TODO: ФЦИН.был -> [ФЦИН]

        for item in items:
            if item in abbr_set:
                new_abbrs.append(item)

        if len(new_abbrs) > 0:
            return new_abbrs

        return [abbr]

    def extract_abbreviations(self, text, filter_abbr=False):
        """

        """
        abbreviations = self._naive_extract_abbreviation(text)
        abbr_set = self._abbreviations or set(abbreviations)

        items = []

        for abbr in abbreviations:
            splitted_abbrs = self._split_abbreviations(abbr, abbr_set)
            items.extend(splitted_abbrs)

        if filter_abbr:
            items = self.filter_abbreviations(items)

        return items

    def filter_abbreviations(self, abbreviations):
        if self._abbr_predictor:
            return list(filter(self._abbr_predictor.predict, abbreviations))
        else:
            raise ValueError('Предиктор не задан')

