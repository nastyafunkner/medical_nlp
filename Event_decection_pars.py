import numpy as np
import pandas as pd
import re
from spacy.vocab import Vocab
from spacy.language import Language
from utils import doc_from_conllu, convert_to_dataframe
nlp = Language(Vocab())
from Data_preprocess import process_regex
from Data_preprocess import lemmatize
import nltk
import pymorphy2

cyrillic = re.compile(r'[^а-я ]')
mult_ws = re.compile(r'\s+')
nltk.download("stopwords")
stopwords = nltk.corpus.stopwords.words('russian')
morph = pymorphy2.MorphAnalyzer()

def verb_extraction(parse):
    doc = doc_from_conllu(nlp.vocab, parse.split("\n"))
    root = [token for token in doc if token.head == token][0]
    all_result = []
    stop_verb = ['учитывать', 'принимать', 'нет', 'готовиться', 'страдать', 'планироваться',
                 'сохраняться', 'являться', 'выразить', 'лежать', 'наблюдаться', 'быть', 'ощущать', 'расширить']
    for verb in root.subtree: # Для каждого элемента дерева
        if verb.tag_ == 'VERB': # Ищем глагол
            if verb.lemma_ in stop_verb:
                continue
            local_result = []
            childs = [i for i in verb.children] # Дочерние элементы глагола
            texts = [i.text for i in verb.children]
            deps = [i.dep_ for i in verb.children] # Зависимости дочерних элементов
            if 'не' in texts:
                local_result.append('не')
            local_result.append(verb.text)
            if 'nsubj' in deps:
                index = deps.index('nsubj')
                child = childs[index]
                for sub in child.subtree:
                    if sub.lemma_ == '(':  # Если открываются скобки, пропускаем все
                        break
                    if sub.dep_ in ['nsubj', 'case', 'amod', 'conj', 'nmod']:
                        local_result.append(sub.text)
                local_result = str.join(' ', local_result)
                all_result.append(local_result)
                continue
            if 'nsubj:pass' in deps:
                index = deps.index('nsubj:pass')
                child = childs[index]
                for sub in child.subtree:
                    if sub.lemma_ == '(':  # Если открываются скобки, пропускаем все
                        break
                    if sub.dep_ in ['nsubj:pass', 'case', 'amod', 'conj', 'nmod']:
                        local_result.append(sub.text)
                local_result = str.join(' ', local_result)
                all_result.append(local_result)
                continue
            if 'obj' in deps:
                index = deps.index('obj')
                child = childs[index]
                for sub in child.subtree:
                    if sub.lemma_ == '(':  # Если открываются скобки, пропускаем все
                        break
                    if sub.dep_ in ['obj', 'case', 'amod', 'conj', 'nmod']:
                        local_result.append(sub.text)
                local_result = str.join(' ', local_result)
                all_result.append(local_result)
                continue
            if 'obl' in deps:
                index = deps.index('obl')
                child = childs[index]
                for sub in child.subtree:
                    if sub.lemma_ == '(':  # Если открываются скобки, пропускаем все
                        break
                    if sub.dep_ in ['obl', 'case', 'amod', 'conj', 'nmod', 'compound']:
                        local_result.append(sub.text)
                local_result = str.join(' ', local_result)
                all_result.append(local_result)
                continue
    return all_result

