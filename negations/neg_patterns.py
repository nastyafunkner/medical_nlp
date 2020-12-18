negations = ['не', 'нет', 'отрицать', 'отсутствовать', 'без', 'избегать', 'отказаться']

patterns_part = [{"label": "NEG_PART", "pattern": [{"LEMMA": {"IN": negations}}]}]

patterns = [{"label": "NEG_EXPR", "pattern": [{"LEMMA": "дополнение"}, {"LEMMA": "нет"}]},
            {"label": "NEG_EXPR", "pattern": [{"LEMMA": 'без'}, {"LEMMA": 'чёткий', "OP": "?"}, {"LEMMA": 'связь'}, {"LEMMA": 'с'}, {"LEMMA": 'физический'}, {"LEMMA": 'нагрузка'}]},
            {"label": "NEG_EXPR", "pattern": [{"LEMMA": 'без'}, {"LEMMA": 'чёткий', "OP": "?"}, {"LEMMA": 'связь'}, {"LEMMA": 'с'}, {"LEMMA": 'фн'}]},
            {"label": "NEG_EXPR", "pattern": [{"LEMMA": {"IN": ['без', 'не']}}, {"TEXT": 'Q'}, {"LEMMA": 'инфаркт'}, {"LEMMA": 'миокард'}]},
            {"label": "NEG_EXPR", "pattern": [{"LEMMA": 'инфаркт'}, {"LEMMA": 'миокард'}, {"LEMMA": {"IN": ['без', 'не']}}, {"TEXT": 'Q'}]},
            {"label": "NEG_EXPR", "pattern": [{"LEMMA": {"IN": ['без', 'не']}}, {"TEXT": 'ИМ'}, {"TEXT": 'Q'}]},
            {"label": "NEG_EXPR", "pattern": [{"LEMMA": {"IN": ['без', 'не']}}, {"TEXT": 'Q'}, {"TEXT": 'ИМ'}]},
            {"label": "NEG_EXPR", "pattern": [{"TEXT": 'ИМ'}, {"LEMMA": {"IN": ['без', 'не']}}, {"TEXT": 'Q'}]},
            {"label": "NEG_EXPR", "pattern": [{"LEMMA": 'стент'}, {"LEMMA": 'без'}, {"LEMMA": 'лк'}]},
            {"label": "NEG_EXPR", "pattern": [{"LEMMA": 'стент'}, {"LEMMA": 'без'}, {"TEXT": 'лек'}]},
            {"label": "NEG_EXPR", "pattern": [{"LEMMA": 'стент'},{"LEMMA": 'без'}, {"LEMMA": 'лек.покрытие'}]},
            {"label": "NEG_EXPR", "pattern": [{"LEMMA": 'стент'},{"LEMMA": 'без'}, {"LEMMA": 'лекарственный'}, {"LEMMA": 'покрытие'}]},
            {"label": "NEG_EXPR", "pattern": [{"LEMMA": 'стент'},{"LEMMA": 'без'}, {"LEMMA": 'покрытие'}, {"LEMMA": 'лек/в'}]},
            {"label": "NEG_EXPR", "pattern": [{"POS": "NOUN"}, {"POS": "NOUN"}, {"TEXT": ':'}, {"TEXT": 'ранее', "OP": "?"}, {"TEXT": 'отрицает'}]},
            {"label": "NEG_EXPR", "pattern": [{"POS": "ADJ"}, {"POS": "NOUN"}, {"TEXT": ':'}, {"TEXT": 'ранее', "OP": "?"}, {"TEXT": 'отрицает'}]},
            {"label": "NEG_EXPR", "pattern": [{"POS": "PROPN"}, {"POS": "NOUN"}, {"TEXT": ':'}, {"TEXT": 'ранее', "OP": "?"}, {"TEXT": 'отрицает'}]},
            {"label": "NEG_EXPR", "pattern": [{"POS": "NOUN"}, {"POS": "PROPN"}, {"TEXT": ':'}, {"TEXT": 'ранее', "OP": "?"}, {"TEXT": 'отрицает'}]},
            {"label": "NEG_EXPR", "pattern": [{"POS": "PROPN"}, {"POS": "PROPN"}, {"TEXT": ':'}, {"TEXT": 'ранее', "OP": "?"}, {"TEXT": 'отрицает'}]},
            {"label": "NEG_EXPR", "pattern": [{"POS": "PROPN"}, {"TEXT": ':'}, {"TEXT": 'ранее', "OP": "?"}, {"TEXT": 'отрицает'}]},
            {"label": "NEG_EXPR", "pattern": [{"POS": "NOUN"}, {"TEXT": ':'}, {"TEXT": 'ранее', "OP": "?"}, {"TEXT": 'отрицает'}]},]
