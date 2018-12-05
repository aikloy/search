import os
import argparse
from flask import Flask, request, make_response
from flask_restplus import Resource, Api, fields
from apscheduler.schedulers.background import BackgroundScheduler

from Class.enum_class import Result
from Function.InnerFunction.get_request_function import get_request
from Variable.request_variable import RESPONSE_OK, RESPONSE_OK_WITH_NO_CONTENT, RESPONSE_INVALID_INPUT, RESPONSE_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR,\
    INDEX_ALREADY_EXIST, INDEX_NOT_EXIST, COLUMN_ALREADY_EXIST, COLUMN_NOT_EXIST, DOCUMENT_ALREADY_EXIST, DOCUMENT_NOT_EXIST,\
    POST_INDEX_CONTROL_AND_INSERT_DOCUMENT, POST_REBUILD_SYNONYM, DELETE_REBUILD_SYNONYM, PUT_CONTROL_DOCUMENT, SEARCH_INITIAL_CHARACTER, AUTO_COMPLETE, SEARCH_COSINE_SIMILARITY, SEARCH_WORD_COUNT
from Function.control_function import load_matrix,\
    check_index_exist, check_doc_exist,\
    get_index, get_document, get_document_count, get_document_by_id,\
    create_index_and_insert_column, insert_documents, get_synonym, insert_synonym, delete_synonym,\
    update_document,\
    drop_index, delete_document,\
    save_data_scheduler,\
    find_sentence_by_initial, get_initial_count, auto_complete, search_with_cosine_similarity, search_with_word_count

parser = argparse.ArgumentParser()
parser.add_argument("--host", type=str, action="store", required=False, default="0.0.0.0", help="flask host")
parser.add_argument("--port", type=int, action="store", required=False, default=12001, help="flask port")
parser.add_argument("--scheduler_time", type=int, action="store", required=False, default=600, help="scheduler time (seconds)")

args = parser.parse_args()
current_dir_path = os.path.dirname(os.path.realpath(__file__))

application = Flask(__name__)
api = Api(application, default="Search", doc="/Search/Swagger/", title="Search API", description="Search API")
TDM = load_matrix()

##################################################################################################################################

namespace = api.namespace("Search/<index_name>/exist", description="index 존재여부 확인")


@namespace.route("")
class CheckIndexExist(Resource):
    @staticmethod
    def get(index_name):
        result = check_index_exist(TDM, index_name)

        return result, RESPONSE_OK


##################################################################################################################################

namespace = api.namespace("Search/<index_name>/<document_id>/exist", description="document 존재여부 확인")


@namespace.route("")
class CheckDocumentExist(Resource):
    @staticmethod
    def get(index_name, document_id):
        content, target, result = check_doc_exist(TDM, index_name, document_id)
        if content is not None:
            return content, RESPONSE_OK
        else:
            if target == Result.INDEX:
                if result is True:
                    return INDEX_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return INDEX_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            elif target == Result.COLUMN:
                if result is True:
                    return COLUMN_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return COLUMN_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            elif target == Result.DOCUMENT:
                if result is True:
                    return DOCUMENT_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return DOCUMENT_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            else:
                return None, RESPONSE_INTERNAL_ERROR


##################################################################################################################################

namespace = api.namespace("Search/index", description="존재하는 index 가져오기")


@namespace.route("")
class GetAllIndex(Resource):
    @staticmethod
    def get():
        result = get_index(TDM)
        if result:
            return result, RESPONSE_OK
        else:
            resp = make_response('', RESPONSE_OK_WITH_NO_CONTENT)
            resp.headers['Content-Length'] = 0

            return resp


##################################################################################################################################

namespace = api.namespace("Search/<index_name>/document", description="특정 index에 존재하는 document 가져오기")