def abbr_extraction(parse, abbr_dict):
    all_result = []
    abbrs_1_lvl = abbr_dict.loc[abbr_dict['lvl'] == 1]
    abbrs = abbrs_1_lvl['abbr'].tolist()
    doc = doc_from_conllu(nlp.vocab, parse.split("\n"))
    root = [token for token in doc if token.head == token][0]
    for abbr in root.subtree: # Для каждого элемента дерева
        if abbr.text.lower() in abbrs: # Ищем аббревиатуру
            local_result = []
            if (abbr.dep_ == 'parataxis' and
                any(ch.dep_ == 'nmod' for ch in abbr.children)): # Если такая зависимость и есть nmod, берем ее и nmod
                local_result.append(abbr.text)
                for ch in abbr.children:
                    if ch.dep_ == 'nmod':
                        local_result.append(ch.text)
                local_result = str.join(' ', local_result)
                all_result.append(local_result)
                continue
            if abbr.dep_ == 'parataxis':  # Если просто такая зависимость, это не событие
                continue
            if abbr.head.tag_ == 'VERB': # Если родитель VERB, берем его
                # Если у родительского глагола есть НЕ, берем его тоже
                head_ch = [i.text for i in abbr.head.children] # Дочерные элементы родителя
                deps = [i.dep_ for i in abbr.children]  # Зависимости дочернего элемента
                childs = [i.text for i in abbr.children] # Дочерние элементы
                if 'не' in head_ch:
                    local_result.append('не')
                local_result.append(abbr.head.text)
                # Если у аббревиатуры есть дочка case, берем ее
                if 'case' in deps:
                    index = deps.index('case')
                    case_child = childs[index]
                    local_result.append(case_child)
                local_result.append(abbr.text) # Для этой ситуации, аббревиатуру добавляем в конце
                local_result = str.join(' ', local_result)
                all_result.append(local_result)
                continue
            elif abbr.head.tag_ == 'NOUN' and abbr.head.dep_ in ['nsubj', 'nmod']:
                # берем их
                local_result.append(abbr.head.text)
                local_result.append(abbr.text)
                local_result = str.join(' ', local_result)
                all_result.append(local_result)
                continue
            elif (any(ch.dep_ in ['nmod', 'case'] for ch in abbr.children) or # TODO Приходится копировать условие для цикла, чтобы отделить последний else
                  any(ch.tag_ == 'PROPN' for ch in abbr.children)): # Берем все дочерние по веткам PROPN case nmod:NOUN
                local_result.append(abbr.text)
                for ch in abbr.children:
                    if ch.dep_ in ['nmod', 'case', 'appos']:
                        for sub in ch.subtree:
                            if sub.lemma_ == '(':  # Если открываются скобки, пропускаем все
                                break
                            if sub.dep_ in ['case', 'amod', 'conj', 'nmod', 'appos']:
                                local_result.append(sub.text)
                    #elif ch.tag_ == "PROPN":
                    #    for sub in ch.subtree:
                    #        if sub.dep_ in ['case', 'amod', 'conj', 'nmod']:
                    #            local_result.append(sub.text)
                local_result = str.join(' ', local_result)
                all_result.append(local_result)
                continue
            else:
                # Если все вароианты не сработали то "событие = аббревиатуре"
                local_result.append(abbr.text)
                local_result = str.join(' ', local_result)
                all_result.append(local_result)
                continue

    return all_result

def coloc_extraction(collocations, sent):
    all_result = []
    collocations = collocations['collocation'].tolist()
    proc_sent = process_regex(cyrillic, mult_ws, text=sent)
    proc_sent_tokens = lemmatize(proc_sent, morph, stopwords, min_word_size=2)
    sent_tup = {}
    for i, a in enumerate(proc_sent_tokens):
        other = {i: a}
        sent_tup.update(other)
    local_result = []
    for collocation in collocations:
        nums_tokens = []
        proc_coll = process_regex(cyrillic, mult_ws, text=collocation)
        proc_coll_tokens = lemmatize(proc_coll, morph, stopwords, min_word_size=2)
        # TODO Сейчас предполагается что словосочетание встречается в предложении один раз
        for i, token in enumerate(proc_sent_tokens):
            for coll_token in proc_coll_tokens:
                if coll_token == token:
                    nums_tokens.append(i)
        if (nums_tokens != [] and # список коэффициентов не пустой
            len(nums_tokens)==len(proc_coll_tokens) and # количество элементов в списке равно длине словосочетания
            (nums_tokens[len(nums_tokens)-1] - nums_tokens[0]) == (len(nums_tokens)-1)): # Если разница крайних равна количеству, значит они идут подряд
            local_result.append(nums_tokens)
    # Объединяем пересекающиеся словосочения
    global_result = []
    for result_1 in local_result:
        if len(local_result) > 1:
            for result_2 in local_result:
                if result_1 == result_2: # Повторения пропускаем
                    continue
                if any(num in result_2 for num in result_1):# Если есть хотя бы один одинаковый токен
                    left_edge = min([result_1[0],result_2[0]])
                    right_edge = max([result_1[-1], result_2[-1]])
                    result_nums = list(np.arange(left_edge,right_edge+1)) # Объединяем словосочетания в одно
                    result_text = [sent_tup[num] for num in result_nums]
                    if any(word in ['килограмм', 'сантиметр'] for word in result_text): # Избавляемся от ошибко лемматизации
                        for i, w in enumerate(result_text):
                            if w == 'килограмм':
                                result_text[i] = 'кг'
                            elif w == 'сантиметр':
                                result_text[i] = 'см'
                    all_result.append(result_text)
        else:
            result = local_result[0]
            result_text = [sent_tup[num] for num in result]
            if any(word in ['килограмм', 'сантиметр'] for word in result_text):
                for i, w in enumerate(result_text):
                    if w == 'килограмм':
                        result_text[i] = 'кг'
                    elif w == 'сантиметр':
                        result_text[i] = 'см'
            all_result.append(result_text)
    all_result = my_set(all_result) # Удаляем повторы
    return all_result

