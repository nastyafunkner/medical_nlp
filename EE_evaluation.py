import pandas as pd
import re
import numpy as np
from Event_decection_pars import event_detection

test_data = pd.read_csv('data/EE_test_data.csv')
parse_sents = pd.read_csv('data/f_parsed_anamnesis_0_99.csv', sep = '$')
abbr_dict = pd.read_csv('data/abbr_for_anamnesis.csv')
collocations = pd.read_csv('data/collocations.csv')

all_sent = test_data['sent'].tolist()
all_true = test_data['result'].tolist()
Nt = 0 # Количество слов true
Np = 0 # Количество слов, выделенных как true
Ntp = 0 # Количество слова, правально выделенных как true

index = 0
for sent, true in zip(all_sent, all_true):

    index = index + 1
    print(index,'/', len(all_sent))
    parse_sent = parse_sents.loc[parse_sents['work'] == sent]
    try:
        parse = parse_sent.iloc[0]['parse']
    except:
        continue
    parse = parse[2:(len(parse) - 2)]  # Убираем скобки и кавычки по краям
    parse = re.sub('\\\\.', parse, '\\$')
    result_list = event_detection(parse, sent, abbr_dict, collocations, 2)
    true_list = true.split(sep='\', ')
    true_list = [re.sub("[\[|\'|\"|\]]", "", s) for s in true_list]

    for result in result_list: # Обновляем количество слов, выделенных как true
        result = result.split(sep=' ')
        Np = Np + len(result)
    for true_l in true_list: # Обновляем количество слов true (эталонных)
        true_l = true_l.split(sep=' ')
        Nt = Nt + len(true_l)
    if result_list == []: # Если ничего не выдлели, продолжаем
        continue
    # Имеем 2 списка: true_list и result_list
    # Делаем их копии
    # Необходимо сопоставить каждый с каждым
    all_match_list = []
    for result in result_list: # Для каждого результата смотрим количество пересечений по каждому эталону
        result_words = result.split(sep=' ')
        match_list = []
        for true_l in true_list: # Для каждого эталона смотрим количество пересечений
            match_sum = 0
            for word in result_words:
                if word in true_l:
                    match_sum = match_sum + 1
            match_list.append(match_sum)
        all_match_list.append(match_list)
    # Найти наибольшее количество пересечений
    x = np.array(all_match_list) # Преобразуем в массив
    m = np.asmatrix(x) # Преобразуем в матрицу
    # Проходим по каждому столбцу, соответстующему каждому эталону, и берем максимальное значение
    for i in range(len(true_list)):
        arr = m[:,i]
        max = arr.max()
        Ntp = Ntp + max

# Посчитать все значения для P, R и F

P = Ntp/Np
R = Ntp/Nt
F = 2*P*R/(P+R)
print('P = ', P)
print('R = ', R)
print('F = ', F)