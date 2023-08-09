PREFIX: str = "facebook"

# cookie 存储
def cookie_key(username):
    return f"{PREFIX}:cookie:{username}"

# 账号数据
def account_key():
    return f"{PREFIX}:account"

# 国家数据
def country_key():
    return f"{PREFIX}:country"

# 广告数据临时存储
def ad_data_key():
    return f"{PREFIX}:ad:data"

# 关键字id标记
def keyword_id_key():
    return f"{PREFIX}:keyword:id"

# 分布式锁
def lock_key(name):
    return f"{PREFIX}:lock:{name}"