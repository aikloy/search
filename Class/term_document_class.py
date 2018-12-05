import datetime
import numpy as np
# from copy import deepcopy
from joblib import Parallel, delayed

from Class.enum_class import Result
from Class.trie_class import Trie
from Function.InnerFunction.clear_invalid_character_function import clear_invalid_character
from Function.InnerFunction.check_column_function import check_column
from Function.InnerFunction.term_document_function import get_search_index, set_search_index,\
    create_term_document_matrix, create_query_matrix, create_wordcount_score_matrix
from Function.InnerFunction.initial_character_function import convert_to_initial_sentence, find_related_sentences
from Function.InnerFunction.split_char_function import split_char


class TermDocument:
    def __init__(self):
        self._load_info()

    def _load_info(self):
        start_time = datetime.datetime.now()
        self.__tables, self.__prev = get_search_index()
        for index_name in self.__tables:
            self._get_average_length(index_name)
        self.__rewrite_index = set()
        end_time = datetime.datetime.now()

        print("load time :", end_time - start_time)

    def get_synonym(self, index_name):
        if not self.index_exist(index_name):
            return None, Result.INDEX, False
        else:
            synonym = dict()
            for word in self.__tables[index_name]["synonym"]:
                if self.__tables[index_name]["synonym"][word] not in synonym:
                    synonym[self.__tables[index_name]["synonym"][word]] = [word]
                else:
                    synonym[self.__tables[index_name]["synonym"][word]].append(word)
            synonym = [{"keyword": x, "words": synonym[x]} for x in synonym]

            return synonym, None, None

    def insert_synonym(self, index_name, documents):
        if not self.index_exist(index_name):
            return None, Result.INDEX, False
        else:
            document_ids = [x["id"] for x in documents]
            if len(document_ids) != len(set(document_ids)):
                return None, Result.DOCUMENT, True

            def local_insert_synonym(document):
                if self.document_exist(index_name, document["id"]):
                    return document
                else:
                    if not (len(document["words"]) == 1 and document["keyword"] in document["words"]):
                        self.__tables[index_name]["synonym_document"][document["id"]] = document["keyword"]
                        for word in document["words"]:
                            if word != document["keyword"] and word not in self.__tables[index_name]["synonym"]:
                                self.__tables[index_name]["synonym"][word] = document["keyword"]

                    return None

            invalid_documents = Parallel(n_jobs=1)(delayed(local_insert_synonym)(document) for document in documents)

            self.__rewrite_index.add(index_name)
            self._delete_prev(index_name)

            self._rebuild_table(index_name)
            self._get_average_length(index_name)

            if invalid_documents:
                if len(invalid_documents) == len(documents):
                    return None, Result.DOCUMENT, True
                else:
                    return invalid_documents, Result.DOCUMENT, True
            else:
                return True, None, None

    def delete_synonym(self, index_name, document_id):
        if not self.index_exist(index_name):
            return None, Result.INDEX, False
        elif document_id not in self.__tables[index_name]["synonym_document"]:
            return None, Result.DOCUMENT, False
        else:
            synonym_document = [x for x in self.__tables[index_name]["synonym_document"]]
            synonym = [x for x in self.__tables[index_name]["synonym"]]
            if document_id in synonym_document:
                for word in synonym:
                    if self.__tables[index_name]["synonym"][word] == self.__tables[index_name]["synonym_document"][document_id]:
                        del self.__tables[index_name]["synonym"][word]
                del self.__tables[index_name]["synonym_document"][document_id]

            self.__rewrite_index.add(index_name)
            self._delete_prev(index_name)

            self._rebuild_table(index_name)
            self._get_average_length(index_name)

            return True, None, None

    def index_exist(self, index_name):
        if index_name in self.__tables:
            return True
        else:
            return False

    def document_exist(self, index_name, document_id):
        if not self.index_exist(index_name):
            return None, Result.INDEX, False
        elif document_id in self.__tables[index_name]["idx2document"]:
            return True, None, None
        else:
            return False, None, None

    def get_index(self):
        index_list = [index_name for index_name in self.__tables]

        return index_list

    def get_document(self, index_name):
        if not self.index_exist(index_name):
            return None, Result.INDEX, False
        else:
            documents = [x for x in self.__tables[index_name]["idx2document"]]

            return documents, None, None

    def get_document_count(self, index_name):
        if not self.index_exist(index_name):
            return None, Result.INDEX, False
        else:
            result = len(self.__tables[index_name]["idx2document"])

            return result, None, None

    def get_document_by_id(self, index_name, document_id):
        if not self.index_exist(index_name):
            return None, Result.INDEX, False
        elif not self.document_exist(index_name, document_id)[0]:
            return None, Result.DOCUMENT, False
        else:
            return self.__tables[index_name]["idx2document"][document_id], None, None

    def create_index_and_insert_column(self, index_name):
        if self.index_exist(index_name):
            return None, Result.INDEX, True
        else:
            self.__tables[index_name] = dict()
            self.__tables[index_name]["synonym"] = dict()
            self.__tables[index_name]["synonym_document"] = dict()
            self.__tables[index_name]["idx2document"] = dict()

            return True, None, None

    def insert_documents(self, index_name, documents):
        if not self.index_exist(index_name):
            return None, Result.INDEX, False
        else:
            document_ids = [x["id"] for x in documents]
            if len(document_ids) != len(set(document_ids)):
                return None, Result.DOCUMENT, True

            def local_insert_document(document):
                if self.document_exist(index_name, document["id"])[0]:
                    return document
                else:
                    self.__tables[index_name]["idx2document"][document["id"]] = document
                    for key in document:
                        terms = list()
                        if key != "id":
                            if isinstance(document[key], str):
                                terms.extend([clear_invalid_character(word) for word in document[key].split()])
                            elif isinstance(document[key], list):
                                for val in document[key]:
                                    if isinstance(val, str):
                                        terms.extend([clear_invalid_character(word) for word in val.split()])

                        if terms:
                            if key not in self.__tables[index_name]:
                                self.__tables[index_name][key] = dict()
                            if "term_frequency" not in self.__tables[index_name][key]:
                                self.__tables[index_name][key]["term_frequency"] = dict()
                            if "document_frequency" not in self.__tables[index_name][key]:
                                self.__tables[index_name][key]["document_frequency"] = dict()
                            if "document_length" not in self.__tables[index_name][key]:
                                self.__tables[index_name][key]["document_length"] = dict()
                            if "average_length" not in self.__tables[index_name][key]:
                                self.__tables[index_name][key]["average_length"] = None

                            self.__tables[index_name][key]["document_length"][document["id"]] = len(terms)

                        for term in terms:
                            if document["id"] not in self.__tables[index_name][key]["term_frequency"]:
                                self.__tables[index_name][key]["term_frequency"][document["id"]] = dict()
                            if term not in self.__tables[index_name][key]["term_frequency"][document["id"]]:
                                self.__tables[index_name][key]["term_frequency"][document["id"]][term] = 1
                            else:
                                self.__tables[index_name][key]["term_frequency"][document["id"]][term] += 1
                            if term not in self.__tables[index_name][key]["document_frequency"]:
                                self.__tables[index_name][key]["document_frequency"][term] = list()
                            if document["id"] not in self.__tables[index_name][key]["document_frequency"][term]:
                                self.__tables[index_name][key]["document_frequency"][term].append(document["id"])

                    return None

            invalid_documents = Parallel(n_jobs=1)(delayed(local_insert_document)(document) for document in documents)

            self._get_average_length(index_name)
            self.__rewrite_index.add(index_name)
            self._delete_prev(index_name)

            if invalid_documents:
                if len(invalid_documents) == len(documents):
                    return None, Result.DOCUMENT, True
                else:
                    return invalid_documents, Result.DOCUMENT, True
            else:
                return True, None, None

    def _rebuild_table(self, index_name):
        # synonym, synonym_document, idx2document = deepcopy(self.__tables[index_name]["synonym"]), deepcopy(self.__tables[index_name]["synonym_document"]), deepcopy(self.__tables[index_name]["idx2document"])
        new_tables = dict()
        new_tables["synonym"] = self.__tables[index_name]["synonym"]
        new_tables["synonym_document"] = self.__tables[index_name]["synonym_document"]
        new_tables["idx2document"] = self.__tables[index_name]["idx2document"]
        self.__tables[index_name] = new_tables
        # self.__tables[index_name] = dict()
        # self.__tables[index_name]["synonym"] = synonym
        # self.__tables[index_name]["synonym_document"] = synonym_document
        # self.__tables[index_name]["idx2document"] = idx2document

        def local_rebuild_tables(document_id):
            for key in self.__tables[index_name]["idx2document"][document_id]:
                terms = list()
                if key != "id":
                    if isinstance(self.__tables[index_name]["idx2document"][document_id][key], str):
                        terms.extend([clear_invalid_character(word) for word in self.__tables[index_name]["idx2document"][document_id][key].split()])
                    elif isinstance(self.__tables[index_name]["idx2document"][document_id][key], list):
                        for val in self.__tables[index_name]["idx2document"][document_id][key]:
                            if isinstance(val, str):
                                terms.extend([clear_invalid_character(word) for word in val.split()])

                if terms:
                    if key not in self.__tables[index_name]:
                        self.__tables[index_name][key] = dict()
                    if "term_frequency" not in self.__tables[index_name][key]:
                        self.__tables[index_name][key]["term_frequency"] = dict()
                    if "document_frequency" not in self.__tables[index_name][key]:
                        self.__tables[index_name][key]["document_frequency"] = dict()
                    if "document_length" not in self.__tables[index_name][key]:
                        self.__tables[index_name][key]["document_length"] = dict()
                    if "average_length" not in self.__tables[index_name][key]:
                        self.__tables[index_name][key]["average_length"] = None

                    self.__tables[index_name][key]["document_length"][document_id] = len(terms)

                for term in terms:
                    if document_id not in self.__tables[index_name][key]["term_frequency"]:
                        self.__tables[index_name][key]["term_frequency"][document_id] = dict()
                    if term not in self.__tables[index_name][key]["term_frequency"][document_id]:
                        self.__tables[index_name][key]["term_frequency"][document_id][term] = 1
                    else:
                        self.__tables[index_name][key]["term_frequency"][document_id][term] += 1
                    if term not in self.__tables[index_name][key]["document_frequency"]:
                        self.__tables[index_name][key]["document_frequency"][term] = list()
                    if document_id not in self.__tables[index_name][key]["document_frequency"][term]:
                        self.__tables[index_name][key]["document_frequency"][term].append(document_id)

        Parallel(n_jobs=1)(delayed(local_rebuild_tables)(document_id) for document_id in self.__tables[index_name]["idx2document"])

    def update_document(self, index_name, document_id, document):
        if not self.index_exist(index_name):
            return None, Result.INDEX, False
        elif not self.document_exist(index_name, document_id)[0]:
            return None, Result.DOCUMENT, False
        elif self.document_exist(index_name, document["id"])[0] and document_id != document["id"]:
            return None, Result.DOCUMENT, True
        else:
            del self.__tables[index_name]["idx2document"][document_id]
            self.__tables[index_name]["idx2document"][document["id"]] = document
            self._rebuild_table(index_name)
            self._get_average_length(index_name)

            self.__rewrite_index.add(index_name)
            self._delete_prev(index_name)

            return True, None, None

    def drop_index(self, index_name):
        if not self.index_exist(index_name):
            return None, Result.INDEX, False
        else:
            del self.__tables[index_name]

            self.__rewrite_index.add(index_name)
            self._delete_prev(index_name)

            return True, None, None

    def delete_document(self, index_name, document_id):
        if not self.index_exist(index_name):
            return None, Result.INDEX, False
        elif not self.document_exist(index_name, document_id):
            return None, Result.DOCUMENT, False
        else:
            del self.__tables[index_name]["idx2document"][document_id]

            self._rebuild_table(index_name)
            self._get_average_length(index_name)

            self.__rewrite_index.add(index_name)
            self._delete_prev(index_name)

            return True, None, None

    def _delete_prev(self, index_name):
        for key in self.__prev:
            if index_name in self.__prev[key]:
                del self.__prev[key][index_name]

    def _get_average_length(self, index_name):
        for column_name in self.__tables[index_name]:
            if "document_length" in self.__tables[index_name][column_name]:
                self.__tables[index_name][column_name]["average_length"] = sum([val for val in self.__tables[index_name][column_name]["document_length"].values()]) / len(self.__tables[index_name]["idx2document"])

    def save_tables(self):
        start_time = datetime.datetime.now()

        set_search_index(self.__tables, self.__prev)

        end_time = datetime.datetime.now()

        print("save time :", end_time - start_time)

    def _search_pre_process(self, index_name, column_list, query):
        tokenize_query = query.strip().split()
        for i in range(len(tokenize_query)):
            if tokenize_query[i] in self.__tables[index_name]["synonym"]:
                tokenize_query[i] = self.__tables[index_name]["synonym"][tokenize_query[i]]

        term_set = set(tokenize_query)
        idx2term = list()
        for column_name in column_list:
            for term in term_set:
                if term not in idx2term and term in self.__tables[index_name][column_name]["document_frequency"]:
                    idx2term.append(term)

        idx2document = self.__tables[index_name]["idx2document"]
        term_frequency, document_frequency, document_length, average_length = dict(), dict(), dict(), None
        for column_name in column_list:
            for document in idx2document:
                if document not in term_frequency:
                    term_frequency[document] = dict()
                if document in self.__tables[index_name][column_name]["term_frequency"]:
                    for term in self.__tables[index_name][column_name]["term_frequency"][document]:
                        if term not in term_frequency[document]:
                            term_frequency[document][term] = self.__tables[index_name][column_name]["term_frequency"][document][term]
                        else:
                            term_frequency[document][term] += self.__tables[index_name][column_name]["term_frequency"][document][term]

                if document in self.__tables[index_name][column_name]["document_length"]:
                    if document not in document_length:
                        document_length[document] = self.__tables[index_name][column_name]["document_length"][document]
                    else:
                        document_length[document] += self.__tables[index_name][column_name]["document_length"][document]

            for term in self.__tables[index_name][column_name]["document_frequency"]:
                if term not in document_frequency:
                    document_frequency[term] = list()
                for document_id in self.__tables[index_name][column_name]["document_frequency"][term]:
                    if document_id not in document_frequency[term]:
                        document_frequency[term].append(document_id)

            if average_length is None:
                average_length = self.__tables[index_name][column_name]["average_length"]
            else:
                average_length += self.__tables[index_name][column_name]["average_length"]

        list_idx2document = [key for key in idx2document]

        return tokenize_query, idx2term, list_idx2document, idx2document, term_frequency, document_frequency, document_length, average_length

    def find_sentence_by_initial(self, index_name, column_names, query):
        if not self.index_exist(index_name):
            return None, Result.INDEX, False
        elif not check_column(self.__tables[index_name]["idx2document"].values(), column_names):
            return None, Result.COLUMN, False
        else:
            query = "".join(query.strip().split())

            column_key = ",".join(column_names)

            if index_name not in self.__prev["initial_character"] or (index_name in self.__prev["initial_character"] and column_key not in self.__prev["initial_character"][index_name]):
                sentences = dict()
                for column_name in column_names:
                    for document in self.__tables[index_name]["idx2document"].values():
                        if isinstance(document[column_name], list):
                            for val in document[column_name]:
                                initial_sentence = convert_to_initial_sentence(val)
                                if initial_sentence not in sentences:
                                    sentences[initial_sentence] = val
                        elif isinstance(document[column_name], str):
                            initial_sentence = convert_to_initial_sentence(document[column_name])
                            if initial_sentence not in sentences:
                                sentences[initial_sentence] = document[column_name]

                if index_name not in self.__prev["initial_character"]:
                    self.__prev["initial_character"][index_name] = dict()
                self.__prev["initial_character"][index_name][column_key] = sentences
            else:
                sentences = self.__prev["initial_character"][index_name][column_key]

            answer = find_related_sentences(query, sentences)

            return answer, None, None

    def get_initial_count(self, index_name, column_names):
        if not self.index_exist(index_name):
            return None, Result.INDEX, False
        elif not check_column(self.__tables[index_name]["idx2document"].values(), column_names):
            return None, Result.COLUMN, False
        else:
            column_key = ",".join(column_names)

            if index_name not in self.__prev["initial_count"] or (index_name in self.__prev["initial_count"] and column_key not in self.__prev["initial_count"][index_name]):
                sentences = dict()
                for column_name in column_names:
                    for document in self.__tables[index_name]["idx2document"].values():
                        if isinstance(document[column_name], list):
                            for val in document[column_name]:
                                initial_sentence = convert_to_initial_sentence(val)
                                if initial_sentence[0] not in sentences:
                                    sentences[initial_sentence[0]] = 1
                                else:
                                    sentences[initial_sentence[0]] += 1
                        elif isinstance(document[column_name], str):
                            initial_sentence = convert_to_initial_sentence(document[column_name])
                            if initial_sentence[0] not in sentences:
                                sentences[initial_sentence[0]] = 1
                            else:
                                sentences[initial_sentence[0]] += 1

                if index_name not in self.__prev["initial_count"]:
                    self.__prev["initial_count"][index_name] = dict()
                self.__prev["initial_count"][index_name][column_key] = sentences
            else:
                sentences = self.__prev["initial_count"][index_name][column_key]

            return sentences, None, None

    def auto_complete(self, index_name, column_names, query):
        if not self.index_exist(index_name):
            return None, Result.INDEX, False
        elif not check_column(self.__tables[index_name]["idx2document"].values(), column_names):
            return None, Result.COLUMN, False
        else:
            query = split_char(query)

            column_key = ",".join(column_names)

            if index_name not in self.__prev["auto_complete"] or (index_name in self.__prev["auto_complete"] and column_key not in self.__prev["auto_complete"][index_name]):
                sentences = dict()
                for column_name in column_names:
                    for document in self.__tables[index_name]["idx2document"].values():
                        if isinstance(document[column_name], list):
                            for val in document[column_name]:
                                if isinstance(val, str):
                                    initial_sentence = split_char(val)
                                    if initial_sentence not in sentences:
                                        sentences[initial_sentence] = val
                        elif isinstance(document[column_name], str):
                            initial_sentence = split_char(document[column_name])
                            if initial_sentence not in sentences:
                                sentences[initial_sentence] = document[column_name]

                if index_name not in self.__prev["auto_complete"]:
                    self.__prev["auto_complete"][index_name] = dict()
                self.__prev["auto_complete"][index_name][column_key] = Trie()
                self.__prev["auto_complete"][index_name][column_key].create(sentences)

            answer = self.__prev["auto_complete"][index_name][column_key].search(query)

            return answer, None, None

    def search_with_cosine_similarity(self, index_name, column_list, query, weight):
        if not self.index_exist(index_name):
            return None, Result.INDEX, False
        else:
            if False in [x in self.__tables[index_name] for x in column_list]:
                return None, Result.COLUMN, False
            else:
                tokenize_query, idx2term, list_idx2document, idx2document, term_frequency, document_frequency, document_length, average_length = self._search_pre_process(index_name, column_list, query)

                document_matrix = create_term_document_matrix(idx2term, list_idx2document, idx2document, term_frequency, document_frequency, document_length, average_length)
                query_matrix = create_query_matrix(tokenize_query, idx2term, idx2document, document_frequency, average_length, weight)
                document_matrix = np.transpose(document_matrix)

                similarity = np.matmul(query_matrix, document_matrix).reshape((len(idx2document), )).tolist()

                document_similarity = list()
                for doc, val in zip(list_idx2document, similarity):
                    if val > 0:
                        document_similarity.append({"document": idx2document[doc], "score": val})
                document_similarity.sort(key=lambda x: x["score"], reverse=True)

                return document_similarity, None, None

    def search_with_word_count(self, index_name, column_list, query, weight):
        if not self.index_exist(index_name):
            return None, Result.INDEX, False
        else:
            if False in [x in self.__tables[index_name] for x in column_list]:
                return None, Result.COLUMN, False
            else:
                tokenize_query, idx2term, list_idx2document, idx2document, term_frequency, document_frequency, document_length, average_length = self._search_pre_process(index_name, column_list, query)

                document_matrix = create_wordcount_score_matrix(idx2term, list_idx2document, idx2document, term_frequency, document_frequency, document_length, average_length, weight)
                document_similarity = list()
                for doc, val in zip(list_idx2document, document_matrix):
                    if val > 0:
                        document_similarity.append({"document": idx2document[doc], "score": val})
                document_similarity.sort(key=lambda x: x["score"], reverse=True)

                return document_similarity, None, None
