from deeppavlov import build_model
import tensorflow as tf
import warnings
import datetime
import logging
import os

import sys
sys.path.append("..")
from utils import pre_process_sentence

config = tf.ConfigProto()
config.gpu_options.allow_growth = True


class Parser:

    def __init__(self, download=True, log=False):

        if not log:
            warnings.filterwarnings("ignore")
            warnings.filterwarnings(action="ignore", module="tensorflow")
            tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
            tf.autograph.set_verbosity(0)
            logging.disable(logging.WARNING)
            os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

        self.model = build_model(
            "ru_syntagrus_joint_parsing", download=download)
        print('Initialization complete!')

    def parse(self, sentence, save=False, batch=3):
        parsed_sentences = []

        if save == True:
            name = str(datetime.datetime.now())[:-7]+'.conll'
            f = open(name, 'w')

        for sent in range(len(sentence)):
            if len(sentence[sent]) == 0:
                sentence[sent] = '.'
                continue
            sentence[sent] = pre_process_sentence(sentence[sent])

        # Syntax parsing. It is best to parse in batches of 3-10 sentences.
        # Otherwise, there may not be enough GPU memory or the parsing speed will be very slow.
        for i in range(0, len(sentence), batch):
            for parse in self.model(sentence[i:i + batch]):
                parsed_sentences.append(parse)
                if save == True:
                    print(parse, file=f)
                    print(file=f)

        if save == True:
            f.close()

        return parsed_sentences
