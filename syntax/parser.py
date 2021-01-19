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
    """
    This class includes methods for syntax parsing.
    Parameters
    ----------
    download : bool, (default=True)
        Flag, which allows to download model from the Internet, if it is not available.
    log : bool, (default=False)
        Flag, which allows turn on logging messages.

    Examples
    --------
    >>> from syntax.parser import Parser
    
    >>> parser = Parser()
    >>> parser.parse(["Болеет СД 2 типа в течении 5 лет ."])

    ['1\tБолеет\tболеть\tVERB\t_\tAspect=Imp|Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act\t0\troot\t_\t_
      2\tСД\tсд\tPROPN\t_\tAnimacy=Inan|Case=Nom|Gender=Neut|Number=Sing\t1\tnsubj\t_\t_
      3\t2\t2\tNUM\t_\t_\t4\tnummod\t_\t_
      4\tтипа\tтип\tNOUN\t_\tAnimacy=Inan|Case=Gen|Gender=Masc|Number=Sing\t2\tnmod\t_\t_\n
      5\tв\tв\tADP\t_\t_\t8\tcase\t_\t_
      6\tтечении\tтечение\tNOUN\t_\tAnimacy=Inan|Case=Loc|Gender=Neut|Number=Sing\t5\tfixed\t_\t_
      7\t5\t5\tNUM\t_\t_\t8\tnummod\t_\t_
      8\tлет\tгод\tNOUN\t_\tAnimacy=Inan|Case=Gen|Gender=Masc|Number=Plur\t1\tobl\t_\t_
      9\t.\t.\tPUNCT\t_\t_\t1\tpunct\t_\t_']
    """

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
        """
        Find event for particular time expression.
        Parameters
        ----------
        sentence : list
            List of sentences or sentence
        save : bool, (default=False)
            Flag, which allows to save result of syntax parsing to Conllu format.
        batch : int, (default=3)
            The total number of sentences presented in one batch. It is best to parse in batches of 3-10 sentences.
            Otherwise, there may not be enough GPU memory or the parsing speed will be very slow.

        Returns
        -------
        event : list
            Time event.
        """
        parsed_sentences = []

        if save == True:
            name = str(datetime.datetime.now())[:-7]+'.conll'
            f = open(name, 'w')

        for sent in range(len(sentence)):
            if len(sentence[sent]) == 0:
                sentence[sent] = '.'
                continue
            sentence[sent] = pre_process_sentence(sentence[sent])

        for i in range(0, len(sentence), batch):
            for parse in self.model(sentence[i:i + batch]):
                parsed_sentences.append(parse)
                if save == True:
                    print(parse, file=f)
                    print(file=f)

        if save == True:
            f.close()

        return parsed_sentences
