import logging
import glob
import os
import configparser
from collections import OrderedDict
import csv
import math

"""
This code goal is to create Vectorial Model from an Inverted List
"""


# LOG format Configurations
FORMAT = '%(asctime)s %(levelname)s: %(message)s'
DATEFMT = '%d %b %H:%M:%S'
list_of_files = glob.glob('/log/*.log')  # * means all if need specific format
latest_file = max(list_of_files, key=os.path.getctime)
logging.basicConfig(filename=latest_file, level=logging.INFO, format=FORMAT, datefmt=DATEFMT, filemode="a")


configFile = os.getcwd() + '\ircystic\src\config\INDEX.cfg'
config = configparser.ConfigParser()
config.read(configFile)

# Return the number of times a given term appears in a given document
def _get_raw_term_frequency(term,document_identifier,inverted_index):
    frequency = len([ id for id in inverted_index[term] if id == document_identifier] )
    return(frequency)


def run(params={}):

    logging.info("\nInitiating indexer\n")

    inverted_index_file = os.getcwd() + config.get('PATH', 'READ')

    inverted_index = OrderedDict()

    with open(inverted_index_file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader, None)
        for row in reader:
            token = row[0].strip()
            document_occurrences = row[1].lstrip('[').rstrip(']').replace("'", "").split(',')
            inverted_index[token] = document_occurrences

    weighting_function = config.get('DEFAULT', 'WEIGHT_FUNCTION')
    if weighting_function != 'tf-idf':
        raise ValueError("Invalid weighting function. Available function is tf-idf")

    words_list = inverted_index.keys()

    documents_list = []
    for key , value in inverted_index.items():
        documents_list += value
    documents_list = list(set(documents_list))

    count_documents = len(documents_list)

    inverse_document_frequencies = OrderedDict()

    for term,hits in inverted_index.items():
        # use set to remove duplicate documents
        doc_count = len(set(hits))
        inverse_document_frequencies[term] = math.log(count_documents/doc_count)


    # finished gathering the pieces, now for the actual matrix
    document_term_matrix = OrderedDict()

    for document_id in documents_list:

        term_weights = list()

        for word in words_list:
            idf = inverse_document_frequencies[word]
            tf = _get_raw_term_frequency(word, document_id, inverted_index)

            tf_idf = round(tf * idf, 3)

            term_weights.append(tf_idf)

        document_term_matrix[document_id] = term_weights

    document_term_dict_file = os.getcwd() + config.get('PATH', 'WRITE')

    with open(document_term_dict_file, "w") as outfile:
        w = csv.writer(outfile, delimiter=";",lineterminator = '\n')

        for key, val in document_term_matrix.items():
            w.writerow([key, val])

    logging.info("\nEnding indexer\n")
    return


if __name__ == "__main__":
    run()
