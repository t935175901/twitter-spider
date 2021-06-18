import os
from config import *

data=[]
topic_find=re.compile(r"#[A-Za-z]\w*")
def run(x):
    #x=[
    # user_name,
    # since_date,
    # until_date,
    # ]
    print("{} is in statistics".format(x[0]))
    temp={"user_name":x[0],'topics':{}}
    datas = []
    fp = open_workbook(os.path.join(tweet_dir,'{}_{}_{}.xlsx'.format(x[0],x[1],x[2])))
    table = fp.sheets()[0]
    nrows = table.nrows
    keys=table.row_values(0)
    for n in range(1, nrows):
        datas.append(dict(zip(keys, table.row_values(n))))
    for n in datas:
        if n['retweet_from'].lower() ==x[0].lower():
            topics=topic_find.findall(n['text'])
            for topic in topics:
                if temp['topics'].get(topic):
                    temp['topics'][topic].append(n['tweet_id'])
                else:temp['topics'][topic]=[n['tweet_id']]
    data.append(temp)

#{'user_name':"",'topic':{topic1:{1535579,7895412}}}
if __name__ == "__main__":
    tweets = os.listdir(tweet_dir)
    datas = [["_".join(x[:-5].split("_")[:-2])]+x[:-5].split("_")[-2:] for x in tweets if "xlsx" in x]
    for x in datas:
        run(x)
    json.dump(data,open("topic_extract.json","w"))





