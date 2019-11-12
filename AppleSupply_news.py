import sys
import start_crawling_G as G


def main():
    # python AppleSupply_news.py [start_date] [end_date]
    # python AppleSupply_news.py '2019/11/07' '2019/11/'08'
    start_date, end_date = str(sys.argv[1]), str(sys.argv[2])
    stock_list = G.est_stocks_AppleSupply()
    G.find_news_trend(stock_list, start_date, end_date)

    # trend_for1108 顯示每家公司的 新聞數量(以udn為例)
    # search_for1108 顯示每則新聞的 標題、內容、連結、新聞台、時間


if __name__ == '__main__':
    main()
