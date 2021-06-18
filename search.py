# coding:utf-8

"""
Twitter账号推文爬虫
@Update: 2021.03.10
"""

from langdetect import detect
from openpyxl import workbook  # 写入Excel表所用
from openpyxl import load_workbook  # 读取Excel表所用
from urllib import parse
import json
import crawlertool as tool
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from config import *
import datetime

class SpiderTwitterSearching(tool.abc.SingleSpider):
    """
    Twitter账号推文爬虫
    """
    def __init__(self, driver):
        self.driver = driver
        # 爬虫实例的变量
        self.word = None

    def running(self, word: str):
        """执行Twitter账号推文爬虫
        :param user_name: twitter账号主页名称（可以通过get_facebook_user_name获取）
        :param since_date: 抓取时间范围的右侧边界（最早日期）
        :param until_date: 抓取时间范围的左侧边界（最晚日期）
        :return: 推文信息列表
        """
        flag=False#判断是否正常退出
        self.word = word
        item_list = []
        if self.word[0]=='#':
            # 生成请求的Url
            temp =self.word
        else:
            temp ='"'+self.word+'"'
        params = {
            "q": temp+" min_faves:5"
        }
        actual_url = "https://twitter.com/search?" + parse.urlencode(params)
        self.console("实际请求Url:" + actual_url)

        # 打开目标Url
        self.driver.get(actual_url)
        time.sleep(5)

        # 判断是否该账号在指定时间范围内没有发文
        tweet_exist = True
        try:
            label_test = self.driver.find_element_by_css_selector(
                "main>div>div>div>div>div>div:nth-child(2) >div>div>div>div:nth-child(2) ")
            if "你输入的词没有找到任何结果" in label_test.text:
                tweet_exist = False
        except NoSuchElementException:
            print("{} found".format(word))
        if not tweet_exist:
            print("{} not found".format(word))
            return item_list

        # 定位标题外层标签
        # label_outer = self.driver.find_element_by_css_selector(
        #     "main > div > div > div > div:nth-child(1) > div > div:nth-child(2) > div > div > section > div > div")
        # self.driver.execute_script("arguments[0].id = 'outer';", label_outer)  # 设置标题外层标签的ID
        # 循环遍历外层标签
        tweet_id_set = set()
        while(1):
            last_label_tweet = None
            for label_tweet in self.driver.find_elements_by_xpath('//*[@data-testid="tweet"]'):  # 定位到推文标签

                item = {}
                try:
                    label = label_tweet.find_element_by_css_selector(
                        "article > div > div > div > div:nth-child(2) > div:"
                        "nth-child(2) > div:nth-child(1) > div > div > div:nth-child(1) > a")
                # 读取推文ID
                except:
                    #break
                    continue
                if pattern := re.search("[0-9]+$", label.get_attribute("href")):
                    item["tweet_id"] = pattern.group()
                if "tweet_id" not in item:
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
                    item["retweet_from"] = ""
                # 解析推文发布时间
                if label := label_tweet.find_element_by_css_selector(
                        "article > div > div > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div > div > div:nth-child(1) > a > time"):
                    timeOrg = datetime.datetime.strptime(
                        label.get_attribute("datetime").replace("T", " ").replace(".000Z", ""), "%Y-%m-%d %H:%M:%S")
                    deltaH = datetime.timedelta(hours=8)
                    timeRec = timeOrg + deltaH
                    item["time"] = timeRec.strftime("%Y-%m-%d %H:%M:%S")
                    # 消除时区偏差+8h

                # 判断是推文还是回复
                item["reply_to"] = ""
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


                # 爬取推文反馈数据
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
                temp=item["text"].strip()
                if len(temp)>=50:
                    try:
                        if detect(temp)=="en":
                            item_list.append(temp)
                    except:
                        pass

            # 向下滚动到最下面的一条推文
            if last_label_tweet is not None and len(item_list)<300:
                self.driver.execute_script("arguments[0].scrollIntoView();", last_label_tweet)  # 滑动到推文标签
                print("执行一次向下翻页...",len(item_list))
                time.sleep(4)
            else:
                flag=True
                break

        return item_list,flag

def run(words):

    num=len(words)
    n=0
    flags=[]
    while(n<num):
        datas=[]
        wb = workbook.Workbook()  # 创建Excel对象
        ws = wb.active  # 获取当前正在操作的表对象
        # 往表中写入标题行,以列表形式写入！
        ws.append(['keyword', 'text'])
        datas,flag=SpiderTwitterSearching(driver).running(words[n])
        flags.append(flag)
        for k in range(len(datas)):
            ws.append([words[n],datas[k]])
        wb.save('data\\test\\{}.xlsx'.format(words[n]))
        n+=1
    print(flags)


driver = webdriver.Chrome()
# ------------------- 单元测试 -------------------
if __name__ == "__main__":
    key_words = []
    with open("keywords.txt", "r") as fp:  # 读取待爬取用户用户名
        for line in fp:
            key_words.append(line.strip())
    run(key_words)

