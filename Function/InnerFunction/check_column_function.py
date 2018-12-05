def check_column(documents, column_names):
    for document in documents:
        for column_name in column_names:
            if column_name not in document:
                return False
            else:
                if isinstance(document[column_name], str) or document[column_name] is None:
                    return True
                elif isinstance(document[column_name], list):
                    for column_value in document[column_name]:
                        if not isinstance(column_value, str):
                            return False
                    return True
                else:
                    return False
