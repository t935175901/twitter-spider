
from config import *


logging.basicConfig(filename='logger.log', level=logging.INFO)


if __name__ == "__main__":
    logging.info('Start merge :{}'.format(datetime.datetime.now()))
    old_tweets = os.listdir(tweet_dir)
    old_datas = np.array([["_".join(x[:-5].split("_")[:-2])]+x[:-5].split("_")[-2:] for x in old_tweets if "xlsx" in x])
    old_datas=pd.DataFrame(old_datas,columns=['name','since1','until1'])
    update_tweets = os.listdir(update_dir)
    update_datas = np.array([["_".join(x[:-5].split("_")[:-2])] + x[:-5].split("_")[-2:] for x in update_tweets if "xlsx" in x])
    update_datas=pd.DataFrame(update_datas,columns=['name','since2','until2'])
    new=pd.merge(old_datas,update_datas,on='name')
    for indexs in tqdm(new.index):
        datas=[]
        now=new.loc[indexs].values[:]
        fp = open_workbook(os.path.join(tweet_dir, '{}_{}_{}.xlsx'.format(now[0], now[1], now[2])))
        table = fp.sheets()[0]
        nrows = table.nrows
        for n in range(0, nrows):
            datas.append(table.row_values(n))
        fp = open_workbook(os.path.join(update_dir, '{}_{}_{}.xlsx'.format(now[0], now[3], now[4])))
        table = fp.sheets()[0]
        nrows = table.nrows
        for n in range(0, nrows):
            datas.append(table.row_values(n))
        datas.sort(key=lambda x:x[2],reverse=1)
        wb = workbook.Workbook()
        ws = wb.active
        for data in datas:
            ws.append(data)
        file_path = os.path.join(tweet_dir, '{}_{}_{}.xlsx'.format(now[0], now[1], now[4]))
        wb.save(file_path)
        os.remove(os.path.join(tweet_dir, '{}_{}_{}.xlsx'.format(now[0], now[1], now[2])))
    logging.info("Merge has been completed. merge time:{}".format(datetime.datetime.now()))
    #time.sleep(update_interval)


