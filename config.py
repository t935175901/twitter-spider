import time
import re
from selenium.webdriver.common.keys import Keys
import datetime
import os
from tqdm import tqdm
import pandas as pd
import json
import logging
import numpy as np
import crawlertool as tool
from multiprocessing.dummy import Pool  # 线程池
from selenium import webdriver
from urllib import parse
from xlrd import open_workbook
from openpyxl import workbook  # 写入Excel表所用
#email = ""
email = ""
#登录邮箱
password = ""
#密码
file_path="user_names.txt"
#待爬取用户文件路径
pool_size=2
#线程池大小
since = datetime.date(2020, 1, 1)
today = datetime.date.today()
#统计开始结束时间
datadir="data"
tweet_dir = os.path.join(datadir, "tweet_sum")
update_dir=os.path.join(datadir, "tweet_newest")
#数据文件夹


def login (driver, email, password):
    driver.get("https://twitter.com/login")
    time.sleep(2)
    driver.find_element_by_name('session[username_or_email]').send_keys(email)
    #insert username
    driver.find_element_by_name('session[password]').send_keys(password)
    #insert password
    driver.find_element_by_name('session[password]').send_keys(Keys.RETURN)
    print("Login successful")
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
