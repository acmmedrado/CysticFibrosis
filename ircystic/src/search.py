import logging
import glob
import os
import configparser
import csv
import numpy as np
from collections import OrderedDict
from scipy import spatial

"""
This code aims to calculate search results based on a model saved previously
"""

# LOG format Configurations
FORMAT = '%(asctime)s %(levelname)s: %(message)s'
DATEFMT = '%d %b %H:%M:%S'
list_of_files = glob.glob('/log/*.log')  # * means all if need specific format
latest_file = max(list_of_files, key=os.path.getctime)
logging.basicConfig(filename=latest_file, level=logging.INFO, format=FORMAT, datefmt=DATEFMT, filemode="a")

def cosine_distance(npvector1, npvector2):
    return (spatial.distance.cosine(npvector1, npvector2))


def get_position(id, doc_distance_pairs):
    idx = 1  # 1-indexed

    for pair in doc_distance_pairs:
        doc_id = pair[0]
        if int(doc_id) == int(id):
            return (idx)
        else:
            idx += 1

    # if it's reached here, then given id couldn't be found in the results
    raise RuntimeError("Failed to find {0} in query results".format(id))


def run(params={}):
    configFile = os.getcwd() + '/ircystic/src/config/busca.cfg'
    config = configparser.ConfigParser()
    config.read(configFile)


    outputFileParam = os.getcwd() + config.get('PATH', 'RESULTADOS')

    # loading model
    modeloFile = os.getcwd() + config.get('PATH', 'MODELO')
    docs_dict = OrderedDict()
    with open(modeloFile, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            doc_id = int(row[0])
            token_vector = row[1].lstrip('[').rstrip(']').split(',')
            docs_dict[doc_id] = np.asarray(list(map(float, token_vector)))

    # loading queries
    consultasFile = os.getcwd() + config.get('PATH', 'CONSULTAS_VECTOR')
    queries_dict = OrderedDict()
    with open(consultasFile, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            query_id = int(row[0])
            token_vector = row[1].lstrip('[').rstrip(']').split(',')
            queries_dict[query_id] = np.asarray(list(map(float, token_vector)))


    with open(outputFileParam, 'w') as csvfile:
        resultsWriter = csv.writer(csvfile, delimiter=';', lineterminator='\n')
        resultsWriter.writerow(['idConsulta', 'Resultado'])

        # calculating results
        # one result line per query
        for query_id, query_vector in queries_dict.items():
            results_row = list()
            results_row.append(query_id)

            doc_distance_pairs = list()

            for doc_id, doc_vector in docs_dict.items():

                distance = cosine_distance(query_vector, doc_vector)
                doc_distance_pairs.append([doc_id, distance])

            # this is the way data will be written to the csv file
            position_doc_distance_triples = list()

            sorted_doc_distance_pairs = sorted(doc_distance_pairs, key=lambda elem: elem[1])

            for i, pair in enumerate(sorted_doc_distance_pairs, start=1):
                doc_id = pair[0]
                distance = pair[1]

                # 1-indexed
                position = i

                if (float(distance) == 1.0):
                    continue

                position_doc_distance_triples.append([position, doc_id, round(distance, 3)])
                # writing results
                # one result line per query
                resultsWriter.writerow([query_id, [position, doc_id, round(distance, 3)]])

            # highest score first so we can compare more easily with the expect results
            sorted_doc_distance_pairs = sorted(position_doc_distance_triples, key=lambda elem: elem[0])

            results_row.append(position_doc_distance_triples)



if __name__ == "__main__":
    logging.info("\nBeginning search module run\n")
    run()
    logging.info("\nEnding search module run\n")
