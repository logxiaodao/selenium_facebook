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
async def generate_advertising(redis_client):
    # 获取关键字和国家
    keyword = "Necklace"
    country = "US"
    page_size = 1

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

# 协程任务把爬取的广告写进mysql
async def mv_advertising(mysql_client, redis_client):
    number = 500
    # 获取 redis 数据
    ad_data = redis_client.ad_range(number)
    if len(ad_data) == 0:
        # 没有数据 暂时休眠
        time.sleep(10)
        return

    # 写入mysql todo 晚点写

    # 从redis中清除写入的数据
    redis_client.ad_pop(number)


async def run():
    # 初始化配置
    config = configparser.ConfigParser()
    config.read("./config/config.ini")

    # 初始化 redis 连接
    redis_client = redis_func.RedisClient(config)

    # 初始化 mysql 连接
    mysql_client = mysql.MySQLDatabase(config)

    # 初始化日志配置
    init_log()

    while True:
        try:
            await asyncio.to_thread(generate_advertising, redis_client)
            await asyncio.to_thread(mv_advertising, mysql_client, redis_client)
        except Exception as e:
            logging.error(f"An error occurred: {e}")

if __name__ == '__main__':
    asyncio.run(run())


