import json
import sys
import time

sys.path.append('func')
sys.path.append('config')
from func import facebook
from func import redis_func
from func import common
from func import mysql
import logging
from logging.handlers import TimedRotatingFileHandler
import configparser
import asyncio
import datetime
from consts import consts
from consts import redis_key
from apscheduler.schedulers.blocking import BlockingScheduler
import functools


# 初始化日志
def init_log():
    # 创建TimedRotatingFileHandler对象
    handler = TimedRotatingFileHandler(filename='./logs/app.log', when='midnight', interval=1, backupCount=30)

    # 配置日志记录
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)


# 爬取广告(可直接并发调用)
def generate_advertising(mysql_client, redis_client):
    print("generate_advertising start")
    # 获取国家列表
    country_list = redis_client.get_country()
    if country_list is None or len(country_list) == 0:
        return

    # 获取关键字标记(轮转关键字)  这一块并发不安全，加锁顺序执行
    keyword_id = int(redis_client.get(redis_key.keyword_id_key()))
    if keyword_id is None:
        keyword_id = 0

    # 获取一个关键字
    keyword_id, keyword, page_size = mysql_client.get_keyword(keyword_id)
    if keyword is None or page_size is None:
        # 没有取到（到尾部了）则从头部再取一次
        keyword_id, keyword, page_size = mysql_client.get_keyword(0)
        if keyword is None or page_size is None:  # 关键字表里没数据了
            redis_client.set(redis_key.keyword_id_key(), 0)
            return

    redis_client.set(redis_key.keyword_id_key(), keyword_id)

    # 初始化facebook配置
    fb = facebook.Facebook(redis_client)

    # 登陆
    fb.login()

    # 一个关键字 爬取多个国家的数据
    for country in country_list:
        # 未设置关键字页则给默认值
        if page_size <= 0:
            page_size = 20

        # 爬取广告
        fb.scrape_ad_information(country, keyword, page_size)

        # 休眠一段时间
        time.sleep(common.random_int())

    # 退出登陆
    fb.logout()

    # 关闭浏览器
    fb.close()

    print("generate_advertising end")


# 把爬取的广告写进mysql(可直接并发调用)
def mv_advertising(mysql_client, redis_client, row_number=500):
    print("mv_advertising start")
    # 获取锁
    identifier = redis_client.acquire_lock(redis_key.lock_key("mv_advertising"))
    if not identifier:
        print("mv_advertising 获取锁失败")
        return

    if row_number == 0:
        print("row_number 需要大于 0")
        return

    # 获取 redis 数据
    ad_data_list = redis_client.ad_range(row_number)
    if len(ad_data_list) == 0:
        print("没有数据")
        return

    # 转化成mysql的数据
    fb_ad_data_list = []
    for ad_data in ad_data_list:
        ad_data = json.loads(ad_data.decode('utf-8', errors='ignore'))
        row = {
            "advertiser": ad_data["advertiser"],
            "ad_content": ad_data["ad_content"],
            "advertiser_url": ad_data["advertiser_url"],
            "advertiser_domain": ad_data["advertiser_domain"],
            "country": ad_data["country"],
            "keyword": ad_data["keyword"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        if not redis_client.in_filter_domain(row["advertiser_domain"]):
            fb_ad_data_list.append(row)

    # 批量写入mysql
    rowcount = mysql_client.insert_batch(consts.FB_AD_DATA, fb_ad_data_list)
    if rowcount > 0:
        # 从redis中清除写入的数据(忽略的数据也要清除)
        redis_client.ad_pop(row_number)

    # 释放锁
    if identifier:
        redis_client.release_lock(redis_key.lock_key("mv_advertising"), identifier)

    print("mv_advertising end")

# 启动
def run():
    # 初始化配置
    config = configparser.ConfigParser()
    config.read("./config/config.ini")

    # 初始化日志配置
    init_log()

    # 初始化 mysql 连接
    mysql_client = mysql.MySQLDatabase(config)

    # 初始化 redis 连接
    redis_client = redis_func.RedisClient(config)

    # 初始化 redis 数据
    init_redis_data(mysql_client, redis_client)

    # 调试爬取广告数据
    # generate_advertising(mysql_client, redis_client)

    # 调试 数据入库
    # mv_advertising(mysql_client, redis_client)

    # 创建调度器 添加定时任务，每隔20秒执行一次
    scheduler = BlockingScheduler()
    scheduler.add_job(functools.partial(generate_advertising, mysql_client, redis_client), 'interval', minutes=3)
    scheduler.add_job(functools.partial(mv_advertising, mysql_client, redis_client, 500), 'interval', seconds=20)
    scheduler.start()



# 初始化 redis 数据
def init_redis_data(mysql_client, redis_client):
    # 初始化用户数据到redis
    user_data = mysql_client.get_user_data()
    redis_client.set_account(user_data)

    # 初始化国家数据到redis
    country_data = mysql_client.get_country_data()
    redis_client.set_country(country_data)

    # 初始化域名过滤数据到redis(模糊匹配)
    like_data = mysql_client.get_filter_domain(consts.FB_FILTER_DOMAIN_RULE_LIKE)
    if like_data is not None and len(like_data) > 0:
        redis_client.set_filter_domain(consts.FB_FILTER_DOMAIN_RULE_LIKE, like_data)

    # 初始化域名过滤数据到redis(全匹配)
    eq_data = mysql_client.get_filter_domain(consts.FB_FILTER_DOMAIN_RULE_EQ)
    if eq_data is not None and len(eq_data) > 0:
        redis_client.set_filter_domain(consts.FB_FILTER_DOMAIN_RULE_EQ, eq_data)


if __name__ == '__main__':
    run()
