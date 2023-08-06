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

class Facebook:
    def __init__(self, config_file):
        self.driver = webdriver.Chrome()
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.current_index = 1

    # 顺序获取账号密码
    def get_next_credentials(self):
        if f"CredentialSet{self.current_index}" in self.config:
            username = self.config.get(f"CredentialSet{self.current_index}", "username")
            password = self.config.get(f"CredentialSet{self.current_index}", "password")
            self.current_index += 1
            return username, password
        else:
            self.current_index = 1
            if f"CredentialSet{self.current_index}" in self.config:
                username = self.config.get(f"CredentialSet{self.current_index}", "username")
                password = self.config.get(f"CredentialSet{self.current_index}", "password")
                self.current_index += 1
                return username, password
            else:
                return None, None

    # 登录
    def login(self, email, password):
        self.driver.get("https://www.facebook.com/login")
        email_field = self.driver.find_element(By.ID, "email")
        email_field.send_keys(email)
        password_field = self.driver.find_element(By.ID, "pass")
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        WebDriverWait(self.driver, 10).until(EC.url_contains("facebook.com"))

    # 退出登陆
    def logout(self):
        self.driver.delete_cookie("c_user")
        self.driver.refresh()

    # 爬取广告
    def scrape_ad_information(self, country, keyword, wait_second):
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={keyword}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_unordered&media_type=all"
        self.driver.get(url)

        # 滚动页面以加载更多广告
        # self.scroll_page(wait_second)

        try:
            ad_elements = self.driver.find_elements(By.CLASS_NAME, "xh8yej3")
            if len(ad_elements) == 0:
                return
            time.sleep(2)  # 休眠一下 避免页面刷新获取不到
            for ad_element in ad_elements:
                ad_buttons = ad_element.find_elements(By.CSS_SELECTOR, ".x8t9es0.x1fvot60.xxio538.x1heor9g.xuxw1ft.x6ikm8r.x10wlt62.xlyipyv.x1h4wwuj.x1pd3egz.xeuugli")
                if len(ad_buttons) == 0:
                    continue
                i = 1
                time.sleep(2)  # 休眠一下 避免页面刷新获取不到
                for ad_button in ad_buttons:
                    print(ad_button.text.lower())
                    if ad_button.text.lower() in ["shop now", "去逛逛"]:  # 判断是否是独立站
                        ad_content, advertiser, advertiser_url, advertiser_domain = "", "", "", ""
                        ad_content_element = ad_element.find_element(By.CSS_SELECTOR, "._4ik4._4ik5")  # 广告内容
                        if ad_content_element:
                            ad_content = ad_content_element.text
                        advertiser_element = ad_element.find_element(By.CSS_SELECTOR, ".x8t9es0.x1fvot60.xxio538.x108nfp6.xq9mrsl.x1h4wwuj.x117nqv4.xeuugli")  # 广告商
                        if advertiser_element:
                            advertiser = advertiser_element.text
                        advertiser_url_element = ad_element.find_element(By.CSS_SELECTOR, ".x1hl2dhg.x1lku1pv.x8t9es0.x1fvot60.xxio538.xjnfcd9.xq9mrsl.x1yc453h.x1h4wwuj.x1fcty0u.x1lliihq")  # 落地页
                        if advertiser_url_element:
                            advertiser_url = advertiser_url_element.get_attribute("href")
                            if advertiser_url:
                                advertiser_domain = urlparse(advertiser_url).netloc  # 独立站域名
                        print(datetime.datetime.now())
                        print(f"下一个{i}个广告\r\n")
                        print("广告商:", advertiser)
                        print("广告内容:", ad_content)
                        print("广告产品url:", advertiser_url)
                        print("独立站域名:", advertiser_domain)
                        i+=1
        except StaleElementReferenceException:
            print("发生异常:", StaleElementReferenceException)

    # 滚动页面
    def scroll_page(self, wait_second):
        # 滚动到页面底部
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(wait_second)  # 根据需要调整等待时间
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def close(self):
        self.driver.quit()