@namespace.route("")
class GetAllDocument(Resource):
    @staticmethod
    def get(index_name):
        content, target, result = get_document(TDM, index_name)
        if content is not None:
            if content:
                return content, RESPONSE_OK
            else:
                resp = make_response('', RESPONSE_OK_WITH_NO_CONTENT)
                resp.headers['Content-Length'] = 0

                return resp
        else:
            if target == Result.INDEX:
                if result is True:
                    return INDEX_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return INDEX_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            elif target == Result.COLUMN:
                if result is True:
                    return COLUMN_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return COLUMN_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            elif target == Result.DOCUMENT:
                if result is True:
                    return DOCUMENT_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return DOCUMENT_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            else:
                return None, RESPONSE_INTERNAL_ERROR


##################################################################################################################################

namespace = api.namespace("Search/<index_name>/document/count", description="특정 index에 존재하는 document의 개수 가져오기")


@namespace.route("")
class GetDocumentCount(Resource):
    @staticmethod
    def get(index_name):
        content, target, result = get_document_count(TDM, index_name)
        if content is not None:
            return content, RESPONSE_OK
        else:
            if target == Result.INDEX:
                if result is True:
                    return INDEX_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return INDEX_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            elif target == Result.COLUMN:
                if result is True:
                    return COLUMN_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return COLUMN_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            elif target == Result.DOCUMENT:
                if result is True:
                    return DOCUMENT_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return DOCUMENT_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            else:
                return None, RESPONSE_INTERNAL_ERROR


##################################################################################################################################

namespace = api.namespace("Search/<index_name>", description="index 생성/삭제 및 document 추가")


@namespace.route("")
class IndexControlAndInsertDocument(Resource):
    @staticmethod
    @api.expect([
        api.model("Document", {"id": fields.String(required=False)})
    ])
    def post(index_name):
        request_body = get_request(request)
        if isinstance(request_body, list):
            for doc in request_body:
                if "id" not in doc:
                    return POST_INDEX_CONTROL_AND_INSERT_DOCUMENT, RESPONSE_INVALID_INPUT

            content, target, result = insert_documents(TDM, index_name, request_body)
            if target is None:
                return content, RESPONSE_OK
            else:
                if target == Result.INDEX:
                    if result is True:
                        return INDEX_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return INDEX_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.COLUMN:
                    if result is True:
                        return COLUMN_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return COLUMN_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.DOCUMENT:
                    if result is True:
                        if content:
                            return DOCUMENT_ALREADY_EXIST, RESPONSE_OK
                        else:
                            return DOCUMENT_ALREADY_EXIST, RESPONSE_ALREADY_EXIST
                    else:
                        return DOCUMENT_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return None, RESPONSE_INTERNAL_ERROR
        else:
            content, target, result = create_index_and_insert_column(TDM, index_name)
            if content is not None:
                return content, RESPONSE_OK
            else:
                if target == Result.INDEX:
                    if result is True:
                        return INDEX_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return INDEX_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.COLUMN:
                    if result is True:
                        return COLUMN_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return COLUMN_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.DOCUMENT:
                    if result is True:
                        return DOCUMENT_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return DOCUMENT_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return None, RESPONSE_INTERNAL_ERROR

    @staticmethod
    def delete(index_name):
        content, target, result = drop_index(TDM, index_name)
        if content is not None:
            return content, RESPONSE_OK
        else:
            if target == Result.INDEX:
                if result is True:
                    return INDEX_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return INDEX_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            elif target == Result.COLUMN:
                if result is True:
                    return COLUMN_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return COLUMN_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            elif target == Result.DOCUMENT:
                if result is True:
                    return DOCUMENT_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return DOCUMENT_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            else:
                return None, RESPONSE_INTERNAL_ERROR


##################################################################################################################################

namespace = api.namespace("Search/<index_name>/synonym", description="synonym 정보 가져오기/추가/삭제")


