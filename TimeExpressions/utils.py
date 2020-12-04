from spacy.tokens import Doc, Token
import pandas as pd
import re


def doc_from_conllu(vocab, lines):
    """
    Convert conllu string to spacy doc
    Parameters
    ----------
    vocab : Spacy vocab
        Spacy model vocabulary.
    lines : list
        Sentence in CONLL-U.

    Returns
    -------
    result : Spacy doc
    """
    words, spaces, tags, poses, morphs, lemmas = [], [], [], [], [], []
    heads, deps = [], []
    Token.set_extension(
        "is_digit", getter=lambda token: token.text.isnumeric(), force=True)
    for i in range(len(lines)):
        line = lines[i]
        parts = line.split("\t")
        id_, word, lemma, pos, tag, morph, head, dep, _1, misc = parts
        if "." in id_ or "-" in id_:
            continue
        if "SpaceAfter=No" in misc:
            spaces.append(False)
        else:
            spaces.append(True)

        id_ = int(id_) - 1
        head = (int(head) - 1) if head not in ("0", "_") else id_
        tag = pos if tag == "_" else tag
        morph = morph if morph != "_" else ""
        dep = "ROOT" if dep == "root" else dep

        words.append(word)
        lemmas.append(lemma)
        poses.append(pos)
        tags.append(tag)
        morphs.append(morph)
        heads.append(head)
        deps.append(dep)

    doc = Doc(vocab, words=words, spaces=spaces)
    for i in range(len(doc)):
        doc[i].tag_ = tags[i]
        doc[i].pos_ = poses[i]
        doc[i].dep_ = deps[i]
        doc[i].lemma_ = lemmas[i]
        doc[i].head = doc[heads[i]]
    doc.is_parsed = True
    doc.is_tagged = True

    return doc


def pre_process_sentence(sentence):
    """
    Preprocess sentence.
    Add dots in the end. Add spaces to dashes.
    Convert all dates to format %H.%M %d.%m.%y
    Parameters
    ----------
    sentence : str
        Original sentence.

    Returns
    -------
    sentence : str
        Processed sentence.
    """
    day = r'(?:[12][0-9]|3[01]|0?[1-9])'
    month = r'(?:10|11|12|0[1-9])'
    year4d = r'(?:19[1-9][0-9]|20[0-9][0-9])'
    year2d = r'(?:\d\d)'

    day_r = r'((?:[12][0-9]|3[01]|0?[1-9]))'
    month_r = r'((?:10|11|12|0[1-9]))'
    year4d_r = r'((?:19[1-9][0-9]|20[1-9][0-9]))'
    year2d_r = r'((?:\d\d))'
    hour_r = r'((?:[01][0-9]|2[0-3]|[0-9]))'
    minute_r = r'((?:[0-5][0-9]))'

    shortdate_r = r'{}[-./,]{}[-./,]{}'.format(day_r, month_r, year2d_r)
    date_r = r'{}[-./,]{}[-./,]{}'.format(day_r, month_r, year4d_r)
    date_my4d_r = r'{}[.-/]{}'.format(month_r, year4d_r)
    date_my2d_r = r'{}[.-/]{}'.format(month_r, year2d_r)
    time_r = r'{}[-.:-]{}'.format(hour_r, minute_r)

    for i in [r"[-]+", r"[\s]+", r"[,]+", r"[.]+", r"[:]+"]:
        sentence = re.sub(i, lambda x: x.group(0)[0], sentence)

    sentence = re.sub(r"[А-Яа-я\d][-–,][А-Яа-я]", lambda x: x.group(
        0).replace(x.group(0)[1], " "+x.group(0)[1]+" "), sentence)
    sentence = re.sub(
        r"[А-Яа-я]\d", lambda x: x.group(0).replace(x.group(0)[0], x.group(0)[0]+" "), sentence)
    sentence = re.sub(
        r"\d[А-Яа-я]", lambda x: x.group(0).replace(x.group(0)[-1], " "+x.group(0)[-1]), sentence)
    sentence = re.sub(r"г.\w", lambda x: x.group(
        0).replace("г.", "г "), sentence)
    sentence = re.sub(r"- х", '', sentence)
    sentence = re.sub(r" х ", ' ', sentence)
    sentence = re.sub(r"(19[0-9][0-9]|20[0-9][0-9])[,]",
                      lambda x: x.group(0).replace(',', ' , '), sentence)
    sentence = re.sub(r"[А-Яа-я][.][А-Яа-я\d]",
                      lambda x: x.group(0).replace('.', ' . '), sentence)
    sentence = re.sub(r"[Пп]ациент \d+ лет",
                      lambda x: x.group(0)[0:7], sentence)
    sentence = re.sub(r"[Пп]ациентка \d+ лет",
                      lambda x: x.group(0)[0:9], sentence)

    sentence = re.sub(r"–", '-', sentence)
    sentence = re.sub(r"[.]:", '. :', sentence)
    sentence = re.sub(r"[.]-", '-', sentence)
    sentence = re.sub(r"[.],\w", lambda x: x.group(
        0).replace(',', ' , '), sentence)
    sentence = re.sub(r"\d[.],", lambda x: x.group(
        0).replace(',', ' , '), sentence)
    sentence = re.sub(r"[.],", lambda x: x.group(
        0).replace(',', ' , '), sentence)
    sentence = re.sub(
        r"\w-\s", lambda x: x.group(0).replace('- ', ' - '), sentence)
    sentence = re.sub(
        r"\s-\w", lambda x: x.group(0).replace(' -', ' - '), sentence)
    sentence = re.sub(r'({}[./-]{}[.-/]{}[-])'.format(day, month,
                                                      year4d), lambda x: x.group(0)[:-1] + ' ', sentence)
    sentence = re.sub(r"\D,\d", lambda x: x.group(
        0).replace(',', ' , '), sentence)

    sentence = re.sub(r"\sг[.],\s", lambda x: x.group(
        0).replace("г.,", "г ,"), sentence)
    sentence = re.sub(r"г.[\s\w]", lambda x: x.group(
        0).replace("г.", "г "), sentence)

    sentence = re.sub(r'({}.{}).[-–]({}.{}.{})'.format(day, month, day, month, year4d),
                      lambda x: '{} - {}'.format(x.group(1), x.group(2)), sentence)  # 6.12.-10.12.2010
    sentence = re.sub(r'({}.{}).[-–]({}.{}.{})'.format(day, month, day, month, year2d),
                      lambda x: '{} - {}'.format(x.group(1), x.group(2)), sentence)  # 6.12.-10.12.10
    sentence = re.sub(r'({}.{})[-–]({}.{}.{})'.format(day, month, day, month, year4d),
                      lambda x: '{} - {}'.format(x.group(1), x.group(2)), sentence)  # 6.12-10.12.2010
    sentence = re.sub(r'({}.{})[-–]({}.{}.{})'.format(day, month, day, month, year2d),
                      lambda x: '{} - {}'.format(x.group(1), x.group(2)), sentence)  # 6.12-10.12.10
    sentence = re.sub(r'({}[./,-]{}[./,-]{})[-–]({}[./,-]{}[./,-]{})'.format(day, month, year2d, day,
                                                                             month, year4d), lambda x: '{} - {}'.format(x.group(1), x.group(2)), sentence)  # 16.07.12-23.07.2012
    sentence = re.sub(r'({}[./,-]{}[./,-]{})[-–]({}[./,-]{}[./,-]{})'.format(day, month, year2d, day,
                                                                             month, year2d), lambda x: '{} - {}'.format(x.group(1), x.group(2)), sentence)  # 16.07.12-23.07.12
    sentence = re.sub(r'({})[-–]({}[./,-]{}[./,-]{})'.format(day, day, month, year4d),
                      lambda x: '{} - {}'.format(x.group(1), x.group(2)), sentence)  # 10-13.09.2011
    sentence = re.sub(r'({})[-–]({}[./,-]{}[./,-]{})'.format(day, day, month, year2d),
                      lambda x: '{} - {}'.format(x.group(1), x.group(2)), sentence)  # 10-13.09.11
    sentence = re.sub(date_r, lambda x: '{}.{}.{}'.format(
        x.group(1), x.group(2), x.group(3)), sentence)
    sentence = re.sub(shortdate_r, lambda x: '{}.{}.{}'.format(
        x.group(1), x.group(2), x.group(3)), sentence)
    sentence = re.sub(date_my4d_r, lambda x: '{}.{}'.format(
        x.group(1), x.group(2)), sentence)
    sentence = re.sub(date_my2d_r, lambda x: '{}.{}'.format(
        x.group(1), x.group(2)), sentence)
    sentence = re.sub(time_r, lambda x: '{}.{}'.format(
        x.group(1), x.group(2)), sentence)

    if sentence[-1] != ".":
        sentence = sentence + " ."
    return sentence

