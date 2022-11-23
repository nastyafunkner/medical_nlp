# use to find bigrams, which are pairs of words
from utils import pre_process_sentence
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.collocations import TrigramCollocationFinder
from nltk.metrics import TrigramAssocMeasures
import pandas as pd
import re
from nltk.corpus import stopwords

stopset = set(stopwords.words('russian'))
stopset.update(['мм', 'рт', 'ст', 'мг']) # Дополняем стопслова
filter_stops = lambda w: len(w) < 2 or w in stopset

all_data = pd.read_csv('data/cardio_anamnesis_all_0_1000.csv', sep = '\t')
all_data = all_data.dropna(axis='index', how='any', subset=['anamnesis'])
all_data = all_data.drop_duplicates(subset = ['anamnesis'], keep='first')

all_words = []
all_sents = []

# цикл по всем записям
for i, row in all_data.iterrows():
  record=row['anamnesis']
  print(i, '/', len(all_data))
  try:
    sents = re.split('(?<!\w\.\w.)(?<![AZ][az]\.)(?<=\.|\?)\s', record)
  except: # все тут должно быть нормально
    sents = []
    print('разделение')
    print(record)
  for sent in sents:
    sent = sent.lower()
    if sent not in all_sents: # Если предложения нету в общем списке, добавляем в список и делим на слова
      all_sents.append(sent)
      words = re.split('[\s+|\-|\.|,|:]', sent) # Разделяем слова на сонове пробелов, тире, точек и запятых
      iter_words = words.copy() # Клон для цикла
      for word in iter_words:
        if word == '' or word.isnumeric(): # Удаляем все пустые строки
          words.remove(word)
      all_words = all_words + words

biagram_collocation = BigramCollocationFinder.from_words(all_words)
biagram_collocation.apply_word_filter(filter_stops)
#nbest_bigr = biagram_collocation.nbest(BigramAssocMeasures.likelihood_ratio, 100)

trigram_collocation = TrigramCollocationFinder.from_words(all_words)
trigram_collocation.apply_word_filter(filter_stops)
trigram_collocation.apply_freq_filter(3)
#nbest_bigr = trigram_collocation.nbest(TrigramAssocMeasures.likelihood_ratio, 200)

frec_data = []
frec_ngrams = trigram_collocation.ngram_fd
keys = frec_ngrams.keys()
values = frec_ngrams.values()
for key, value in zip(keys, values):
  key = str.join(' ', list(key))
  frec_data.append({'collocation': key, 'score': value})

measure_data = []
score_fn = TrigramAssocMeasures.likelihood_ratio
score_ngrams = trigram_collocation.score_ngrams(score_fn)
for p, s in score_ngrams:
  p = str.join(' ', list(p))
  measure_data.append({'collocation': p, 'score': s})

frec_data = pd.DataFrame(frec_data)
measure_data = pd.DataFrame(measure_data)
frec_data.to_csv('data/Frec_trigram.csv', sep='\t', index=False)
measure_data.to_csv('data/Measure_trigram.csv', sep='\t', index=False)

frec_data = []
frec_ngrams = biagram_collocation.ngram_fd
keys = frec_ngrams.keys()
values = frec_ngrams.values()
for key, value in zip(keys, values):
  key = str.join(' ', list(key))
  frec_data.append({'collocation': key, 'score': value})

measure_data = []
score_fn = BigramAssocMeasures.likelihood_ratio
score_ngrams = biagram_collocation.score_ngrams(score_fn)
for p, s in score_ngrams:
  p = str.join(' ', list(p))
  measure_data.append({'collocation': p, 'score': s})

frec_data = pd.DataFrame(frec_data)
measure_data = pd.DataFrame(measure_data)
frec_data.to_csv('data/Frec_bigram.csv', sep='\t', index=False)
measure_data.to_csv('data/Measure_bigram.csv', sep='\t', index=False)