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


# 协程任务不停爬取广告
async def generate_advertising(mysql_client, redis_client):
    # 获取关键字标记(轮转关键字)
    keyword_id = redis_client.get(redis_key.keyword_id_key())
    if keyword_id is None:
        keyword_id = 0

    # 获取一个关键字
    keyword_id, keyword, page_size = mysql_client.get_keyword(keyword_id)
    if keyword is None or page_size is None:
        redis_client.set(redis_key.keyword_id_key(), 0)
        return
    redis_client.set(redis_key.keyword_id_key(), keyword_id)

    # 获取国家列表
    country_list = redis_client.get_country()
    if country_list is None or len(country_list) == 0:
        return

    # 一个关键字 爬取多个国家的数据
    for country in country_list:
        # 休眠一段时间
        time.sleep(common.random_int())

        # 初始化facebook配置
        fb = facebook.Facebook(redis_client)

        # 登陆
        fb.login()

        # 爬取广告
        fb.scrape_ad_information(country, keyword, page_size)

        # # 退出登陆
        fb.logout()

        # 关闭浏览器
        fb.close()

    # 每执行完一个账号 休眠一分钟
    time.sleep(60)


# 协程任务把爬取的广告写进mysql
async def mv_advertising(mysql_client, redis_client):
    # 获取锁
    identifier = redis_client.acquire_lock(redis_key.lock_key("mv_advertising"))

    number = 500
    # 获取 redis 数据
    ad_data_list = redis_client.ad_range(number)
    if len(ad_data_list) == 0:
        # 没有数据 暂时休眠
        time.sleep(20)
        return

    # 转化成mysql的数据
    fb_ad_data_list = []
    for ad_data in ad_data_list:
        row = {
            "advertiser": ad_data["advertiser"],
            "ad_content": ad_data["ad_content"],
            "advertiser_url": ad_data["advertiser_url"],
            "advertiser_domain": ad_data["advertiser_domain"],
            "country": ad_data["country"],
            "keyword": ad_data["keyword"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        fb_ad_data_list.append(row)

    # 批量写入mysql
    mysql_client.insert_batch(consts.FB_AD_DATA, fb_ad_data_list)

    # 从redis中清除写入的数据
    redis_client.ad_pop(number)

    # 释放锁
    if identifier:
        redis_client.release_lock(redis_key.lock_key("mv_advertising"), identifier)

# 启动协程任务
async def run():
    # 初始化配置
    config = configparser.ConfigParser()
    config.read("./config/config.ini")

    # 初始化 redis 连接
    redis_client = redis_func.RedisClient(config)

    # 初始化 mysql 连接
    mysql_client = mysql.MySQLDatabase(config)

    # 初始化用户redis数据
    user_data = mysql_client.get_user_data()
    redis_client.set_account(user_data)

    # 初始化国家数据
    country_data = mysql_client.get_country_data()
    redis_client.set_country(country_data)

    # 初始化日志配置
    init_log()

    while True:
        try:
            await asyncio.to_thread(generate_advertising, mysql_client, redis_client)
            await asyncio.to_thread(mv_advertising, mysql_client, redis_client)
        except Exception as e:
            logging.error(f"An error occurred: {e}")


if __name__ == '__main__':
    asyncio.run(run())
