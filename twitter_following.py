# coding:utf-8
from config import *
flags=[]
datas=[]
record=0
str=lambda a:int(float(a.replace(",","").split("万")[0])*10000) if len(a.split("万"))==2 else int(a.replace(",",""))
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
        flag=False
        self.user_name = user_name
        # 生成请求的Url

        person_url="https://twitter.com/{}".format(user_name)
        while 1:
            try:
                self.driver.get(person_url)
                time.sleep(3)
                following_num = str(self.driver.find_element_by_xpath(
                    "//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div[1]/div/div/div[1]/a/span[1]/span").text)
                follower_num = str(self.driver.find_element_by_xpath(
                    "//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div[1]/div/div/div[2]/a/span[1]/span").text)
                break
            except:
                print("wait 2 sec")
                time.sleep(2)
        following_url = "https://twitter.com/{}/followers_you_follow".format(user_name)
        #following_url = "https://twitter.com/{}/following".format(user_name)
        # 打开目标Url

        while 1:
            try:
                self.driver.get(following_url)
                time.sleep(3)
                try:
                    if "还没有你认识的任何关注者" in self.driver.find_element_by_xpath(
                            "//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div[1]/span").text:
                        print("nothing")
                        return {"user_name": user_name, "following_num": following_num, "follower_num": follower_num,
                                "following": []}, flag
                except:
                    pass
                # 循环遍历外层标签
                following_set = set()
                for _ in range(1000):
                    last_label_user = None
                    for label_user in self.driver.find_elements_by_xpath(
                            '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/section/div/div/div'):  # 定位到推文标签
                        try:
                            label = label_user.find_element_by_css_selector("div > div > div > div > div> div> a")
                        except:
                            break
                        if pattern := label.get_attribute("href"):  # 读取用户名
                            t = get_twitter_user_name(pattern)
                        if t in following_set:
                            continue
                        following_set.add(t)
                        last_label_user = label_user

                    # 向下滚动到最下面的一条推文
                    if last_label_user is not None:
                        self.driver.execute_script("arguments[0].scrollIntoView();", last_label_user)  # 滑动到推文标签
                        self.console("执行一次向下翻页...")
                        time.sleep(2.5)
                    else:
                        flag = True
                        break
                return {"user_name": user_name, "following_num": following_num, "follower_num": follower_num,
                        "following": list(following_set)}, flag

            except:
                print("wait 2 sec")
                time.sleep(2)

        # 定位标题外层标签


def run(user_name):
    print("Start collecting following list of {}:".format(user_name))
    datas.append(SpiderTwitterAccountFollowList(driver).running(user_name)[0])
    print("Collection complete ")



# ------------------- 单元测试 -------------------
driver = webdriver.Chrome()
login(driver, email, password)
#解决办法：并去掉run中该部分
if __name__ == "__main__":
    user_names = []
    with open(file_path, "r") as fp:  # 读取待爬取用户用户名
        for line in fp:
            temp = line.strip().replace("\t", " ").split("  ")
            if 1:#temp[1] != "TRUE":
                user_names.append(get_twitter_user_name(temp[0]))
    if not os.path.isdir(datadir):
        os.mkdir(datadir)
    pool = Pool(1)
    #池子太大导致频繁登录极易被发现而登录异常，解决方法之一是仅开一个driver只登录一次但必须依次线性爬取
    pool.map(run, user_names)
    pool.close()
    pool.join()
    path = os.path.join(datadir, "following")
    if not os.path.isdir(path):
        os.mkdir(path)
    fp = open(os.path.join(path, 'followers_you_following.json'), 'w', encoding='utf-8')
    json.dump(datas, fp=fp, ensure_ascii=False)


