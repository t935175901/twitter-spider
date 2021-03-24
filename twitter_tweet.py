# coding:utf-8

"""
Twitter账号推文爬虫
@Update: 2021.03.21
"""

import crawlertool as tool
from multiprocessing.dummy import Pool  # 线程池
from selenium import webdriver
from config import *
import datetime
import os
from openpyxl import workbook  # 写入Excel表所用
flags=[]#标识是否爬取成功
class SpiderTwitterAccountPost(tool.abc.SingleSpider):
    """
    Twitter账号推文爬虫
    """
    def __init__(self, driver):
        self.driver = driver
        # 爬虫实例的变量
        self.user_name = None

    def running(self, user_name: str, since_date):
        """执行Twitter账号推文爬虫
        :param user_name: twitter账号主页名称（可以通过get_facebook_user_name获取）
        :param since_date: 抓取时间范围的右侧边界（最早日期）
        :return: 推文信息列表
        """
        flag=False#判断搜索完全与否
        self.user_name = user_name
        item_list = []
        actual_url="https://twitter.com/{}/with_replies".format(self.user_name)
        self.driver.get(actual_url)
        time.sleep(6)
        while (1):
            try:
                temp=self.driver.find_elements_by_xpath('//*[@data-testid="tweet"]')
                break
            except:
                self.driver.refresh()
                time.sleep(3)
                pass


        # 循环遍历外层标签
        tweet_id_set = set()
        while(1):
            last_label_tweet = None
            while(1):
                try:
                    temp=self.driver.find_elements_by_xpath('//*[@data-testid="tweet"]')
                    break
                except:
                    time.sleep(1)
            for label_tweet in temp:  # 定位到推文标签

                item = {}
                label = label_tweet.find_element_by_css_selector(
                    "article > div > div > div > div:nth-child(2) > div:"
                    "nth-child(2) > div:nth-child(1) > div > div > div:nth-child(1) > a")
                # 读取推文ID

                if pattern := re.search("[0-9]+$", label.get_attribute("href")):
                    item["tweet_id"] = pattern.group()
                if "tweet_id" not in item:
                    self.log("账号名称:" + user_name + "|未找到推文ID标签(第" + str(len(item_list)) + "条推文)")
                    continue

                # 判断推文是否已被抓取(若未被抓取则解析推文)
                if item["tweet_id"] in tweet_id_set:
                    continue

                tweet_id_set.add(item["tweet_id"])
                last_label_tweet = label_tweet

                # 解析推文来源,判断转推与否
                try:
                    if label := label_tweet.find_element_by_css_selector(
                            "article > div > div > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > a > div > div:nth-child(2) > div > span"):
                        item["retweet_from"] = label.text.replace("@", "")
                except:
                    item["retweet_from"]=""
                # 解析推文发布时间
                if label := label_tweet.find_element_by_css_selector(
                        "article > div > div > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div > div > div:nth-child(1) > a > time"):
                    timeOrg = datetime.datetime.strptime(label.get_attribute("datetime").replace("T", " ").replace(".000Z", ""), "%Y-%m-%d %H:%M:%S")
                    deltaH = datetime.timedelta(hours=8)
                    timeRec = timeOrg + deltaH
                    item["time"] = timeRec.strftime("%Y-%m-%d %H:%M:%S")
                    #消除时区偏差+8h


                # 判断是推文还是回复
                item["reply_to"]=""
                if label := label_tweet.find_element_by_css_selector(
                        "article > div > div > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1)"):
                    if "回复" in label.text and "@" in label.text:
                         # 解析回复内容
                        item["reply_to"] = label.text.replace("回复", "")
                        item["reply_to"] = item["reply_to"].replace("@", "")
                        item["reply_to"] = item["reply_to"].replace(" ", "")
                        item["reply_to"] = item["reply_to"].replace("\n", "").replace("\r", "")
                        if label2 := label_tweet.find_element_by_css_selector(
                                "article > div > div > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div:nth-child(2)"):
                            item["text"] = label2.text
                    else:
                        # 解析推文内容
                        item["text"] = label.text
                # 爬取推文图片
                item["images"] = ""
                image_url = ""

                    # 定位图片外层标签
                lable_image = label_tweet.find_elements_by_xpath('.//img[@alt="图像"]')
                for image in lable_image:
                    try:
                        image_url = image.get_attribute("src")
                        if len(image_url):
                            image_url += ' '
                            item["images"] += image_url
                    except:
                        pass
                item["replies"] = 0  # 推文回复数
                item["retweets"] = 0  # 推文转推数
                item["likes"] = 0  # 推文喜欢数

                # 定位到推文反馈数据标签
                if label := label_tweet.find_element_by_css_selector(
                        "article > div > div > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div[role='group']"):
                    if text := label.get_attribute("aria-label"):
                        # 解析推文反馈数据
                        for feedback_item in text.split("、"):
                            if "回复" in feedback_item:
                                if pattern := re.search("[0-9]+", feedback_item):
                                    item["replies"] = int(pattern.group())
                            elif "转推" in feedback_item:
                                if pattern := re.search("[0-9]+", feedback_item):
                                    item["retweets"] = int(pattern.group())
                            elif "喜欢" in feedback_item:
                                if pattern := re.search("[0-9]+", feedback_item):
                                    item["likes"] = int(pattern.group())
                if (timeRec.date()-since_date).days<0 and item["retweet_from"].lower()==self.user_name.lower():
                    return item_list,True
                #if item["retweet_from"] !=self.user_name:
                item_list.append(item)


            # 向下滚动到最下面的一条推文
            if last_label_tweet is not None :
                self.driver.execute_script("arguments[0].scrollIntoView();", last_label_tweet)  # 滑动到推文标签
                #print("执行一次向下翻页...",self.user_name,len(item_list))
                time.sleep(2)
            else:
                flag=True
                break
        return item_list,flag

def run(x):
    #x=
    # user_name,
    # since_date,
    # until_date]
    driver = webdriver.Chrome()
    datas=[]
    print("Start collecting tweets from {}:".format(x[0]))
    wb = workbook.Workbook()  # 创建Excel对象
    ws = wb.active  # 获取当前正在操作的表对象
    # 往表中写入标题行,以列表形式写入！
    ws.append(["tweet_id", "retweet_from","time","reply_to","text","replies","retweets", "likes","images"])
    datas,flag = SpiderTwitterAccountPost(driver).running(x[0], x[1])
    flags.append(flag)
    for data in datas:
        ws.append([data["tweet_id"],data["retweet_from"],data["time"],data["reply_to"],data["text"],data["replies"],data["retweets"],data["likes"],data["images"]])
    driver.quit()
    path=os.path.join(datadir,"tweet")
    if not os.path.isdir(path):
        os.mkdir(path)
    file_path=os.path.join(path,'{}_{}_{}.xlsx'.format(x[0], x[1],today))
    wb.save(file_path)
    print("Collection complete\n")



# ------------------- 单元测试 -------------------
if __name__ == "__main__":
    user_names = ["senmarkkelly"]
    # with open(file_path, "r") as fp:  # 读取待爬取用户用户名
    #     for line in fp:
    #         user_names.append(get_twitter_user_name(line.strip()))
    # fp.close()
    if not os.path.isdir(datadir):
        os.mkdir(datadir)
    pool = Pool(pool_size)
    combe = lambda user_names, since_date: list(zip(user_names, [since_date] * len(user_names)))
    pool.map(run, combe(user_names,since_date))
    pool.close()
    pool.join()
    print(flags)


