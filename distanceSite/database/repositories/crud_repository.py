

class CrudRepository:

    def __init__(self, connection):
        self.connection = connection

    def mapToJson(self, results, headers):
        json_data = list()
        for result in results:
            json_data.append(dict(zip(headers, result)))
        return json_data

    def insert_query(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
            return True
        except Exception as fail:
            print(fail)
            self.connection.rollback()
            cursor.close()
            return False

    def select_query(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            results = []
            headers = [x[0] for x in cursor.description]
            for row in cursor:
                results.append(row)
            cursor.close()
            self.connection.commit()
        except Exception as fail:
            print(fail)
            self.connection.rollback()
            cursor.close()
            return None
        return self.mapToJson(results, headers)
    
    def query(self, query, parameters):
        cursor = self.connection.cursor()
        cursor.execute(query, parameters)
        results = []
        headers=[x[0] for x in cursor.description]
        for row in cursor:
            results.append(row)
        cursor.close()
        return self.mapToJson(results, headers)
