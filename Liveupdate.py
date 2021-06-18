

import overlength_tweet as ot
from config import *


logging.basicConfig(filename='logger.log', level=logging.INFO)


def run(x):
    #x=[
    # user_name,
    # since_date,
    # until_date,
    # ]
    if users[x[0]]==1:
        print("has")
        return None
    datas = []
    fp = open_workbook(os.path.join(tweet_dir,'{}_{}_{}.xlsx'.format(x[0],x[1],x[2])))
    table = fp.sheets()[0]
    nrows = table.nrows
    keys=table.row_values(0)
    for n in range(1, nrows):
        datas.append(dict(zip(keys, table.row_values(n))))
    driver = webdriver.Chrome()
    #datas = list_dict_duplicate_removal(ot.SpiderTwitterAccountPost(driver).running(x[0], x[2])+datas)#确保时间顺序并去重
    new_datas=ot.SpiderTwitterAccountPost(driver).running(x[0], x[2])
    driver.quit()
    #os.remove(os.path.join(tweet_dir,'{}_{}_{}.xlsx'.format(x[0],x[1],x[2])))
    datas=[data for data in new_datas if data not in datas]
    if len(datas)<10:
        logging.warning("WARN:number of {}'s tweets is only {}".format(x[0],len(datas)))
    if len(datas)>0 and (datetime.datetime.strptime(datas[-1]['time'][:10], "%Y-%m-%d").date()-x[2]).days<8:
        users[x[0]]=1
    else:
        users[x[0]]=15

    wb = workbook.Workbook()
    ws = wb.active
    ws.append(
        ["tweet_id", "retweet_from", "time", "reply_to", "text", "replies", "retweets", "likes", "images"])
    for data in datas:
        ws.append([data["tweet_id"], data["retweet_from"], data["time"], data["reply_to"], data["text"],
                   data["replies"], data["retweets"], data["likes"], data["images"]])
    if not update_dir:
        os.mkdir(update_dir)
    file_path = os.path.join(update_dir, '{}_{}_{}.xlsx'.format(x[0], x[2], today))
    wb.save(file_path)
    f = open('logging.json', 'w')
    f.write(json.dumps(users))
    f.close()
f=open('logging.json','r')
users=json.loads(f.read())
f.close()
if __name__ == "__main__":
    logging.info('Start update :{}'.format(datetime.datetime.now()))
    tweets = os.listdir(tweet_dir)
    datas = [["_".join(x[:-5].split("_")[:-2])]+x[:-5].split("_")[-2:] for x in tweets if "xlsx" in x]
    for n in range(len(datas)):
        t1=[int(x) for x in datas[n][1].split("-")]
        t2=[int(x) for x in datas[n][2].split("-")]
        datas[n][1]=datetime.date(t1[0],t1[1],t1[2])
        datas[n][2]=datetime.date(t2[0],t2[1],t2[2])
    pool = Pool(pool_size)
    pool.map(run, datas)
    pool.close()
    pool.join()
    print("Update has been completed. Update time:{}".format(datetime.datetime.now()))
    #time.sleep(update_interval)




