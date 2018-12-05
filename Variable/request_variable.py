REQUEST_BASE = "http://{ip}:{port}{url}"

RESPONSE_OK = 200
RESPONSE_OK_WITH_NO_CONTENT = 204
RESPONSE_GET_PARTIAL_OK = 206
RESPONSE_INVALID_INPUT = 400
RESPONSE_ALREADY_EXIST = 422
RESPONSE_INTERNAL_ERROR = 500

INDEX_ALREADY_EXIST = {
    "error": "index already exist"
}
INDEX_NOT_EXIST = {
    "error": "index not exist"
}
COLUMN_ALREADY_EXIST = {
    "error": "column already exist"
}
COLUMN_NOT_EXIST = {
    "error": "column not exist"
}
DOCUMENT_ALREADY_EXIST = {
    "error": "document already exist"
}
DOCUMENT_NOT_EXIST = {
    "error": "document not exist"
}

POST_INDEX_CONTROL_AND_INSERT_DOCUMENT = {
    "error": "Invalid input",
    "valid_body": [
        {
            "propose": "index 생성",
            "require_body": None
        },
        {
            "propose": "document 추가",
            "require_body": ["object / document 내용 (id 필수)"]
        }
    ]
}

POST_REBUILD_SYNONYM = {
    "error": "Invalid input",
    "valid_body": {
        "propose": "synonym 추가",
        "require_body": [
            {
                "id": "string / document ID",
                "keyword": "string / 대표 동의어",
                "words": ["string / 동의어"]
            }
        ]
    }
}

DELETE_REBUILD_SYNONYM = {
    "error": "Invalid input",
    "valid_body": {
        "propose": "synonym 삭제",
        "require_body": {
            "document_id": "string / document ID"
        }
    }
}

PUT_CONTROL_DOCUMENT = {
    "error": "Invalid input",
    "valid_body": {
        "propose": "document 수정",
        "require_body": "object / document 내용 (id 필수)"
    }
}

SEARCH_INITIAL_CHARACTER = {
    "error": "Invalid input",
    "valid_body": {
        "propose": "초성검색",
        "require_body": {
            "query": "string / 검색할 초성"
        }
    }
}

AUTO_COMPLETE = {
    "error": "Invalid input",
    "valid_body": {
        "propose": "자동완성",
        "require_body": {
            "query": "string / 자동완성할 대상"
        }
    }
}

SEARCH_COSINE_SIMILARITY = {
    "error": "Invalid input",
    "valid_body": {
        "propose": "cosine 유사도를 통한 검색",
        "require_body": {
            "query": "string / 검색할 문자열",
            "weight": "object / 단어별 가중치"
        }
    }
}

SEARCH_WORD_COUNT = {
    "error": "Invalid input",
    "valid_body": {
        "propose": "BM25를 통해 검색",
        "require_body": {
            "query": "string / 검색할 문자열",
            "weight": "object / 단어별 가중치"
        }
    }
}
