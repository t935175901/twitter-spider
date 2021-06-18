
from config import *

import json
if __name__ == "__main__":
    user_names = []
    with open(file_path, "r") as fp:  # 读取待爬取用户用户名
        for line in fp:
            temp=line.strip().replace("\t"," ").split("  ")
            if temp[1]!="TRUE":
                user_names.append(get_twitter_user_name(temp[0]).lower())
    #already=json.load(open("data/following/followers_you_know.json","r"))
    #temp=[x.lower() for x in already["following"]]
    n=len(user_names)
    if not os.path.isdir(datadir):
        os.mkdir(datadir)
    driver = webdriver.Chrome()
    login(driver, email, password)
    x=0
    while (x<n):
        if 1:#user_names[x] not in temp:
            print(x)
            following_url = "https://twitter.com/{}".format(user_names[x])
            driver.get(following_url)
            time.sleep(2)
            try:
                a = driver.find_elements_by_xpath('//*[@data-testid="placementTracking"]/div')
                # if len(a)==3:
                #     find=driver.find_element_by_css_selector("main > div > div > div > div > div > div:nth-child(2) > div > div > div:nth-child(1) > div > div"
                #              " > div > div:nth-child(3) > div > div > div > span > span")
                #     a.find_element_by_link_text("关注")
                # else:
                #     find = driver.find_element_by_css_selector(
                #         "main > div > div > div > div > div > div:nth-child(2) > div > div > div:nth-child(1) > div > div"
                #         " > div > div:nth-child(2) > div > div > div > span > span")
                if "正在关注" not in a[0].text:
                    a[0].click()
                    time.sleep(2)
                x += 1
            except:
                pass
                time.sleep(1)
                # 为了避免网络波动导致的未能及时加载
        else:
            x+=1




