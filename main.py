import sys
sys.path.append('func')
sys.path.append('config')
from func import facebook
import requests
import logging
from logging.handlers import TimedRotatingFileHandler


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

    # 记录日志
    logger.info('这是一个普通信息')


if __name__ == '__main__':

    # 初始化日志配置
    init_log()

    # 从配置文件读取账号密码
    fb = facebook.Facebook("./config/config.ini")

    # 获取账号密码
    username, password, secret = fb.get_next_credentials()

    # 登陆
    fb.login(username, password, secret)

    # 爬取广告
    data = fb.scrape_ad_information("US", "Necklace", 1)

    # # 退出登陆
    fb.logout()

    # 关闭浏览器
    fb.close()
