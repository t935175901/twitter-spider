import time
import re
from selenium.webdriver.common.keys import Keys
email = "ty_enh"
#登录邮箱，建议换成自己的
password = "ty20000924"
#密码
file_path="user_names.txt"
#待爬取用户文件路径
num=2
#线程池大小

def login (driver, email, password):
    driver.get("https://twitter.com/login")
    driver.find_element_by_name('session[username_or_email]').send_keys(email)
    #insert username
    driver.find_element_by_name('session[password]').send_keys(password)
    #insert password
    driver.find_element_by_name('session[password]').send_keys(Keys.RETURN)
    time.sleep(2)

def get_twitter_user_name(page_url: str) -> str:
    """提取Twitter的账号用户名称
    主要用于从Twitter任意账号页的Url中提取账号用户名称
    :param page_url: Twitter任意账号页的Url
    :return: Twitter账号用户名称
    """
    if pattern := re.search(r"(?<=twitter.com/)[^/]+", page_url):
        return pattern.group()
    return page_url
