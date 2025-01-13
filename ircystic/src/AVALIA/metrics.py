import os
from collections import OrderedDict
import csv
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


# return pairs (recall,precision), one for each recall point provided
def calculate_points(sorted_expected_results, sorted_actual_results):
    recall_points = [0.0, 0.1, 0.2, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    # list of pairs
    pairs = list()

    for recall_point in recall_points:
        # qual é a precisão do algoritmo se só considerarmos
        #   a proporção dada dos documentos relevantes retornados?

        new_pair = [recall_point]

        precisions_at_recall_point = list()

        for query_id, expected_document_ids in sorted_expected_results.items():
            expected_results_for_query = expected_document_ids
            actual_results_for_query = sorted_actual_results[query_id]

            precision = _precision_at_recall_point(
                expected_results_for_query,
                actual_results_for_query,
                recall_point)

            precisions_at_recall_point.append(precision)

        # the y-value is the average precision at point recall_point
        # over all queries
        average_precisions = sum(precisions_at_recall_point) / len(precisions_at_recall_point)

        new_pair.append(average_precisions)
        pairs.append(new_pair)

    return (pairs)


# data uma lista de ids esperados e uma lista de ids recuperados, retorna a precisão
#   se só considerarmos o recall_point dado. Se o recall_point for 1.0, então o resultado
#   é a precisão normal
def _precision_at_recall_point(sorted_expected_doc_ids, sorted_actual_doc_ids, recall_point):
    assert (isinstance(recall_point, float))

    # recall_point is given as a normalized proportion (from 0.0 to 1.0)
    recall_threshold = int(len(sorted_expected_doc_ids) * recall_point)

    # this is a little hack so as not to get division by zeros
    # this is the minimum recall, so maximum precision
    if recall_threshold == 0:
        recall_threshold = 1

    # what precision do I get if we only consider the first <recall_threshold>
    #   expected results?
    precision = _get_precision_at_absolute_recall(
        sorted_expected_doc_ids,
        sorted_actual_doc_ids,
        recall_threshold)

    return (precision)


# returns an ordered dict[int,list[int]]
def load_from_csv_file(path_to_file):
    # ordered dict so as to keep the same order and avoid 'surprises'
    data = OrderedDict()

    with open(path_to_file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        for row in reader:
            query_id = int(row[0].strip())

            if isinstance(row[1], list):
                # doc ids
                value = map(lambda str: int(str.strip("'")), row[1].lstrip('[').rstrip(']').split(','))

            elif isinstance(row[1], str):
                # just a string
                value = row[1].strip()
            else:
                raise RuntimeError("Csv file at '{0}' does not fit expected structure for parsing".format(path_to_file))

            data[query_id] = value

    return (data)


def _get_precision_at_absolute_recall(expected_results, actual_results, absolute_threshold):
    hits = 0
    total = 0

    for idx, actual_id in enumerate(actual_results):
        if hits >= absolute_threshold:
            return (hits / total)
        # if idx > absolute_threshold:
        #     # this will cause a threshold of 0 to return 1.0, which makes sense
        #     #  because minimum recall equals maximum precision, which is 1.0
        #     return(running_precision)
        if actual_id in expected_results:
            hits += 1
            total += 1
        else:
            total += 1

    return (hits / total)


def plot_recall_precision_curve(recall_precision_pairs,
                                title='Precision-Recall curve (11 pts)',
                                display=False,
                                color='b',
                                filename=None):
    if not display:
        assert (filename is not None)

    recalls = list(map(lambda el: round(el[0], 2), recall_precision_pairs))
    precisions = list(map(lambda el: round(el[1], 3), recall_precision_pairs))

    plt.plot(recalls, precisions, "{0}o-".format(color), label=title)
    plt.gca().xaxis.grid(True, which='major')
    plt.gca().yaxis.grid(True)
    plt.gca().set_xticks([0.0, 0.1, 0.2, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])

    for i, j in zip(recalls, precisions):
        label = "({0},{1})".format(i, j)

        textpos = _get_text_pos(i, j)

        plt.annotate(label,
                     xy=(i, j),
                     weight=10,
                     arrowprops=dict(
                         arrowstyle="->",
                         connectionstyle="arc3"),
                     xytext=textpos)

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.legend(loc="upper right")

    if (display):
        plt.show()
    else:
        plt.savefig(filename)


def _get_text_pos(i, j, x_text_delta=0.0, y_text_delta=0.0):
    if int(i * 10) % 2 == 0:
        y_text_delta = 0.05
    else:
        y_text_delta = 0.2

    return ((i + x_text_delta, j + y_text_delta))

if __name__ == "__main__":
    filename = os.getcwd() + '/output/search_processor/esperados.csv'
    expected_results = load_from_csv_file(filename)

    filename = os.getcwd() + '/output/result/search_result_no_stemmer.csv'
    #filename = os.getcwd() + '/output/result/search_result.csv'
    actual_results = load_from_csv_file(filename)
    precision_11_points = calculate_points(expected_results, actual_results)
    outputfilename = os.getcwd() + '/AVALIA/11pontos-NO_stemmer-.png'

    plot_recall_precision_curve(
        precision_11_points,
        title="Precision-Recall curve",
        display=False,
        filename = os.getcwd() + '/AVALIA/precision_11_points_NO_stemmer.png')