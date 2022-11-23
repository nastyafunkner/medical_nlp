import re
import razdel
from typing import List

# Препроцессинг данных: удаление лишних символов
def process_regex(re_words_to_save, re_mult_ws, text: str) -> str:
    text = text.lower()
    text = re.sub(re_words_to_save, '', text)
    text = re.sub(re_mult_ws, ' ', text)
    text = text.strip()
    return text

# Выполняет лемматизацию элементов строки, возвращает строку с результатом
def lemmatize(text: str, lemmatizer, stopwords, min_word_size: int = 5) -> List[str]:
    words = [token.text for token in razdel.tokenize(text)]
    res = []
    for word in words:
        if word not in stopwords:# and len(word) > 1:
            p = lemmatizer.parse(word)[0]
            word_normal_form = p.normal_form
            if len(word_normal_form) < min_word_size:
                continue
            res.append(word_normal_form.replace('ё', 'е'))
    return res

# Осуществляет препроцессинг всех записей, также производится лемматизация по токенам
# TODO доработать для удобного использования
def process_data(data, lemmatizer, min_word_size=3, min_sent_size=1):
    proc_doc = []
    for sent in data:
        proc_sent = process_regex(
            cyrillic,
            mult_ws,
            text=sent
        )
        proc_sent_tokens = lemmatize(proc_sent, lemmatizer, min_word_size)
        # порог по длине предложения
        if len(proc_sent_tokens) < min_sent_size:
            continue
        proc_sent = ' '.join(proc_sent_tokens)
        proc_doc.append(proc_sent)
    return proc_doc