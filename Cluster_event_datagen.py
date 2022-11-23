import pandas as pd
import re

from syntax.parser import Parser
from TimeExpressions.TimeProcessor import TimeProcessor

parser = Parser()
processor = TimeProcessor()

df = pd.read_csv('data/cardio_anamnesis_all_300_400.csv', sep = '\t')

# Цикл для прохода по всем записям
counter = 0
counter_exc = 0
columns = ['id', 'date', 'sentence', 'time_expr', 'event']
data_for_analyse = []
time_exp_exc = []
for i, row in df.iterrows():
  sentence=row['anamnesis']
  print(i)
  try:
    sents = re.split('(?<!\w\.\w.)(?<![AZ][az]\.)(?<=\.|\?)\s', sentence)
  except:
    sents = []
    print(sentence)
  if len(sents) > 3:
    for sentence in sents:
      try:
        doc = processor.process(sentence=sentence, parser=parser, save=False)
        counter = 0
        for ent in doc[0].ents:
          data_for_analyse.append({'id':row['id'], 'date':row['date'], 'sentence': sentence, 'time_expr': ent.text, 'event': ent._.event, 'timestamp': ent._.timestamp})
          counter+=1
          print(counter)
      except:
        print('Не удалось выделить ВК') # Сохраняем ВК которые не удалось обработать
        time_exp_exc.append(sentence)
        continue
  else:
    try:
      doc = processor.process(sentence=sentence, parser=parser, save=False)
      counter = 0
      for ent in doc[0].ents:
        data_for_analyse.append({'id':row['id'], 'date':row['date'], 'sentence': sentence, 'time_expr': ent.text, 'event': ent._.event, 'timestamp': ent._.timestamp})
        counter+=1
        print(counter)
    except:
      print('Не удалось выделить ВК') # Сохраняем ВК которые не удалось обработать
      time_exp_exc.append(sentence)
      continue
data = pd.DataFrame(data_for_analyse)
time_except_df = pd.DataFrame(time_exp_exc)
data.to_csv('data/cardio_events_300_400.csv', sep='\t', index=False)
time_except_df.to_csv('data/time_except_300_400.csv', sep='\t', index=False)