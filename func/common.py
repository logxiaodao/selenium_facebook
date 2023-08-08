import random

# 去掉facebook链接
def remove_facebook_redirect(url):
    prefix = 'https://l.facebook.com/l.php?u='
    if url.startswith(prefix):
        url = url.replace(prefix, '')
    return url

# 生成一个随机数
def random_int():
    my_list = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    number = random.choice(my_list)
    return number