from multiprocessing.dummy import Pool  # 线程池
from selenium import webdriver
import twitter_tweet as tw
import os
import json
from config import *
from functools import reduce
tweet_dir = os.path.join(datadir, "tweet")
#去重
def list_dict_duplicate_removal(data_list):
    run_function = lambda x, y: x if y in x else x + [y]
    return reduce(run_function, [[], ] + data_list)

def run(x):
    #x=[
    # user_name,
    # since_date,
    # until_date,
    # ]
    driver = webdriver.Chrome()
    today = datetime.date.today()
    old_data=[]
    old_data += tw.SpiderTwitterAccountPost(driver).running(x[0], x[2],today)
    old_data += tw.SpiderTwitterAccountPost(driver).running(x[0], x[2],today, ifretweet=True)

    fp=open(os.path.join(tweet_dir,'{}_{}_{}.json'.format(x[0],x[1],x[2])), 'r', encoding='utf-8')
    old_data+=json.load(fp)
    new_data=list_dict_duplicate_removal(old_data)
    fp.close()
    os.remove(os.path.join(tweet_dir,'{}_{}_{}.json'.format(x[0],x[1],x[2])))
    fp=open(os.path.join(tweet_dir,'{}_{}_{}.json'.format(x[0],x[1],today)), 'w', encoding='utf-8')
    json.dump(new_data, fp=fp, ensure_ascii=False)
    fp.close()
if __name__ == "__main__":
    while(True):
        tweets = os.listdir(tweet_dir)
        datas = [re.split("_", x[:-5]) for x in tweets]
        for n in range(len(datas)):
            t1=[int(x) for x in datas[n][1].split("-")]
            t2=[int(x) for x in datas[n][2].split("-")]
            datas[n][1]=datetime.date(t1[0],t1[1],t1[2])
            datas[n][2]=datetime.date(t2[0],t2[1],t2[2])
        pool = Pool(pool_size)
        pool.map(run, datas)
        pool.close()
        pool.join()
        print("This round of update has been completed. Update time:{}".format(datetime.datetime.now()))
        time.sleep(update_interval)




