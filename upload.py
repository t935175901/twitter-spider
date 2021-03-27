import requests as re
import json
import pandas as pd
import os
import xlrd
import operator

path = "data/tweet"

class UploadTweets:
    def upload(self):
        df = pd.read_csv("data.csv", usecols=[0,1])
        print(df.head(5))
        twitterIds = df['twitterid'].values.tolist()
        twitterIds = [i.lower() for i in twitterIds]
        names = df['name'].values.tolist()
        # print(twitterIds, '\n', names)

        fs = os.listdir(path)
        for file in fs:
            try:
                twitterId = file.split('_')[0].lower()
                name = names[twitterIds.index(twitterId)]
                print(file, name)
                r = re.get('http://test.xuejun.ziqiang.net.cn/person/personByName?name='+name)
                id = json.loads(r.text)['data']['id']

                tweets = read_xlsx(path+'/'+file)
                for tweet in tweets:
                    tweet['ownerId'] = int(id)
                    if tweet['retweetFrom'].lower() == twitterId.lower():
                        del tweet['retweetFrom']
                    else:
                        if tweet['retweetFrom'].lower() in twitterIds:
                            retweetName = names[twitterIds.index(tweet['retweetFrom'].lower())]
                            r = re.get('http://test.xuejun.ziqiang.net.cn/person/personByName?name='+retweetName)
                            tweet['retweetFrom'] = int(json.load(r.text)['data']['id'])
                        else:
                            #creat_person()
                            tweet['retweetFrom'] = int(id)
                    if tweet['replyTo'].lower() in twitterIds:
                        replyName = names[twitterIds.index(tweet['replyTo'].lower())]
                        r = re.get('http://test.xuejun.ziqiang.net.cn/person/personByName?name='+replyName)
                        tweet['replyTo'] = int(json.load(r.text)['data']['id'])
                    else:
                        #creat_person()
                        tweet['replyTo'] = int(id)

                headers = {'Content-Type': 'application/json'}
                response = re.post(url='http://test.xuejun.ziqiang.net.cn/activity/addOrUpdateActivities', headers=headers, data=json.dumps(tweets))
                print(json.loads(response.text))

            except:
                print("读取推文文件失败")

def creat_person():
    pass



def read_xlsx(filename):
    # 打开excel文件
    data1 = xlrd.open_workbook(filename)
    # 读取第一个工作表
    table = data1.sheets()[0]
    # 统计行数
    n_rows = table.nrows

    data = []

    # 微信文章属性：wechat_name wechat_id title abstract url time read like number
    for v in range(1, n_rows - 1):
        # 每一行数据形成一个列表
        values = table.row_values(v)
        # 列表形成字典
        data.append({
                    "ownerId": 0,
                    "retweetFrom": values[1],
                    "time": values[2],
                    "replyTo": values[3],
                    "content": values[4],
                    "replies": int(values[5]),
                    "retweet": int(values[6]),
                    "likes": int(values[7]),
                    "imageUrl": values[8]
                     })
    # 返回所有数据
    return data

if __name__ == '__main__':
    upLoader = UploadTweets()
    upLoader.upload()
