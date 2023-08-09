import mysql.connector

class MySQLDatabase:
    def __init__(self, config):
        self.host = config.get("Mysql", "host")
        self.user = config.get("Mysql", "username")
        self.password = config.get("Mysql", "password")
        self.database = config.get("Mysql", "db")
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except mysql.connector.Error as error:
            print("Failed to connect to MySQL database:", error)

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Disconnected from MySQL database")

    def execute_query(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor

    def select_all(self, table, limit):
        query = f"SELECT * FROM {table} LIMIT {limit}"
        cursor = self.execute_query(query)
        rows = cursor.fetchall()
        return rows

    def select_by_id(self, table, id):
        query = f"SELECT * FROM {table} WHERE id = {id}"
        cursor = self.execute_query(query)
        row = cursor.fetchone()
        return row

    def insert(self, table, data):
        columns = ', '.join(data.keys())
        values = ', '.join([f"'{value}'" for value in data.values()])
        query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
        cursor = self.execute_query(query)
        self.connection.commit()
        return cursor.lastrowid

    def update(self, table, id, data):
        set_values = ', '.join([f"{key} = '{value}'" for key, value in data.items()])
        query = f"UPDATE {table} SET {set_values} WHERE id = {id}"
        cursor = self.execute_query(query)
        self.connection.commit()
        return cursor.rowcount

    def delete(self, table, id):
        query = f"DELETE FROM {table} WHERE id = {id}"
        cursor = self.execute_query(query)
        self.connection.commit()
        return cursor.rowcount

# Usage example:
# database = MySQLDatabase('localhost', 'root', 'password', 'mydatabase')
# database.connect()
#
# # Select all rows from a table
# rows = database.select_all('mytable')
# for row in rows:
#     print(row)
#
# # Insert a new row into a table
# data = {'name': 'John', 'age': 30, 'email': 'john@example.com'}
# new_id = database.insert('mytable', data)
# print("New row ID:", new_id)
#
# # Update a row in a table
# data = {'name': 'Jane', 'age': 25, 'email': 'jane@example.com'}
# updated_rows = database.update('mytable', 1, data)
# print("Updated rows:", updated_rows)
#
# # Delete a row from a table
# deleted_rows = database.delete('mytable', 2)
# print("Deleted rows:", deleted_rows)
#
# database.disconnect()