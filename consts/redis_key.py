PREFIX: str = "facebook"


# cookie 存储
def cookie_key(username):
    return f"{PREFIX}:cookie:{username}"

# 账号数据
def account_key():
    return f"{PREFIX}:account"

# 广告数据临时存储
def ad_data_key():
    return f"{PREFIX}:ad:data"
