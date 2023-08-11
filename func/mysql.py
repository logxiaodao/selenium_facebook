import mysql.connector
from selenium_facebook.consts import consts

class MySQLDatabase:
    def __init__(self, config):
        try:
            self.connection = mysql.connector.connect(
                host=config.get("Mysql", "host"),
                port=config.get("Mysql", "port"),
                user=config.get("Mysql", "username"),
                password=config.get("Mysql", "password"),
                database=config.get("Mysql", "db"),
                connect_timeout=30
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
        print(query)
        cursor.execute(query)
        return cursor

    def select_all(self, table, where = None, limit = consts.MYSQL_MAX_ROW):
        query = f"SELECT * FROM {table} "
        if where not in  [None, ""]:
            query += f" WHERE {where} "
        if limit not in [0, None]:
            query += f" LIMIT {limit};"
        cursor = self.execute_query(query)
        rows = cursor.fetchall()

        # 获取列名信息
        columns = [column[0] for column in cursor.description]

        # 将每一行的数据与列名进行组合，生成字典
        results = []
        for row in rows:
            data = {}
            for i, value in enumerate(row):
                data[columns[i]] = value
            results.append(data)

        return results

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

    # def insert_batch(self, table, data_list):
    #     columns = ', '.join(data_list[0].keys())
    #     values = ', '.join([', '.join([f"`{value}`" for value in data.values()]) for data in data_list])
    #     query = f"INSERT IGNORE INTO {table} ({columns}) VALUES ({values})"
    #     cursor = self.execute_query(query)
    #     self.connection.commit()
    #     return cursor.rowcount

    def insert_batch(self, table, data_list):
        columns = ', '.join(data_list[0].keys())
        placeholders = ', '.join(['%s'] * len(data_list[0]))
        values = [tuple(data.values()) for data in data_list]
        query = f"INSERT IGNORE INTO {table} ({columns}) VALUES ({placeholders})"
        cursor = self.connection.cursor()
        cursor.executemany(query, values)
        self.connection.commit()
        return cursor.rowcount

    def update(self, table, id, data):
        set_values = ', '.join([f"{key} = '{value}'" for key, value in data.items()])
        query = f"UPDATE {table} SET {set_values} WHERE id = {id};"
        cursor = self.execute_query(query)
        self.connection.commit()
        return cursor.rowcount

    def delete(self, table, id):
        query = f"DELETE FROM {table} WHERE id = {id};"
        cursor = self.execute_query(query)
        self.connection.commit()
        return cursor.rowcount

    # 获取用户数据
    def get_user_data(self):
        user_data_list = self.select_all(consts.FB_AD_USER, f" status = {consts.FB_AD_USER_STATUS_ON} ")
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
        keyword_data_list = self.select_all(consts.FB_AD_KEYWORD, f" id > {keyword_id} and `status` in ({consts.FB_AD_KEYWORD_STATUS_ON},{consts.FB_AD_KEYWORD_STATUS_DEFAULT}) and `is_crawling` in({consts.FB_AD_KEYWORD_IS_CRAWLING_DEFAULT},{consts.FB_AD_KEYWORD_IS_CRAWLING_YES}) ", 1)
        if len(keyword_data_list) > 0:
            return keyword_data_list[0]["id"], keyword_data_list[0]["keyword"], keyword_data_list[0]["page"]
        else:
            return None, None, None

    # 获取国家数据信息
    def get_country_data(self):
        country_data_list = self.select_all(consts.FB_AD_COUNTRY, f" is_crawling = {consts.FB_AD_COUNTRY_IS_CRAWLING_YES} ")
        if len(country_data_list) == 0:
            return None
        country_code_list = []
        for row in country_data_list:
            country_code_list.append(row["country_code"])
        return country_code_list

    # 获取过滤信息
    def get_filter_domain(self, rule):
        filter_domain_list = self.select_all(consts.FB_FILTER_DOMAIN, f" rule = '{rule}' and status = {consts.FB_FILTER_DOMAIN_STATUS_ON} ")
        if len(filter_domain_list) == 0:
            return None
        domain_list = []
        for row in filter_domain_list:
            domain_list.append(row["domain"])
        return domain_list
