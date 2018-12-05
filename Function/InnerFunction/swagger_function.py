from flask_restplus import fields


def get_swagger_namespace(api):
    namespaces = dict()

    namespaces["SearchIndexExist"] = api.namespace("/Search/<index_name>/exist", description="Index 존재여부 확인")

    return namespaces


def get_swagger_values(api):
    swagger_param = dict()

    swagger_param["CreateIndexAndInsertColumn"] = dict()
    swagger_param["CreateIndexAndInsertColumn"]["DELETE"] = api.model("CreateIndexAndInsertColumnDelete", {
        "column_name": fields.String
    })

    swagger_param["RebuildSynonym"] = dict()
    swagger_param["RebuildSynonym"]["POST"] = [api.model("RebuildSynonymPost", {
        "id": fields.String,
        "keyword": fields.String,
        "words": fields.List(fields.String)
    })]
    swagger_param["RebuildSynonym"]["DELETE"] = api.model("RebuildSynonymDelete", {
        "document_id": fields.String
    })

    swagger_param["InsertDocument"] = dict()
    swagger_param["InsertDocument"]["POST"] = api.model("InsertDocumentPost", {
        "document": fields.Raw
    })
    swagger_param["InsertDocument"]["PUT"] = api.model("InsertDocumentPost", {
        "document": fields.Raw
    })
    swagger_param["InsertDocument"]["DELETE"] = api.model("InsertDocumentDelete", {
        "document": fields.Raw
    })

    swagger_param["InsertMultiDocument"] = dict()
    swagger_param["InsertMultiDocument"]["POST"] = api.model("InsertMultiDocumentPost", {
        "documents": fields.List(fields.Raw),
        "document_ids": fields.List(fields.String)
    })

    swagger_param["SearchInitialCharacter"] = dict()
    swagger_param["SearchInitialCharacter"]["POST"] = api.model("SearchInitialCharacterPost", {
        "query": fields.String
    })

    swagger_param["AutoComplete"] = dict()
    swagger_param["AutoComplete"]["POST"] = api.model("AutoCompletePost", {
        "query": fields.String
    })

    swagger_param["SearchCosineSimilarity"] = dict()
    swagger_param["SearchCosineSimilarity"]["POST"] = api.model("SearchCosineSimilarityPost", {
        "query": fields.String,
        "weight": fields.Raw
    })

    swagger_param["SearchWordCount"] = dict()
    swagger_param["SearchWordCount"]["POST"] = api.model("SearchWordCountPost", {
        "query": fields.String,
        "weight": fields.Raw
    })

    return swagger_param
