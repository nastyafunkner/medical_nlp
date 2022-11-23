import pandas as pd
import nltk
import re
import pymorphy2

from Data_preprocess import process_regex
from Data_preprocess import lemmatize
from abbreviation.abbreviation_extractor import AbbreviationExtractor
from abbreviation.abbreviation_predictor import EntropyVoter, DictVoter
from abbreviation.recomendations.word_entropy import WordEntropyCounter
from abbreviation.abbreviation_predictor import VotingAbbreviationClassifier

words = open('abbreviation/recomendations/russian_words.txt').read().split()
dv = DictVoter(set(words))
wec = WordEntropyCounter.from_file('abbreviation/recomendations/war_and_piece.wec')
ev = EntropyVoter(wec=wec, limit=0.77)
ev2 = EntropyVoter(wec, limit=0.2)

voter = VotingAbbreviationClassifier()
voter.add_voter('entropy_voter1', ev)
voter.add_voter('dict_voter', dv)
voter.add_voter('entropy_voter2', ev2)


with open('data/all_anamnesises.txt') as f:
    anamnesises = f.read().split('\n\t')

abbr_extractor = AbbreviationExtractor(anamnesises, voter)

nltk.download("stopwords")
stopwords = nltk.corpus.stopwords.words('russian')
morph = pymorphy2.MorphAnalyzer()
cyrillic = re.compile(r'[^а-я ]')
mult_ws = re.compile(r'\s+')
fix_punct = re.compile(r'\s+(\?|\.|,|!|:)')

data = pd.read_csv('data/cardio_anamnesis_all_0_1000.csv', sep = '\t')
abbr_terms = pd.read_csv('data/abbr_term.csv', sep = '\t', encoding='utf-8')

# Удаляем повторяющиеся строки 1
# new_data = data.drop_duplicates(subset = ['Наименование работ', '№ \nп/п'], keep='first')
# Удаляем повторяющиеся строки и nan
new_data = data.dropna(axis='index', how='any', subset=['anamnesis'])
new_data = new_data.drop_duplicates(subset = ['anamnesis'], keep='first')
new_data = new_data.loc[new_data['anamnesis'].str.match('[^\W\d]')] # Непонятно надо ли это использовать

anamnesis = new_data['anamnesis'].tolist()
abrr_from_works = []
except_list = []
all_sents = [] # Список всех предложений, чтобы не повторять обработку

for i, anamn in enumerate(anamnesis):
    print(i, 'from:', len(anamnesis))
    # TODO тут сомнительная предобработка, надо подумать надо ли ее поменять
    try:
        sents = re.split('(?<!\w\.\w.)(?<![AZ][az]\.)(?<=\.|\?)\s', anamn)
    except:  # все тут должно быть нормально
        sents = []
        print('разделение')
        print(anamn)
    for sent in sents:
        if sent not in all_sents:  # Если предложения нету в общем списке, добавляем в список
            all_sents.append(sent)
            proc_sent = process_regex(cyrillic, mult_ws, text=sent)
            proc_sent_tokens = lemmatize(proc_sent, morph, stopwords, min_word_size=2)
            for i, token in enumerate(proc_sent_tokens):
                if voter.predict(token):
                    try:
                        data_term = abbr_terms.loc[abbr_terms['abbreviation'] == token.upper()]
                        data_term = data_term['term'].to_list()[0]  # Пока берем только первое включение
                        abrr_from_works.append({'abbr': token, 'dec': data_term, 'anamnesis': sent})
                    except:
                        abrr_from_works.append({'abbr': token, 'dec': '-', 'anamnesis': sent})
data = pd.DataFrame(abrr_from_works)
new_data = data.drop_duplicates(subset = ['abbr'], keep='first')
new_data.to_csv('data/abrr_from_anamnesis.csv', sep='\t', index=False)