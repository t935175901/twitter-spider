# coding:utf-8
import json
import crawlertool as tool
from multiprocessing.dummy import Pool  # 线程池
from selenium import webdriver
from config import *
import os


class SpiderTwitterAccountFollowList(tool.abc.SingleSpider):
    """
    Twitter账号following列表爬虫
    """
    def __init__(self, driver):
        self.driver = driver
        # 爬虫实例的变量
        self.user_name = None

    def running(self, user_name: str):
        """
        :param user_name: twitter账号主页名称（可以通过get_facebook_user_name获取）
        :return: 关注列表和被关注列表
        """
        self.user_name = user_name
        # 生成请求的Url
        following_url = "https://twitter.com/{}/followers_you_follow".format(user_name)

        # 打开目标Url
        self.driver.get(following_url)
        time.sleep(3)

        # 定位标题外层标签
        try:
            label_outer = self.driver.find_element_by_css_selector(" main > div > div > div > div > div >"
                                                               " div:nth-child(2) > section > div > div")
        except:
            print("Find nothing")
            return {"user_name": user_name, "following": []}
        # 循环遍历外层标签
        following_set = set()
        for _ in range(1000):
            last_label_user = None
            for label_user in label_outer.find_elements_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/section/div/div/div'):  # 定位到推文标签
                try:label = label_user.find_element_by_css_selector("div > div > div > div > div> div> a")

                except:
                    break
                if pattern :=label.get_attribute("href"):       # 读取用户名
                    t=get_twitter_user_name(pattern)
                if t in following_set:
                    continue
                following_set.add(t)
                last_label_user = label_user

            # 向下滚动到最下面的一条推文
            if last_label_user is not None:
                self.driver.execute_script("arguments[0].scrollIntoView();", last_label_user)  # 滑动到推文标签
                self.console("执行一次向下翻页...")
                time.sleep(1.5)
            else:
                break
        return {"user_name":user_name,"following":list(following_set)}

def run(user_name):
    print("Start collecting following list of {}:".format(user_name))
    path = os.path.join(datadir, "following")
    if not os.path.isdir(path):
        os.mkdir(path)
    fp = open(os.path.join(path, '{}_following.json'.format(user_name)), 'w', encoding='utf-8')
    json.dump(SpiderTwitterAccountFollowList(driver).running(user_name), fp=fp, ensure_ascii=False)
    print("Collection complete")



# ------------------- 单元测试 -------------------
driver = webdriver.Chrome()
login(driver, email, password)
#解决办法：并去掉run中该部分
if __name__ == "__main__":
    user_names = []
    with open(file_path, "r") as fp:  # 读取待爬取用户用户名
        for line in fp:
            user_names.append(get_twitter_user_name(line.strip()))
    if not os.path.isdir(datadir):
        os.mkdir(datadir)
    pool = Pool(1)
    #池子太大导致频繁登录极易被发现而登录异常，解决方法之一是仅开一个driver只登录一次但必须依次线性爬取
    pool.map(run, user_names)
    pool.close()
    pool.join()


