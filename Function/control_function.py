from Class.term_document_class import TermDocument


def load_matrix():
    tdm = TermDocument()

    return tdm


def check_index_exist(tdm, index_name):
    answer = tdm.index_exist(index_name)

    return answer


def check_doc_exist(tdm, index_name, doc_id):
    answer = tdm.document_exist(index_name, doc_id)

    return answer


def get_index(tdm):
    index_names = tdm.get_index()

    return index_names


def get_document(tdm, index_name):
    content, target, result = tdm.get_document(index_name)

    return content, target, result


def get_document_count(tdm, index_name):
    content, target, result = tdm.get_document_count(index_name)

    return content, target, result


def get_document_by_id(tdm, index_name, document_id):
    content, target, result = tdm.get_document_by_id(index_name, document_id)

    return content, target, result


def create_index_and_insert_column(tdm, index_name):
    content, target, result = tdm.create_index_and_insert_column(index_name)

    return content, target, result


def get_synonym(tdm, index_name):
    content, target, result = tdm.get_synonym(index_name)

    return content, target, result


def insert_synonym(tdm, index_name, documents):
    content, target, result = tdm.insert_synonym(index_name, documents)

    return content, target, result


def delete_synonym(tdm, index_name, document_id):
    content, target, result = tdm.delete_synonym(index_name, document_id)

    return content, target, result


def insert_documents(tdm, index_name, documents):
    content, target, result = tdm.insert_documents(index_name, documents)

    return content, target, result


def update_document(tdm, index_name, document_id, document):
    content, target, result = tdm.update_document(index_name, document_id, document)

    return content, target, result


def delete_document(tdm, index_name, document_id):
    content, target, result = tdm.delete_document(index_name, document_id)

    return content, target, result


def drop_index(tdm, index_name):
    content, target, result = tdm.drop_index(index_name)

    return content, target, result


def delete_column(tdm, index_name, column_name):
    content, target, result = tdm.delete_column(index_name, column_name)

    return content, target, result


def find_sentence_by_initial(tdm, index_name, column_names, query):
    content, target, result = tdm.find_sentence_by_initial(index_name, column_names, query)

    return content, target, result


def get_initial_count(tdm, index_name, column_names):
    content, target, result = tdm.get_initial_count(index_name, column_names)

    return content, target, result


def auto_complete(tdm, index_name, column_names, query):
    content, target, result = tdm.auto_complete(index_name, column_names, query)

    return content, target, result


def search_with_cosine_similarity(tdm, index_name, column_name, query, weight):
    content, target, result = tdm.search_with_cosine_similarity(index_name, column_name, query, weight)

    return content, target, result


def search_with_word_count(tdm, index_name, column_name, query, weight):
    content, target, result = tdm.search_with_word_count(index_name, column_name, query, weight)

    return content, target, result


def save_data_scheduler(tdm):
    tdm.save_tables()
