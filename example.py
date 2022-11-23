import pandas as pd

df = pd.read_csv('data/Old_data/train_time.csv')
df = df[:100]
print(df.head())

from syntax.parser import Parser

parser = Parser()

from TimeExpressions.TimeProcessor import TimeProcessor

processor = TimeProcessor()

doc = processor.process(sentence="Через 2 недели после выписки - декомпенсация СН до IV ФК, развите анасарки.", parser=parser, save=False)
print([('ВК: '+ent.text, 'Нормальная форма: '+str(ent._.normal_form), 'Событие: '+ent._.event_dep, 'Зависимое событие: '+ent._.event, 'тип_вк: '+str(ent._.timestamp)) for ent in doc[0].ents])