import sys
sys.path.append('func')
sys.path.append('config')

from func import facebook
from config import business

if __name__ == '__main__':
    print(business.keyword_list)
    print(business.country_list)
    exit(1)

    # 从配置文件读取账号密码
    fb = facebook.Facebook("./config/config.ini")

    # 获取账号密码
    username, password = fb.get_next_credentials()

    # 登陆
    fb.login(username, password)

    # 爬取广告
    fb.scrape_ad_information("US", "Necklace", 10)

    # # 退出登陆
    fb.logout()

    # # 关闭浏览器
    fb.close()