@namespace.route("")
class RebuildSynonym(Resource):
    @staticmethod
    def get(index_name):
        content, target, result = get_synonym(TDM, index_name)
        if content is not None:
            if content:
                return content, RESPONSE_OK
            else:
                resp = make_response('', RESPONSE_OK_WITH_NO_CONTENT)
                resp.headers['Content-Length'] = 0

                return resp
        else:
            if target == Result.INDEX:
                if result is True:
                    return INDEX_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return INDEX_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            elif target == Result.COLUMN:
                if result is True:
                    return COLUMN_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return COLUMN_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            elif target == Result.DOCUMENT:
                if result is True:
                    return DOCUMENT_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return DOCUMENT_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            else:
                return None, RESPONSE_INTERNAL_ERROR

    @staticmethod
    @api.expect([api.model("SynonymDocument", {
        "id": fields.String,
        "keyword": fields.String,
        "words": fields.List(fields.String)
    })])
    def post(index_name):
        request_body = get_request(request)
        if isinstance(request_body, list):
            for doc in request_body:
                if not ("id" in doc and isinstance(doc["id"], str) and "keyword" in doc and isinstance(doc["keyword"], str) and "words" in doc and isinstance(doc["words"], list)):
                    return POST_REBUILD_SYNONYM, RESPONSE_INVALID_INPUT
                else:
                    for word in doc["words"]:
                        if not isinstance(word, str):
                            return POST_REBUILD_SYNONYM, RESPONSE_INVALID_INPUT

            content, target, result = insert_synonym(TDM, index_name, request_body)

            if target is None:
                if content:
                    return content, RESPONSE_OK
                else:
                    resp = make_response('', RESPONSE_OK_WITH_NO_CONTENT)
                    resp.headers['Content-Length'] = 0

                    return resp
            else:
                if target == Result.INDEX:
                    if result is True:
                        return INDEX_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return INDEX_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.COLUMN:
                    if result is True:
                        return COLUMN_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return COLUMN_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.DOCUMENT:
                    if result is True:
                        if content:
                            return DOCUMENT_ALREADY_EXIST, RESPONSE_OK
                        else:
                            return DOCUMENT_ALREADY_EXIST, RESPONSE_ALREADY_EXIST
                    else:
                        return DOCUMENT_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return None, RESPONSE_INTERNAL_ERROR
        else:
            return POST_REBUILD_SYNONYM, RESPONSE_INVALID_INPUT

    @staticmethod
    @api.expect(api.model("RebuildSynonymDelete", {
        "document_id": fields.String
    }))
    def delete(index_name):
        request_body = get_request(request)
        if "document_id" in request_body and isinstance(request_body["document_id"], str):
            content, target, result = delete_synonym(TDM, index_name, request_body["document_id"])

            if content is not None:
                if content:
                    return content, RESPONSE_OK
                else:
                    resp = make_response('', RESPONSE_OK_WITH_NO_CONTENT)
                    resp.headers['Content-Length'] = 0

                    return resp
            else:
                if target == Result.INDEX:
                    if result is True:
                        return INDEX_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return INDEX_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.COLUMN:
                    if result is True:
                        return COLUMN_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return COLUMN_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.DOCUMENT:
                    if result is True:
                        return DOCUMENT_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return DOCUMENT_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return None, RESPONSE_INTERNAL_ERROR
        else:
            return DELETE_REBUILD_SYNONYM, RESPONSE_INVALID_INPUT


##################################################################################################################################

namespace = api.namespace("Search/<index_name>/<document_id>", description="document 가져오기/수정/삭제")