# Функция удалени повторов в списке
def my_set(l):
    n = []
    for i in l:
        if i not in n:
            n.append(i)
    return n

def event_detection(parse, sent, abbr_dict, collocations, only):
    all_result = []
    if only == 0:
        all_result = verb_extraction(parse)

    elif only == 1 or only == 2:
        verb_extr = verb_extraction(parse)
        abbr_extr = abbr_extraction(parse, abbr_dict)
        verb_result = verb_extr.copy()
        abbr_result = abbr_extr.copy()
        for k, verb_res in enumerate(verb_extr):
            for abbr_res in abbr_extr:
                # Разбиваем предложения на слова
                verb_res_split = verb_res.split(' ')
                abbr_res_split = abbr_res.split(' ')
                # если аббревиатура внутри глагола то удалаем аббревиатуру из аббревиатур
                if all(abbr_word in verb_res_split for abbr_word in abbr_res_split):
                    abbr_result.remove(abbr_res)
                    continue
                for i, verb_word in enumerate(verb_res_split):
                    if abbr_res_split[0] == verb_word: # Если между элементами есть пересечение
                        counter = 0 # Ищем количество пересечений
                        for abbr_res_split_count in abbr_res_split:
                            if abbr_res_split_count in verb_res_split:
                                counter = counter + 1
                            else:
                                break
                        # объединяем в одно и меняем исходное по глаголам
                        remain_index = len(abbr_res_split) - counter
                        abbr_res_split = abbr_res_split[remain_index:]
                        verb_res_split = verb_res_split + abbr_res_split
                        verb_res = str.join(' ', verb_res_split)
                        verb_result[k] = verb_res
                        # удаляем из аббревиатур
                        try:
                            abbr_result.remove(abbr_res)
                        except:
                            print('aaa')
                        break
        # Объединяем списки
        all_result = verb_result + abbr_result

        if only == 2:
            coll_extr = coloc_extraction(collocations, sent)
            coll_extr_real = []
            # Находим соответствие слов в предложении в исходной форме
            # Для каждого найденного словосочетания
            for coll in coll_extr:
                # находим все сходства по нормальной форме первого слова
                parse_df = pd.DataFrame([x.split('\t') for x in parse.split('\n')])
                coll_nums = parse_df.loc[parse_df[2] == coll[0]]
                coll_nums = coll_nums[0].tolist()
                sent_words = parse_df[2].tolist()
                sent_words_real = parse_df[1].tolist()
                # Для каждого номера
                for num in coll_nums:
                    num = int(num) - 1
                    words = sent_words[num:(num+len(coll))]# Берем слова в выбранном промежутке
                    if all(word in coll for word in words): # Если они соответствуют словосочетанию
                        words = sent_words_real[num:(num + len(coll))] # Берем его в ненормальной форме
                        words = str.join(' ', words) # Объединяем
                        coll_extr_real.append(words)
                        break

            coll_result = coll_extr_real.copy()
            for k, all_res in enumerate(all_result):
                for coll_res in coll_result:
                    # Разбиваем предложения на слова
                    all_res_split = all_res.split(' ')
                    coll_res_split = coll_res.split(' ')
                    # если аббревиатура внутри глагола то удалаем аббревиатуру из аббревиатур
                    if all(coll_word in all_res_split for coll_word in coll_res_split):
                        coll_result.remove(coll_res)
                        continue
                    for i, all_word in enumerate(all_res_split):
                        if coll_res_split[0] == all_word:  # Если между элементами есть пересечение
                            # объединяем в одно и меняем исходное по глаголам
                            remain_index = len(all_res_split) - i
                            coll_res_split = coll_res_split[remain_index:]
                            all_res_split = all_res_split + coll_res_split
                            all_res = str.join(' ', all_res_split)
                            all_result[k] = all_res
                            # удаляем из аббревиатур
                            coll_result.remove(coll_res)
                            break
            # Объединяем списки
            all_result = all_result + coll_result

    return all_result

