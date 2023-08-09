import redis
import datetime
from selenium_facebook.consts import redis_key
import json

class RedisClient:
    def __init__(self, config):
        host = config.get("Redis", "host")
        port = config.get("Redis", "port")
        password = config.get("Redis", "password")
        db = config.get("Redis", "db")
        self.redis = redis.Redis(host=host, port=port, db=db, password=password)

    # 设置账号密码
    def set_account(self, rows):
        self.redis.sadd(redis_key.account_key(), rows)
        pass

    # 随机获取账号密码
    def get_account(self):
        account_str = self.redis.srandmember(redis_key.account_key())
        account_data = json.loads(account_str)
        return account_data["username"], account_data["password"], account_data["secret"]

    # 设置 cookie
    def set_cookie(self, username, cookie, expiration_datetime=0):
        self.redis.set(redis_key.cookie_key(username), cookie)
        # 默认设置为七天
        if expiration_datetime == 0:
            expiration_datetime = datetime.datetime.now() + datetime.timedelta(days=7)

        self.redis.expireat(redis_key.cookie_key(username), expiration_datetime)

    # 获取cookie
    def get_cookie(self, username):
        return self.redis.get(redis_key.cookie_key(username))

    # 存储广告数据进redis
    def ad_push(self, row):
        if self.redis.lpos(redis_key.ad_data_key(), row):
            return

        self.redis.rpush(redis_key.ad_data_key(), row)

    # 取出广告数据（并发不安全，用的时候记得加锁）
    def ad_range(self, ad_number):
        return self.redis.lrange(redis_key.ad_data_key(), 0, ad_number)

    # 移除广告数据（并发不安全，用的时候记得加锁）
    def ad_pop(self, ad_number):
        for _ in range(ad_number):
            self.redis.lpop(redis_key.ad_data_key())

    def set(self, key, value):
        self.redis.set(key, value)

    def get(self, key):
        return self.redis.get(key)