@namespace.route("")
class ControlDocument(Resource):
    @staticmethod
    def get(index_name, document_id):
        content, target, result = get_document_by_id(TDM, index_name, document_id)
        if content is not None:
            return content, RESPONSE_OK
        else:
            if target == Result.INDEX:
                if result is True:
                    return INDEX_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return INDEX_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            elif target == Result.COLUMN:
                if result is True:
                    return COLUMN_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return COLUMN_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            elif target == Result.DOCUMENT:
                if result is True:
                    return DOCUMENT_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return DOCUMENT_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            else:
                return None, RESPONSE_INTERNAL_ERROR

    @staticmethod
    @api.expect([api.model("UpdateDocument", {
        "id": fields.String
    })])
    def put(index_name, document_id):
        request_body = get_request(request)
        if "id" in request_body and isinstance(request_body["id"], str):
            content, target, result = update_document(TDM, index_name, document_id, request_body)
            if content is not None:
                return content, RESPONSE_OK
            else:
                if target == Result.INDEX:
                    if result is True:
                        return INDEX_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return INDEX_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.COLUMN:
                    if result is True:
                        return COLUMN_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return COLUMN_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.DOCUMENT:
                    if result is True:
                        return DOCUMENT_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return DOCUMENT_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return None, RESPONSE_INTERNAL_ERROR
        else:
            return PUT_CONTROL_DOCUMENT, RESPONSE_INVALID_INPUT

    @staticmethod
    def delete(index_name, document_id):
        content, target, result = delete_document(TDM, index_name, document_id)
        if content is not None:
            return content, RESPONSE_OK
        else:
            if target == Result.INDEX:
                if result is True:
                    return INDEX_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return INDEX_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            elif target == Result.COLUMN:
                if result is True:
                    return COLUMN_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return COLUMN_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            elif target == Result.DOCUMENT:
                if result is True:
                    return DOCUMENT_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return DOCUMENT_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            else:
                return None, RESPONSE_INTERNAL_ERROR


##################################################################################################################################

@api.route("/Search/InitialCharacter/<index_name>/<column_names>")
class SearchInitialCharacter(Resource):
    @staticmethod
    @api.expect(api.model("SearchInitialCharacterPost", {
        "query": fields.String
    }))
    def post(index_name, column_names):
        column_list = column_names.strip().split(",")
        request_body = get_request(request)
        if "query" in request_body and isinstance(request_body["query"], str):
            content, target, result = find_sentence_by_initial(TDM, index_name, column_list, request_body["query"])
            if content is not None:
                if len(content) == 0:
                    resp = make_response('', RESPONSE_OK_WITH_NO_CONTENT)
                    resp.headers['Content-Length'] = 0

                    return resp
                else:
                    return content, RESPONSE_OK
            else:
                if target == Result.INDEX:
                    if result is True:
                        return INDEX_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return INDEX_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.COLUMN:
                    if result is True:
                        return COLUMN_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return COLUMN_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.DOCUMENT:
                    if result is True:
                        return DOCUMENT_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return DOCUMENT_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return None, RESPONSE_INTERNAL_ERROR
        else:
            return SEARCH_INITIAL_CHARACTER, RESPONSE_INVALID_INPUT


##################################################################################################################################

@api.route("/Search/InitialCount/<index_name>/<column_names>")
class SearchInitialCount(Resource):
    @staticmethod
    def get(index_name, column_names):
        column_list = column_names.strip().split(",")
        content, target, result = get_initial_count(TDM, index_name, column_list)
        if content is not None:
            if len(content) == 0:
                resp = make_response('', RESPONSE_OK_WITH_NO_CONTENT)
                resp.headers['Content-Length'] = 0

                return resp
            else:
                return content, RESPONSE_OK
        else:
            if target == Result.INDEX:
                if result is True:
                    return INDEX_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return INDEX_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            elif target == Result.COLUMN:
                if result is True:
                    return COLUMN_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return COLUMN_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            elif target == Result.DOCUMENT:
                if result is True:
                    return DOCUMENT_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return DOCUMENT_NOT_EXIST, RESPONSE_INTERNAL_ERROR
            else:
                return None, RESPONSE_INTERNAL_ERROR


##################################################################################################################################

@api.route("/Search/AutoComplete/<index_name>/<column_names>")
class AutoComplete(Resource):
    @staticmethod
    @api.expect(api.model("AutoCompletePost", {
        "query": fields.String
    }))
    def post(index_name, column_names):
        column_list = column_names.strip().split(",")
        request_body = get_request(request)
        if "query" in request_body and isinstance(request_body["query"], str):
            content, target, result = auto_complete(TDM, index_name, column_list, request_body["query"])
            if content is not None:
                if len(content) == 0:
                    resp = make_response('', RESPONSE_OK_WITH_NO_CONTENT)
                    resp.headers['Content-Length'] = 0

                    return resp
                else:
                    return content, RESPONSE_OK
            else:
                if target == Result.INDEX:
                    if result is True:
                        return INDEX_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return INDEX_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.COLUMN:
                    if result is True:
                        return COLUMN_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return COLUMN_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.DOCUMENT:
                    if result is True:
                        return DOCUMENT_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return DOCUMENT_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return None, RESPONSE_INTERNAL_ERROR
        else:
            return AUTO_COMPLETE, RESPONSE_INVALID_INPUT


