import sqlite3


class DatabaseManager:

    def __init__(self, database_file_path):
        self.database_file_path = database_file_path

    def create_connection(self):
        connection = None
        try:
            connection = sqlite3.connect(self.database_file_path)
            cursor = connection.cursor()
            return connection, cursor
        except Exception as e:
            print(e)
        return connection

    def db_execute_select(self, sql_str, args=None, pass_errors=False):
        try:
            connection, cursor = self.create_connection()
            if args:
                cursor.execute(sql_str, args)
            else:
                cursor.execute(sql_str)
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return results
        except Exception as e:
            if pass_errors:
                raise e
            else:
                print(e)

    def db_execute_commit(self, sql_str, args=None, pass_errors=False):
        try:
            connection, cursor = self.create_connection()
            if args:
                cursor.execute(sql_str, args)
            else:
                cursor.execute(sql_str)
            connection.commit()
            cursor.close()
            connection.close()
        except Exception as e:
            if pass_errors:
                raise e
            else:
                print(e)