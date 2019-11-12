import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import json
import time


def update_stocks_namelist():
    df_allStocks = pd.read_html(requests.get("http://isin.twse.com.tw/isin/C_public.jsp?strMode=2").text)[0]
    # strMode=2為上市公司 strMode=4為上櫃公司 # pd.read_html()直接轉成df
    df_allStocks.columns = df_allStocks.iloc[0]
    df_allStocks = df_allStocks.iloc[1:]  # 處理columns

    df_allStocks = df_allStocks.set_index('有價證券代號及名稱')  # 處理index

    df_allStocks = df_allStocks.loc[:"上市認購(售)權證"].iloc[1:-1]
    # loc[] iloc[] 皆會保留最後一項 range(1,n) 只會到n的前一項
    df_allStocks = df_allStocks.dropna(thresh=3, axis=0).dropna(thresh=3, axis=1)
    # 不同於drop()針對整排整列做刪除 dropna()專門處理Nan資料
    save_dataFrame_or_Series(df_allStocks, r'./df_stocksContent.csv')
    print("allStocks_list total:{}".format(len(df_allStocks.index)))
    list_allStocks = []
    for i in list(df_allStocks.index):
        list_allStocks.append(re.sub('\u3000', '+', i))
    save_list_or_dict(list_allStocks, r'./stocksName.json')
    return list_allStocks


def est_stocks_namelist(route=r'./stocksName.json'):  # 抓證交所的全部股票
    if os.path.exists(route):
        with open(route, 'r') as file_object:
            contents = json.load(file_object)
        return contents
    else:
        return []


def est_stocks_AppleSupply(route=r'./AppleSupply_TW.csv'):  # 只抓其中的蘋概股
    if os.path.exists(route):
        df = pd.read_csv(route)
    else:
        df = pd.DataFrame({})

    stock_list = []
    for x in range(len(df)):
        stock_list.append(str(df.loc[x]['名稱']))

    return stock_list


def save_list_or_dict(data, route=None):  # json.dump可處理dict和list 多層次也一樣可處理 但不能處理pandas的型態
    # route ex: r'./saved/data_name.json'
    route_list = route.split('/')
    for x in range(2, len(route_list)):
        if not os.path.isdir("/".join(route_list[:x])):
            os.mkdir("/".join(route_list[:x]))
    with open(route, 'w') as file_object:
        json.dump(data, file_object)


def est_list_or_dict(route):
    if os.path.exists(route):
        with open(route, 'r') as file_object:
            contents = json.load(file_object)
        return contents
    else:
        print('沒有此檔案或路徑不正確.')
        return []


def save_dataFrame_or_Series(data, route=None):
    route_list = route.split('/')
    for x in range(2, len(route_list)):
        if not os.path.isdir("/".join(route_list[:x])):
            os.mkdir("/".join(route_list[:x]))
    data.to_csv(route, encoding='utf_8_sig')


def est_dataFrame_or_Series(route):
    if os.path.exists(route):
        df_content = pd.read_csv(route)
        return df_content
    else:
        print('沒有此檔案或路徑不正確.')
        return pd.DataFrame({})


def find_news_trend(namelist, start_date='2019/09/24', end_date='2019/09/26'):  # /僅為方便字串切片
    start = start_date.split('/')  # split() 返回 segmented string list
    end = end_date.split('/')
    search_dict = {}
    search_dict_for_csv = {}
    trend_dict = {}
    for stock in namelist:
        def insert_stock(stock_inserted):

            url = 'https://www.google.com.tw/search?hl=zh-TW&' \
                  + 'tbs=cdr%3A1%2Ccd_min%3A'+start[1]+'%2F'+start[2]+'%2F'+start[0] \
                  + '%2Ccd_max%3A'+end[1]+'%2F'+end[2]+'%2F'+end[0]+'&tbm=nws&' \
                  + 'q='+stock_inserted+'+udn&oq='+stock_inserted+'+udn'

            hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/'
                                 '537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
            time.sleep(5)
            res = requests.get(url, headers=hdr)
            search_dict[stock_inserted] = []
            if res.status_code == requests.codes.ok:
                print('requests is allowed for:', stock_inserted)
                soup = BeautifulSoup(res.text, 'html.parser')  # .content返回bytes型數據 .text則返回unicode型數據
                # print(soup.prettify())  # return str形式
                items = soup.find_all('div', class_='g')  # class為python的內建變數 需用class_
                count = 0

                for item in items:
                    count += 1
                    title = item.find('h3', class_='r').find('a').text  # 多層次的標籤也可用css selector(soup.selector)
                    # class=可以有多個標籤 id=則只能有一個身份
                    text = item.find('div', class_='st').text
                    # 內部標籤會自動忽略 因為已被算入text中 ex: <em>自動忽略
                    link = re.sub('/url\?q=', '', item.find('h3', class_='r').find('a').get('href'))
                    # ?...等 皆屬特殊符號 \?取代
                    # get()用於抓取屬性 或用.find('a')['href']表示屬性
                    source = item.find('div', class_='slp').text.split('-')
                    publisher = source[0]
                    time_source = str(source[1])  # 取名time變數 會跟time module打結 產生問題

                    search_dict[stock_inserted].append({
                        "news_title": title,
                        "news_text": text,
                        "news_link": link,
                        "news_from": publisher,
                        "time_created": time_source})

                    search_dict_for_csv[stock_inserted+'-'+str(count)] = {
                        "news_title": title,
                        "news_text": text,
                        "news_link": link,
                        "news_from": publisher,
                        "time_created": time_source}

                    print('the numbers of '+stock_inserted+' news:', count)  # +號只能用str 故使用數字時應用,號
                trend_dict[stock_inserted] = count
            else:
                print('requests is not allowed and try again.')
                time.sleep(1800)
                insert_stock(stock_inserted)

        insert_stock(stock)

    trend = pd.Series(trend_dict)  # Series取代DataFrame 因為資料只有一項 用df會出錯
    save_dataFrame_or_Series(trend, r'./saved/trend_for'+end[1]+end[2]+'.csv')

    # save_list_or_dict(search_dict, r'./saved/search_'+end[1]+end[2]+'.json')
    search = pd.DataFrame(search_dict_for_csv).transpose()
    save_dataFrame_or_Series(search, r'./saved/search_for'+end[1]+end[2]+'.csv')
    return trend, search_dict
