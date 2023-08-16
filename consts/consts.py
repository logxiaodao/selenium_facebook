
# mysql 相关配置
MYSQL_MAX_ROW: int = 10000   # 单次查询最大条数
FB_AD_COUNTRY: str = "fb_ad_country"   # facebook 国家表
FB_AD_USER: str = "fb_ad_user"   # facebook 用户表
FB_AD_KEYWORD: str = "fb_ad_keyword"   # facebook 关键字表
FB_AD_DATA: str = "fb_ad_data"   # facebook 广告数据表
FB_FILTER_DOMAIN: str = "fb_filter_domain"   # facebook 域名过滤表
OMS_KEYWORD: str = "oms_keyword"   # facebook 关键字表



# 表字段配置
# -------------- fb_filter_domain 域名过滤表 ---------------
#  status 状态
FB_FILTER_DOMAIN_STATUS_ON = 1   # 启用
FB_FILTER_DOMAIN_STATUS_OFF = 2  # 停用
# rule 规则
FB_FILTER_DOMAIN_RULE_LIKE: str = "like"  # 模糊匹配
FB_FILTER_DOMAIN_RULE_EQ: str = "eq"    # 全匹配


# -------------- fb_ad_data 广告数据表 ---------------
#  is_jewelry 是否首饰站
FB_AD_DATA_IS_JEWELRY_YES = 1  # 是
FB_AD_DATA_IS_JEWELRY_NO = 2   # 不是


# -------------- fb_ad_keyword 关键字表 ---------------
#  is_crawling 是否需要爬去数据
FB_AD_KEYWORD_IS_CRAWLING_DEFAULT = 1  # 未知
FB_AD_KEYWORD_IS_CRAWLING_YES = 2  # 需要
FB_AD_KEYWORD_IS_CRAWLING_NO = 3   # 不需要
#  status 状态
FB_AD_KEYWORD_STATUS_DEFAULT = 1   # 未知
FB_AD_KEYWORD_STATUS_ON = 2   # 启用
FB_AD_KEYWORD_STATUS_OFF = 3  # 停用
#  category 分类
FB_AD_KEYWORD_CATEGORY_HEAD_WEAR = 1  # 头(发)饰
FB_AD_KEYWORD_CATEGORY_NECKLACE = 2  # 项链
FB_AD_KEYWORD_CATEGORY_BRACELET_OR_ANKLET = 3  # 手(脚)镯
FB_AD_KEYWORD_CATEGORY_RING = 4  # 戒指
FB_AD_KEYWORD_CATEGORY_EARRING = 5  # 耳(钉)环
FB_AD_KEYWORD_CATEGORY_BODY_JEWELRY = 6  # 身体首饰
FB_AD_KEYWORD_CATEGORY_BROOCH = 7  # 胸针
FB_AD_KEYWORD_CATEGORY_OTHER = 8  # 其他


# -------------- fb_ad_country 国家表 ---------------
#  is_crawling 是否需要爬去数据
FB_AD_COUNTRY_IS_CRAWLING_DEFAULT = 1  # 未知
FB_AD_COUNTRY_IS_CRAWLING_YES = 2  # 需要
FB_AD_COUNTRY_IS_CRAWLING_NO = 3   # 不需要


# -------------- fb_ad_user 用户表 ---------------
#  status 状态
FB_AD_USER_STATUS_DEFAULT = 1  # 未知
FB_AD_USER_STATUS_ON = 2  # 启用
FB_AD_USER_STATUS_OFF = 3  # 停用


# -------------- oms_keyword 关键字表 ---------------
#  is_crawling 是否需要爬去数据
OMS_KEYWORD_IS_CRAWLING_DEFAULT = 1  # 未知
OMS_KEYWORD_IS_CRAWLING_YES = 2  # 需要
OMS_KEYWORD_IS_CRAWLING_NO = 3   # 不需要
#  status 状态
OMS_KEYWORD_STATUS_DEFAULT = 1   # 未知
OMS_KEYWORD_STATUS_ON = 2   # 启用
OMS_KEYWORD_STATUS_OFF = 3  # 停用