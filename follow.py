# coding:utf-8
import re
import time

import json
import crawlertool as tool
from multiprocessing.dummy import Pool  # 线程池
from selenium import webdriver
from selenium.webdriver.common.keys import Keys



def login(driver,email,password):
	driver.get("https://twitter.com/login")
	driver.find_element_by_name('session[username_or_email]').send_keys(email)
	# insert username
	driver.find_element_by_name('session[password]').send_keys(password)
	# insert password
	driver.find_element_by_name('session[password]').send_keys(Keys.RETURN)
	time.sleep(2)

class SpiderTwitterAccountFollowList(tool.abc.SingleSpider):
    """
    Twitter账号推文爬虫
    """

    def __init__(self, driver):
        self.driver = driver

        # 爬虫实例的变量
        self.user_name = None

    @staticmethod
    def get_twitter_user_name(page_url: str) -> str:
        """提取Twitter的账号用户名称
        主要用于从Twitter任意账号页的Url中提取账号用户名称
        :param page_url: Twitter任意账号页的Url
        :return: Twitter账号用户名称
        """
        if pattern := re.search(r"(?<=twitter.com/)[^/]+", page_url):
            return pattern.group()

    def running(self, user_name: str):
        """
        :param user_name: twitter账号主页名称（可以通过get_facebook_user_name获取）
        :return: 关注列表和被关注列表
        """
        self.user_name = user_name
        # 生成请求的Url
        # follower_url="https://twitter.com/{}/followers".format(user_name)
        following_url = "https://twitter.com/{}/following".format(user_name)

        # 打开目标Url
        self.driver.get(following_url)
        time.sleep(1)


        # 定位标题外层标签
        label_outer = self.driver.find_element_by_css_selector(
            "main>div>div>div>div>div>div:nth-child(2)>section>div>div")
        # 循环遍历外层标签
        following_set = set()
        for _ in range(1000):
            last_label_user = None
            for label_user in label_outer.find_elements_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/section/div/div/div'):  # 定位到推文标签
                try:label = label_user.find_element_by_css_selector("div > div > div > div > div> div> a")

                except:
                    break
                if pattern :=label.get_attribute("href"):                # 读取用户名
                    t=self.get_twitter_user_name(pattern)
                if t in following_set:
                    continue
                following_set.add(t)
                last_label_user = label_user

            # 向下滚动到最下面的一条推文
            if last_label_user is not None:
                self.driver.execute_script("arguments[0].scrollIntoView();", last_label_user)  # 滑动到推文标签
                self.console("执行一次向下翻页...")
                time.sleep(1)
            else:
                break
        fp = open('twitter_following_{}.json'.format(user_name), 'w', encoding='utf-8')
        json.dump({"user_name":user_name,"following":list(following_set)}, fp=fp, ensure_ascii=False)
        print("{} is done".format(user_name))

# ------------------- 单元测试 -------------------
if __name__ == "__main__":
    user_name = "SpeakerPelosi"
    email="935175901@qq.com"
    password="ty20000924"
    driver = webdriver.Chrome()

    login(driver,email,password)
    #follower_url="https://twitter.com/{}/followers".format(user_name)
    following_url="https://twitter.com/{}/following".format(user_name)
    driver.get(following_url)
    SpiderTwitterAccountFollowList(driver).running(user_name)

    time.sleep(3)
    driver.quit()