def convert_to_dataframe(docs):
    """
    Present spacy docs in pandas dataframe format
    Parameters
    ----------
    docs : list
        list of parsed sentences

    Returns
    -------
    sentence : Pandas DataFrame
        Table of parsed sentences.
    """
    time_expr, rules, norms, uncertains, events = [], [], [], [], []
    sentences, dates, birthdates, stamps = [], [], [], []

    for doc in docs:
        sentences.append(str(doc))
        dates.append(str(doc._.date))
        birthdates.append(str(doc._.birthday))

        norms.append([ent._.normal_form for ent in doc.ents])
        uncertains.append([ent._.uncertain for ent in doc.ents])
        time_expr.append([ent.text for ent in doc.ents])
        stamps.append([ent._.timestamp for ent in doc.ents])
        rules.append([ent.ent_id_ for ent in doc.ents])
        events.append([ent._.event for ent in doc.ents])

    time_expr = [', '.join(expr) for expr in time_expr]
    events = [', '.join(event) for event in events]
    rules = [', '.join(rule) for rule in rules]
    # stamps = [', '.join(stamp) for stamp in stamps]
    norms = [', '.join([' – '.join([str(y) for y in x]) if type(
        x) is list else str(x) for x in norm]) for norm in norms]
    uncertains = [', '.join(['[{}]'.format(', '.join([str(y) for y in x])) if type(
        x) is list else str(x) for x in uncertain]) for uncertain in uncertains]
    uncertains = [i.replace('[]', 'None') for i in uncertains]

    df = pd.DataFrame({'sentence': sentences, 'date': dates, 'birthdate': birthdates, 
                       'time_expr': time_expr, 'event': events, 'norm': norms, 
                       'uncertain': uncertains,'stamp': stamps, 'rule': rules})

    return df
