import logging
import glob
import os
import configparser
import xml.etree.ElementTree as ET
from collections import OrderedDict
import csv

config = configparser.ConfigParser()

import ircystic.src.shared.sentence_handler as sHandler

"""
This code aims to transform query files (xml) to have the same pattern from Inverted List.
"""

# LOG format Configurations
FORMAT = '%(asctime)s %(levelname)s: %(message)s'
DATEFMT = '%d %b %H:%M:%S'
list_of_files = glob.glob('/log/*.log')  # * means all if need specific format
latest_file = max(list_of_files, key=os.path.getctime)
logging.basicConfig(filename=latest_file, level=logging.INFO, format=FORMAT, datefmt=DATEFMT, filemode="a")


def sentenceHandle(sentence, params):
    configFile = os.getcwd() + '\ircystic\src\config\INDEX.cfg'
    config.read(configFile)

    # Remove Line break
    sentence = sHandler.remove_line_break_in_string(sentence)

    # remove punctuation
    sentence = sHandler.remove_punctutaion(sentence)

    two_leters_or_more = params['MIN_WORD_LENGTH'] if 'MIN_WORD_LENGTH' in params.keys() else config[
        'DEFAULT'].getboolean('MIN_WORD_LENGTH_3')
    if two_leters_or_more:
        sentence = sHandler.all_words_three_or_more(sentence)

    only_letters = params['ONLY_LETTERS'] if 'ONLY_LETTERS' in params.keys() else config['DEFAULT'].getboolean(
        'ONLY_LETTERS')
    if only_letters:
        sentence = sHandler.remove_number_in_string(sentence)

    ignore_stop_words = params['IGNORE_STOP_WORDS'] if 'IGNORE_STOP_WORDS' in params.keys() else config[
        'DEFAULT'].getboolean('IGNORE_STOP_WORDS')
    if ignore_stop_words:
        sentence = sHandler.remove_stop_word(sentence)

    use_stemmer = params['USE_STEMMER'] if 'USE_STEMMER' in params.keys() else config['DEFAULT'].getboolean(
        'USE_STEMMER')
    if use_stemmer:
        sentence = sHandler.stemmer(sentence)

    # to uppercase
    sentence = sHandler.changing_cases(sentence)

    return sentence


def build_querie_vector(querie, tokenSpace):
    term_vector = list()

    for token in tokenSpace:
        if token in querie:
            term_vector.append(float(1))
        else:
            term_vector.append(float(0))

    return (term_vector)


def write_csv_files(queriestDict):
    configFile = os.getcwd() + '\ircystic\src\config\PC.cfg'
    config.read(configFile)

    # output files
    processed_queries_file = os.getcwd() + config.get('PATH', 'CONSULTAS')
    expected_results_file = os.getcwd() + config.get('PATH', 'ESPERADOS')
    queries_vector = os.getcwd() + config.get('PATH', 'CONSULTASFolder') + "querieVectors.csv"

    # writing output

    with open(processed_queries_file, "w") as outfile:
        w = csv.writer(outfile, delimiter=";", lineterminator='\n')

        for key, val in queriestDict.items():
            w.writerow([key, val["queryText"]])

    with open(expected_results_file, "w") as outfile:
        w = csv.writer(outfile, delimiter=";", lineterminator='\n')

        for key, val in queriestDict.items():
            for score, doc in val['queryResults'].items():
                w.writerow([key, doc, score])

    with open(queries_vector, "w") as outfile:
        w = csv.writer(outfile, delimiter=";", lineterminator='\n')
        for key, val in queriestDict.items():
            w.writerow([key, val['queryVector']])


def run(params={}):
    configFile = os.getcwd() + '\ircystic\src\config\PC.cfg'
    config.read(configFile)
    queriesFiles = os.getcwd() + config.get('PATH', 'LEIA')

    configFile = os.getcwd() + '\ircystic\src\config\GLI.cfg'
    config.read(configFile)
    inverted_index_file = os.getcwd() + config.get('DEFAULT', 'WRITE')

    with open(inverted_index_file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        global_tokens = []
        next(reader, None)  # skip the headers
        for row in reader:
            global_tokens.append(row[0])

    tree = ET.parse(queriesFiles)
    root = tree.getroot()

    queriestDict = OrderedDict()

    for query in root.findall('QUERY'):

        queryNumber = query.find("QueryNumber").text.strip()
        queryText = query.find("QueryText").text.strip()
        queryText = sentenceHandle(queryText, params)
        queryResultsQtd = query.find("Results").text.strip()

        queryVector = build_querie_vector(queryText, global_tokens)

        queryResults = OrderedDict()

        for item in query.find("Records").findall('Item'):
            document = item.text.strip()
            score = item.attrib['score'].strip()
            queryResults[score] = document

        queriestDict[queryNumber] = {'queryText': queryText, 'queryVector': queryVector,
                                     'queryResultsQtd': queryResultsQtd, 'queryResults': queryResults}

    write_csv_files(queriestDict)


if __name__ == "__main__":
    logging.info("\nBeginning search processor module run\n")
    run()
    logging.info("\nEnding search processor module run\n")