##################################################################################################################################

@api.route("/Search/CosineSimilarity/<index_name>/<column_names>")
class SearchCosineSimilarity(Resource):
    @staticmethod
    @api.expect(api.model("SearchCosineSimilarityPost", {
        "query": fields.String,
        "weight": fields.Raw
    }))
    def post(index_name, column_names):
        column_list = column_names.strip().split(",")
        request_body = get_request(request)
        if "query" in request_body and isinstance(request_body["query"], str) and "weight" in request_body and isinstance(request_body["weight"], dict) and False not in [isinstance(request_body["weight"][x], int) or isinstance(request_body["weight"][x], float) for x in request_body["weight"]]:
            content, target, result = search_with_cosine_similarity(TDM, index_name, column_list, request_body["query"], request_body["weight"])
            if content is not None:
                if len(content) == 0:
                    resp = make_response('', RESPONSE_OK_WITH_NO_CONTENT)
                    resp.headers['Content-Length'] = 0

                    return resp
                else:
                    return content, RESPONSE_OK
            else:
                if target == Result.INDEX:
                    if result is True:
                        return INDEX_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return INDEX_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.COLUMN:
                    if result is True:
                        return COLUMN_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return COLUMN_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.DOCUMENT:
                    if result is True:
                        return DOCUMENT_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return DOCUMENT_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return None, RESPONSE_INTERNAL_ERROR
        else:
            return SEARCH_COSINE_SIMILARITY, RESPONSE_INVALID_INPUT


##################################################################################################################################

@api.route("/Search/WordCount/<index_name>/<column_names>")
class SearchWordCount(Resource):
    @staticmethod
    @api.expect(api.model("SearchCosineSimilarityPost", {
        "query": fields.String,
        "weight": fields.Raw
    }))
    def post(index_name, column_names):
        column_list = column_names.strip().split(",")
        request_body = get_request(request)
        if "query" in request_body and isinstance(request_body["query"], str) and "weight" in request_body and isinstance(request_body["weight"], dict) and False not in [isinstance(request_body["weight"][x], int) or isinstance(request_body["weight"][x], float) for x in request_body["weight"]]:
            content, target, result = search_with_word_count(TDM, index_name, column_list, request_body["query"], request_body["weight"])
            if content is not None:
                if len(content) == 0:
                    resp = make_response('', RESPONSE_OK_WITH_NO_CONTENT)
                    resp.headers['Content-Length'] = 0

                    return resp
                else:
                    return content, RESPONSE_OK
            else:
                if target == Result.INDEX:
                    if result is True:
                        return INDEX_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return INDEX_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.COLUMN:
                    if result is True:
                        return COLUMN_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return COLUMN_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                elif target == Result.DOCUMENT:
                    if result is True:
                        return DOCUMENT_ALREADY_EXIST, RESPONSE_INTERNAL_ERROR
                    else:
                        return DOCUMENT_NOT_EXIST, RESPONSE_INTERNAL_ERROR
                else:
                    return None, RESPONSE_INTERNAL_ERROR
        else:
            return SEARCH_WORD_COUNT, RESPONSE_INVALID_INPUT


##################################################################################################################################

# @api.route("/Search/save")
# class Save(Resource):
#     @staticmethod
#     def post():
#         save_data_scheduler(TDM)
#
#         return True, RESPONSE_OK


schedulers = BackgroundScheduler()
schedulers.start()

schedulers.add_job(func=save_data_scheduler, trigger="interval", seconds=args.scheduler_time, args=[TDM])


if __name__ == "__main__":
    application.run(args.host, args.port)
