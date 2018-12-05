import os
import json
import math
import numpy as np

from Variable.BM25_variable import BM25_VAL_K, BM25_VAL_B

current_dir = os.path.dirname(os.path.realpath(__file__))
save_dir_path = os.path.join(current_dir, "..", "..", "save")
table_path = os.path.join(save_dir_path, "table.json")
prev_path = os.path.join(save_dir_path, "prev.json")


def set_search_index(tables, prev):
    while True:
        try:
            with open(table_path, "w") as f:
                json.dump(tables, f)
            break
        except:
            continue

    while True:
        try:
            with open(prev_path, "w") as f:
                json.dump(prev, f)
            break
        except:
            continue


def get_search_index():
    if os.path.exists(table_path):
        with open(table_path, "r") as f:
            tables = json.load(f)
    else:
        tables = dict()

    if os.path.exists(prev_path):
        with open(prev_path, "r") as f:
            prev = json.load(f)
    else:
        prev = {
            "initial_character": dict(),
            "auto_complete": dict(),
            "initial_count": dict()
        }

    return tables, prev


def create_term_document_matrix(idx2term, list_idx2document, idx2document, term_frequency, document_frequency, document_length, average_length):
    document_matrix = np.zeros(dtype=np.float64, shape=(len(idx2document), len(idx2term)))

    distances = np.zeros(dtype=np.float64, shape=(len(idx2document), 1))

    for document in list_idx2document:
        distance = 0
        document_idx2term = list(set([word for word in term_frequency[document]]))
        for term in document_idx2term:
            if term in document_frequency:
                df = len(document_frequency[term])
            else:
                df = 0

            if term in term_frequency[document]:
                tf = term_frequency[document][term]
            else:
                tf = 0

            if document in document_length:
                length = document_length[document] / average_length
            else:
                length = 0

            cal = ((tf * (BM25_VAL_K + 1)) / (tf + (BM25_VAL_K * ((1 - BM25_VAL_B) + BM25_VAL_B * length)))) * math.log(len(idx2document) / df, 10)
            if term in idx2term:
                document_matrix[list_idx2document.index(document)][idx2term.index(term)] = cal
            distance += cal ** 2

        distance = math.sqrt(distance)
        distances[list_idx2document.index(document)][0] = distance

    document_matrix = np.divide(document_matrix, distances, out=np.zeros_like(document_matrix), where=distances != 0)

    return document_matrix


def create_query_matrix(tokenize_query, idx2term, idx2document, document_frequency, average_length, weight):
    query_matrix = np.zeros(dtype=np.float64, shape=(1, len(idx2term)))

    query_idx2term = list(set(tokenize_query))
    distances = np.zeros(dtype=np.float64, shape=(1, 1))
    distance = 0
    for term in query_idx2term:
        if term in idx2term:
            if term in document_frequency:
                df = len(document_frequency[term])
            else:
                df = 0

            tf = tokenize_query.count(term)

            if term in weight:
                tf *= weight[term]

            length = len(tokenize_query) / average_length

            cal = ((tf * (BM25_VAL_K + 1)) / (tf + (BM25_VAL_K * ((1 - BM25_VAL_B) + BM25_VAL_B * length)))) * math.log(len(idx2document) / df, 10)

            query_matrix[0][idx2term.index(term)] = cal
        else:
            cal = 0
        distance += cal ** 2
    distance = math.sqrt(distance)
    distances[0][0] = distance

    query_matrix = np.divide(query_matrix, distances, out=np.zeros_like(query_matrix), where=distances != 0)

    return query_matrix


def create_wordcount_score_matrix(idx2term, list_idx2document, idx2document, term_frequency, document_frequency, document_length, average_length, weight):
    document_score = list()

    for doc_idx in range(len(list_idx2document)):
        score = 0
        for term_idx in range(len(idx2term)):
            df = len(document_frequency[idx2term[term_idx]])
            if idx2term[term_idx] in term_frequency[list_idx2document[doc_idx]]:
                tf = term_frequency[list_idx2document[doc_idx]][idx2term[term_idx]]
            else:
                tf = 0
            if idx2term[term_idx] in weight:
                tf *= weight[idx2term[term_idx]]
            if list_idx2document[doc_idx] in document_length:
                length = document_length[list_idx2document[doc_idx]] / average_length
            else:
                length = 0

            cal = ((tf * (BM25_VAL_K + 1)) / (tf + (BM25_VAL_K * ((1 - BM25_VAL_B) + BM25_VAL_B * length)))) * math.log(len(idx2document) / df, 10)
            score += cal
        document_score.append(score)

    return document_score