'''
abbr_dict = pd.read_csv('data/abbr_for_anamnesis.csv')
collocations = pd.read_csv('data/collocations.csv')
parse = '1\tУчитывая\tучитывать\tVERB\t_\tAspect=Imp|Tense=Pres|VerbForm=Conv|Voice=Act\t20\tadvcl\t_\t_\n2\tколебания\tколебание\tNOUN\t_\tAnimacy=Inan|Case=Acc|Gender=Neut|Number=Plur\t1\tobj\t_\t_\n3\tв\tв\tADP\t_\t_\t4\tcase\t_\t_\n4\tанамнезе\tанамнез\tNOUN\t_\tAnimacy=Inan|Case=Loc|Gender=Masc|Number=Sing\t2\tnmod\t_\t_\n5\tконцентрации\tконцентрация\tNOUN\t_\tAnimacy=Inan|Case=Gen|Gender=Fem|Number=Sing\t2\tnmod\t_\t_\n6\tингибиторов\tингибитор\tNOUN\t_\tAnimacy=Inan|Case=Gen|Gender=Masc|Number=Plur\t5\tnmod\t_\t_\n7\tкальциневрина\tкальциневрин\tNOUN\t_\tAnimacy=Inan|Case=Gen|Gender=Masc|Number=Sing\t6\tnmod\t_\t_\n8\tна\tна\tADP\t_\t_\t9\tcase\t_\t_\n9\tфоне\tфон\tNOUN\t_\tAnimacy=Inan|Case=Loc|Gender=Masc|Number=Sing\t5\tnmod\t_\t_\n10\tданной\tданный\tADJ\t_\tCase=Gen|Degree=Pos|Gender=Fem|Number=Sing\t11\tamod\t_\t_\n11\tдозы\tдоза\tNOUN\t_\tAnimacy=Inan|Case=Gen|Gender=Fem|Number=Sing\t9\tnmod\t_\t_\n12\t(\t(\tPUNCT\t_\t_\t17\tpunct\t_\t_\n13\tв\tв\tADP\t_\t_\t17\tcc\t_\t_\n14\tт\tтот\tDET\t_\tAnimacy=Inan|Case=Acc|Gender=Neut|Number=Sing\t13\tfixed\t_\t_\n15\t.\t.\tPRON\t_\tAnimacy=Inan|Case=Dat|Gender=Neut|Number=Sing\t13\tfixed\t_\t_\n16\tч.\tч.\tPUNCT\t_\t_\t13\tfixed\t_\t_\n17\tпередозировки\tпередозировка\tNOUN\t_\tAnimacy=Inan|Case=Gen|Gender=Fem|Number=Sing\t11\tparataxis\t_\t_\n18\t)\t)\tPUNCT\t_\t_\t17\tpunct\t_\t_\n19\t,\t,\tPUNCT\t_\t_\t1\tpunct\t_\t_\n20\tнеобходим\tнеобходимый\tADJ\t_\tDegree=Pos|Gender=Masc|Number=Sing|Variant=Short\t0\troot\t_\t_\n21\tконтроль\tконтроль\tNOUN\t_\tAnimacy=Inan|Case=Nom|Gender=Masc|Number=Sing\t20\tnsubj\t_\t_\n22\tв\tв\tADP\t_\t_\t23\tcase\t_\t_\n23\tдинамике\tдинамика\tNOUN\t_\tAnimacy=Inan|Case=Loc|Gender=Fem|Number=Sing\t21\tnmod\t_\t_\n24\t-\t-\tPUNCT\t_\t_\t27\tpunct\t_\t_\n25\tчерез\tчерез\tADP\t_\t_\t27\tcase\t_\t_\n26\t2-3\t2-3\tNUM\t_\t_\t27\tnummod\t_\t_\n27\tнедели\tнеделя\tNOUN\t_\tAnimacy=Inan|Case=Gen|Gender=Fem|Number=Sing\t21\tparataxis\t_\t_\n28\t.\t.\tPUNCT\t_\t_\t20\tpunct\t_\t_'

sent = 'Существенной динамики нет.'

print(event_detection(parse, sent, abbr_dict, collocations, 2))
'''

#print(coloc_extraction(collocations, sent))
#print(abbr_extraction(parse, abbr_dict))
#print(verb_extraction(parse))
