import logging

import redis
import datetime
from selenium_facebook.consts import redis_key
from selenium_facebook.consts import consts
import json
import time


class RedisClient:
    def __init__(self, config):
        host = config.get("Redis", "host")
        port = config.get("Redis", "port")
        password = config.get("Redis", "password")
        db = config.get("Redis", "db")
        self.redis = redis.Redis(host=host, port=port, db=db, password=password)

    # 设置域名过滤信息
    def set_filter_domain(self, rule, rows):
        # 删除域名过滤信息
        self.redis.delete(redis_key.filter_domain_key(rule))
        # 初始化域名过滤信息
        self.redis.sadd(redis_key.filter_domain_key(rule), *rows)
        pass

    # 判断在不在过滤列表中
    def in_filter_domain(self, val):
        # 判断在不在过滤域名中
        is_in_eq = self.redis.sismember(redis_key.filter_domain_key(consts.FB_FILTER_DOMAIN_RULE_EQ), val)
        if is_in_eq:
            return is_in_eq

        # 获取Redis集合中的所有元素
        filter_domains = self.redis.smembers(redis_key.filter_domain_key(consts.FB_FILTER_DOMAIN_RULE_LIKE))
        # 遍历集合中的元素，判断是否存在于字符串中
        for domain in filter_domains:
            if domain.decode() in val:
                return True

        return False

    # 设置国家信息
    def set_country(self, rows):
        # 删除国家数据
        self.redis.delete(redis_key.country_key())
        # 初始化国家数据
        self.redis.sadd(redis_key.country_key(), *rows)
        pass

    # 获取国家列表
    def get_country(self):
        # 获取Set类型键为 'myset' 的所有元素
        country_list = self.redis.smembers(redis_key.country_key())
        # 将元素转换为列表
        country_list = list(country_list)
        if len(country_list) == 0:
            return None

        return country_list

    # 设置账号信息
    def set_account(self, rows):
        # 删除账号数据
        if self.redis.exists(redis_key.account_key()):
            self.redis.delete(redis_key.account_key())

        rows = [str(item) for item in rows]
        # 初始化账号数据
        self.redis.sadd(redis_key.account_key(), *rows)

    # 随机获取账号密码
    def get_account(self):
        account_str = self.redis.srandmember(redis_key.account_key(), 1)
        data = account_str[0].decode().replace("'", "\"")
        account_data = json.loads(data)
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
        self.redis.rpush(redis_key.ad_data_key(), row)

    # 取出广告数据（并发不安全，用的时候记得加锁）
    def ad_range(self, ad_number = 500):
        return self.redis.lrange(redis_key.ad_data_key(), 0, ad_number - 1)

    # 移除广告数据（并发不安全，用的时候记得加锁）
    def ad_pop(self, ad_number):
        for _ in range(ad_number):
            self.redis.lpop(redis_key.ad_data_key())

    def set(self, key, value):
        self.redis.set(key, value)

    def get(self, key):
        return self.redis.get(key)

    # 获取分布式锁
    def acquire_lock(self, redis_lock_key, acquire_timeout=10):
        # 生成锁的唯一标识
        identifier = str(time.time())

        # 尝试获取锁
        lock_acquired = self.redis.setnx(redis_lock_key, identifier)

        # 设置锁的过期时间，防止死锁
        self.redis.expire(redis_lock_key, acquire_timeout)

        # 返回锁的标识符，用于解锁时验证
        return identifier if lock_acquired else None

    # 释放分布式锁
    def release_lock(self, redis_lock_key, identifier):
        # 释放锁
        current_identifier = self.redis.get(redis_lock_key)

        if current_identifier and current_identifier.decode() == identifier:
            self.redis.delete(redis_lock_key)
        else:
            logging.info("无法释放锁，锁已过期或被其他进程持有")
