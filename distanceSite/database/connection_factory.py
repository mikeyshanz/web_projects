import database.postgresql_connection_factory as postgresql_connection_factory


def get_connection():
    return postgresql_connection_factory.get_connection()


def proc_insert_query(query):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        cursor.close()
        return True
    except Exception as fail:
        print(fail)
        connection.rollback()
        cursor.close()
        return False


def proc_select_query(query):
    def mapToJson(results, headers):
        json_data = list()
        for result in results:
            json_data.append(dict(zip(headers, result)))
        return json_data
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    results = []
    headers = [x[0] for x in cursor.description]
    for row in cursor:
        results.append(row)
    cursor.close()
    return mapToJson(results, headers)
