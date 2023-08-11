import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import configparser
import time
import datetime
from urllib.parse import urlparse
from selenium.common.exceptions import StaleElementReferenceException
from urllib.parse import unquote
import common
from selenium.webdriver.chrome.options import Options
import requests
import redis_func
import asyncio
import json


class Facebook:
    # 初始化
    def __init__(self, redis_client):
        # # 初始化redis
        self.redis_client = redis_client
        # 浏览器初始化及打开
        chrome_options = Options()
        chrome_options.add_argument("--incognito")  # 无痕 （兼容并发登陆退出）
        self.driver = webdriver.Chrome(options=chrome_options)

    # 设置浏览器cookie信息
    def set_cookie(self, cookie):
        cookie = {
            'name': 'c_user',
            'value': cookie
        }
        self.driver.add_cookie(cookie)
        self.driver.refresh()

    # 登录
    def login(self):
        # 账号池中随机获取账号密码
        username, password, secret = self.redis_client.get_account()
        if username is None or password is None:
            print("账户名密码为空")
            return

        # 跳转页面
        self.driver.get("https://www.facebook.com/login")

        # 获取cookie缓存 设置cookie
        cookie = self.redis_client.get_cookie(username)
        if cookie is not None:
            cookies = json.loads(cookie)
            for ck in cookies:
                self.driver.add_cookie(ck)
        else:
            # 没有cookie缓存则走登陆流程
            email_field = self.driver.find_element(By.ID, "email")
            email_field.send_keys(username)
            password_field = self.driver.find_element(By.ID, "pass")
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
            WebDriverWait(self.driver, 10).until(EC.url_contains("facebook.com"))

            # 登陆之后如果需要二次验证，进行二次验证
            if self.is_secondary_validation():
                time.sleep(5)
                if secret is None:
                    print(f"{username}的secret是空的")
                    return
                self.secondary_validation(secret)

            # 将cookie缓存起来
            cookies = self.driver.get_cookies()
            json_str = json.dumps(cookies, indent=4, ensure_ascii=False)
            self.redis_client.set_cookie(username, json_str)

    # 退出登录
    def logout(self):
        self.driver.delete_cookie("c_user")
        self.driver.refresh()

    # 爬取广告
    def scrape_ad_information(self, country, keyword, page_size):
        country = country.decode('utf-8', errors='ignore')
        print(f"开始爬取数据，关键字：{keyword}， 国家：{country}")
        time.sleep(2)  # 等两秒在跳转
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={keyword}&search_type=keyword_unordered&media_type=all"
        self.driver.get(url)
        time.sleep(2)

        # 滚动页面以加载更多广告
        self.scroll_page(page_size)

        try:
            ad_elements = self.driver.find_elements(By.CSS_SELECTOR, "._7jvw.x2izyaf.x1hq5gj4.x1d52u69")
            if len(ad_elements) == 0:
                return

            for ad_element in ad_elements:
                ad_content, advertiser, advertiser_url, advertiser_domain = "", "", "", ""
                # 广告内容
                ad_content_elements = ad_element.find_elements(By.CSS_SELECTOR, "._4ik4._4ik5")
                if len(ad_content_elements) > 0:
                    ad_content = ad_content_elements[1].text

                # 广告商
                advertiser_elements = ad_element.find_elements(By.CSS_SELECTOR,".x8t9es0.x1fvot60.xxio538.x108nfp6.xq9mrsl.x1h4wwuj.x117nqv4.xeuugli")
                if len(advertiser_elements) > 0:
                    advertiser = advertiser_elements[0].text

                # 落地页
                advertiser_url_elements = ad_element.find_elements(By.CSS_SELECTOR,".x1hl2dhg.x1lku1pv.x8t9es0.x1fvot60.xxio538.xjnfcd9.xq9mrsl.x1yc453h.x1h4wwuj.x1fcty0u.x1lliihq")
                if len(advertiser_url_elements) == 0:
                    continue

                advertiser_url = unquote(advertiser_url_elements[0].get_attribute("href"))
                advertiser_url = common.remove_facebook_redirect(advertiser_url)
                if advertiser_url:
                    advertiser_domain = urlparse(advertiser_url).netloc  # 独立站域名

                data = {
                    "advertiser": advertiser,
                    "ad_content": ad_content,
                    "advertiser_url": advertiser_url,
                    "advertiser_domain": advertiser_domain,
                    "keyword": keyword,
                    "country": country,
                }
                print(data)

                # 不在过滤域名中，数据存进redis
                if not self.redis_client.in_filter_domain(data["advertiser_domain"]):
                    self.redis_client.ad_push(json.dumps(data))

        except StaleElementReferenceException:
            logging.info("发生异常:", StaleElementReferenceException)

    # 滚动页面
    def scroll_page(self, max_scrolls=20):
        # 滚动次数计数器
        scroll_count = 0

        # 滚动到页面底部
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while scroll_count <= max_scrolls:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(common.random_int())  # 休眠一个随机时间 避免被facebook 发现规律
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scroll_count += 1

        time.sleep(2)

    # 获取验证码
    def query_code(self, fa2_secret):
        response = requests.get(f"https://2fa.live/tok/{fa2_secret}")
        if response.status_code == 200:
            # 获取响应内容
            data = response.json()
            return data["token"]
        else:
            logging.error("请求失败，状态码为：", response.status_code)

    # 二次验证
    def secondary_validation(self, fa2_secret):
        # 获取验证码
        code = self.query_code(fa2_secret)
        if code is not None and len(code) == 6:
            # 填入验证码
            approvals_code_input = self.driver.find_element(By.ID, "approvals_code")
            approvals_code_input.send_keys(code)

            # 通过验证
            button = self.driver.find_element(By.ID, "checkpointSubmitButton")
            button.click()
            # 保存浏览器
            button = self.driver.find_element(By.ID, "checkpointSubmitButton")
            button.click()

    # 判断是否需要二次验证
    def is_secondary_validation(self):
        # 获取当前域名
        current_url = self.driver.current_url
        # 判断前缀是否匹配
        prefixes = [
            "https://www.facebook.com/checkpoint/",
            "http://www.facebook.com/checkpoint/",
            "www.facebook.com/checkpoint/",
            "facebook.com/checkpoint/"
        ]

        # 遍历前缀列表，判断前缀是否匹配
        for prefix in prefixes:
            if current_url.startswith(prefix):
                return True

        return False

    # 关闭页面
    def close(self):
        self.driver.quit()