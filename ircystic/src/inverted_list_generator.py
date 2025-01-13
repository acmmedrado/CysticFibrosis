import configparser
import glob
import logging
import os
import xml.etree.ElementTree as ET
from collections import OrderedDict
from os import walk
import csv
import toolz.dicttoolz as dictionaryTools
from nltk.tokenize import word_tokenize

import ircystic.src.shared.sentence_handler as sHandler

"""
This code goal is to create Inverted List

Inverted List Generator will create an csv file
Row example: 
    FIBROSIS ; [1,2,2,3,4,5,10,15,21,21,21]
"""

# LOG format Configurations
FORMAT = '%(asctime)s %(levelname)s: %(message)s'
DATEFMT = '%d %b %H:%M:%S'
list_of_files = glob.glob('/log/*.log')  # * means all if need specific format
latest_file = max(list_of_files, key=os.path.getctime)
logging.basicConfig(filename=latest_file, level=logging.INFO, format=FORMAT, datefmt=DATEFMT, filemode="a")


def run(params={}):
    logging.info('Initiating inverted list generator\n')

    configFile = os.getcwd() + '\ircystic\src\config\GLI.cfg'
    config = configparser.ConfigParser()
    config.read(configFile)

    filesPathParam = params['LEIA'] if 'LEIA' in params.keys() else config.get('DEFAULT', 'READ')
    filesPath = os.getcwd() + filesPathParam
    filenames = next(walk(filesPath), (None, None, []))[2]  # [] if no file

    outputFileParam = params['ESCREVA'] if 'ESCREVA' in params.keys() else config.get('DEFAULT', 'WRITE')
    outputFileParam = os.getcwd() + outputFileParam

    recordContentDict = OrderedDict()

    for xmlFile in filenames:
        fullFileName = filesPath + xmlFile
        tree = ET.parse(fullFileName)
        root = tree.getroot()
        # print(len(tree.getroot()))
        for record in root.findall('RECORD'):
            recordNum = record.find("RECORDNUM").text
            recordNum = recordNum.strip()
            try:
                textContent = record.find("ABSTRACT").text
                recordContentDict[recordNum] = textContent
            except:
                try:
                    textContent = record.find("EXTRACT").text
                    recordContentDict[recordNum] = textContent
                except:
                    logging.warning(f"Was not possible to extract any content from this article: {recordNum}")
                    continue

    configFile = os.getcwd() + '\ircystic\src\config\INDEX.cfg'
    config = configparser.ConfigParser()
    config.read(configFile)

    # Remove Line break
    recordContentDict = dictionaryTools.valmap(sHandler.remove_line_break_in_string, recordContentDict)

    # remove punctuation
    recordContentDict = dictionaryTools.valmap(sHandler.remove_punctutaion, recordContentDict)

    three_leters_or_more = params['MIN_WORD_LENGTH_3'] if 'MIN_WORD_LENGTH_3' in params.keys() else config['DEFAULT'].getboolean('MIN_WORD_LENGTH_3')
    if three_leters_or_more:
        recordContentDict = dictionaryTools.valmap(sHandler.all_words_three_or_more, recordContentDict)

    only_letters = params['ONLY_LETTERS'] if 'ONLY_LETTERS' in params.keys() else config['DEFAULT'].getboolean('ONLY_LETTERS')
    if only_letters:
        recordContentDict = dictionaryTools.valmap(sHandler.remove_number_in_string, recordContentDict)

    ignore_stop_words = params['IGNORE_STOP_WORDS'] if 'IGNORE_STOP_WORDS' in params.keys() else config['DEFAULT'].getboolean('IGNORE_STOP_WORDS')
    if ignore_stop_words:
        recordContentDict = dictionaryTools.valmap(sHandler.remove_stop_word, recordContentDict)

    # Transform words to UPPERCASE
    recordContentDict = dictionaryTools.valmap(sHandler.changing_cases, recordContentDict)

    # print("\n\n\n Example: \n")
    # print(recordContentDictTokenized['01238'])
    # print("\n\n\n\n\n")

    use_stemmer = params['USE_STEMMER'] if 'USE_STEMMER' in params.keys() else config['DEFAULT'].getboolean('USE_STEMMER')
    if use_stemmer:
        recordContentDict = dictionaryTools.valmap(sHandler.stemmer, recordContentDict)

    recordContentDictTokenized = dictionaryTools.valmap(word_tokenize, recordContentDict)

    all_words = []
    for key, token_list in recordContentDictTokenized.items():
        all_words += token_list

    # catch unique values
    all_words = list(set(all_words))

    wordFrequencyDict = OrderedDict()
    for word in all_words:
        # print(f"Searching for the word: {word}")
        for key, token_list in recordContentDictTokenized.items():
            if token_list.count(word) != 0:
                if not word in wordFrequencyDict.keys():
                    wordFrequencyDict[word] = []
                for i in range(token_list.count(word)):
                    wordFrequencyDict[word].append(key)

    with open(outputFileParam, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', lineterminator='\n')
        writer.writerow(['Word', 'Documents'])
        for item in wordFrequencyDict.items():
            writer.writerow(item)
    logging.info('Ending invert list generator\n')


if __name__ == "__main__":
    run()
