# search #

simple search engine

#### 설명 ####

cosine similarity, BM25 등 다양한 방식의 검색 기능  
다른 형태의 검색방식으로도 커스터마이징 가능

#### install ####

python 설치  
    -  apt-get install python3.6  
virtualenv 설치  
    - pip install virtualenv  
virtualenv 생성  
    - virtualenv env -p python3.6  
필요한 modules 설치  
    - source ./env/bin/activate  
    - pip install -r requirements.txt  

#### run ####

// from search  
python main.py

|Option|type|Explain|Is required|Default|
|-----|---|--------------------|---|-----|
|--host|String|flask host|X|"0.0.0.0"|
|--port|Integer|flask port|X|12001|
|--scheduler_time|Integer|scheduler time (seconds)|X|600|

#### http request ####

GET /Search/<index_name>/exist
```
    - index 존재여부 확인
    
    input
        (no parameter)
        
    output
        (Boolean)
```
GET /Search/<index_name>/<document_id>/exist
```
    - document 존재여부 확인
    
    input
        (no parameter)
    output
        (Boolean)
```
GET /Search/index
```
    - 존재하는 index list 가져오기
    
    input
        (no parameter)
    output
        [
            (String / index명),
            ...
        ]
```
GET /Search/<index_name>/document
```
    - 특정 index에 존재하는 document list 가져오기
    
    input
        (no parameter)
    output
        [
            (String / document ID),
            ...
        ]
```
GET /Search/<index_name>/document/count
```
    - 특정 index에 존재하는 document의 개수 가져오기
    
    input
        (no parameter)
    output
        (Integer / document 개수)
```
POST /Search/<index_name>
```
    - index 생성
    
    input
        (no parameter)
    output
        (Boolean / index 생성여부)
```
POST /Search/<index_name>
```
    - document 추가
    
    input
        [
            (Object / document 내용("id" key  반드시 필요)),
            ...
        ]
    output
        (Boolean / document 추가여부)
```
DELETE /Search/<index_name>
```
    - index 삭제
    
    input
        (no parameter)
    output
        (Boolean / index 삭제여부)
```
GET /Search/<index_name>/synonym
```
    - 특정 index에 적용된 동의어 가져오기
    
    input
        (no parameter)
    output
        [
            {
                "keyword": (String / 대표 동의어),
                "words": [
                    (String / 동의어 단어),
                    ...
                ]
            },
            ...
        ]
```
POST /Search/<index_name>/synonym
```
    - 특정 index에 동의어 등록
    
    input
        [
            {
                "id": (String / 동의어 ID (required)),
                "keyword": (String / 대표 동의어),
                "words": [
                    (String / 동의어 단어),
                    ...
                ]
            },
            ...
        ]
    output
        (Boolean / 동의어 등록여부)
```
DELETE /Search/<index_name>/synonym
```
    - 특정 index의 동의어 삭제
    
    input
        {"document_id": (String / 동의어 ID (required))}
    output
        (Boolean / 동의어 삭제여부)
```
GET /Search/<index_name>/<document_id>
```
    - 해당 index의 특정 document 내용 가져오기
    
    input
        (no parameter)
    output
        (Object / document 내용)
```
PUT /Search/<index_name>/<document_id>
```
    - 특정 index의 특정 document 수정
    
    input
        (Object / document 내용("id" key 반드시 필요))
    output
        (Boolean / document 수정여부)
```
DELETE /Search/<index_name>/<document_id>
```
    - 특정 index의 특정 document 삭제
    
    input
        (no parameter)
    output
        (Boolean / document 삭제여부)
```
POST /Search/InitialCharacter/<index_name>/<column_names>
```
    - 초성검색
    
    input
        {"query": (String / 검색하고자 하는 초성)}
     output
        [
            {
                "score": (Integer / 초성이 맞는 점수),
                "sentence": (String / 완성 문장)
            },
            ...
        ]
```
GET /Search/InitialCount/<index_name>/<column_names>
```
    - 시작 초성 개수
    
    input
        {
            (String / 초성): (Integer / 개수),
            ...
        }
```
POST /Search/AutoComplete/<index_name>/<column_names>
```
    - 자동완성
    
    input
        {"query": (String / 자동완성 되고자 하는 문장)}
    output
        [
            (String / 자동완성된 문장),
            ...
        ]
```
POST /Search/CosineSimilarity/<index_name>/<column_names>
```
    - cosine similarity를 이용한 검색
    
    input
        {
            "query": (String / 검색할 내용),
            "weight": {
                (String / 중요도를 변경할 단어): (Float / 중요도 값 (기본 1.0)),
                ...
            }
        }
    output
        [
            {
                "document": (Object / document 내용),
                "score": (Float / 유사도 점수)
            },
            ...
        ]
```
POST /Search/WordCount/<index_name>/<column_names>
```
    - BM25를 이용한 검색
    
    input
        {
            "query": (String / 검색할 내용),
            "weight": {
                (String / 중요도를 변경할 단어): (Float / 중요도 값 (기본 1.0)),
                ...
            }
        }
    output
        [
            {
                "document": (Object / document 내용),
                "score": (Float / BM25 점수)
            },
            ...
        ]
```