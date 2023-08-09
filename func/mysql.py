import mysql.connector
from selenium_facebook.consts import consts

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

    def select_all(self, table, where = None, limit = consts.MYSQL_MAX_ROW):
        query = f"SELECT * FROM {table}"
        if where not in  [None, ""]:
            query += f" WHERE {where}"
        if limit not in [0, None]:
            query += f" LIMIT {limit}"
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

    def insert_batch(self, table, data_list):
        columns = ', '.join(data_list[0].keys())
        values = ', '.join([', '.join([f"'{value}'" for value in data.values()]) for data in data_list])
        query = f"INSERT INTO {table} ({columns}) VALUES {values}"
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

    # 获取用户数据
    def get_user_data(self):
        user_data_list = self.select_all(consts.FB_AD_USER, "status = 2")
        if len(user_data_list) == 0:
            return None
        rows = []
        for row in user_data_list:
            rows.append({
                "username": row["username"],
                "password": row["password"],
                "secret":   row["secret"],
            })
        return rows

    # 获取关键字信息
    def get_keyword(self, keyword_id):
        keyword_data_list = self.select_all(consts.FB_AD_KEYWORD, f" id > {keyword_id} and status in (2, 1) and is_crawling in(2, 1) ", 1)
        if len(keyword_data_list) > 0:
            return keyword_data_list["id"], keyword_data_list["keyword"], keyword_data_list["page"]
        else:
            return None, None, None

    # 获取国家数据信息
    def get_country_data(self):
        country_data_list = self.select_all(consts.FB_AD_COUNTRY, " status = 2 ")
        if len(country_data_list) == 0:
            return None
        country_code_list = []
        for row in country_data_list:
            country_code_list.append(row["country_code"])
        return country_code_list
