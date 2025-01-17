# -*- encoding: UTF-8 -*-

import akshare as ak
import logging
import talib as tl

import concurrent.futures

fullMarketValue = 30000000000
partMarketVaule = 10000000000

def fetch(code_name):
    stock = code_name[0]
    data = ak.stock_zh_a_hist(symbol=stock, period="daily", start_date="20200101", adjust="qfq")

    if data is None or data.empty:
        logging.debug("股票："+stock+" 没有数据，略过...")
        return

    data['p_change'] = tl.ROC(data['收盘'], 1)

    return data


def run(stocks):
    stocks_data = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        future_to_stock = {executor.submit(fetch, stock): stock for stock in stocks}
        for future in concurrent.futures.as_completed(future_to_stock):
            stock = future_to_stock[future]
            try:
                data = future.result()
                if (stock[2] is not None and stock[3] is not None and stock[2] == stock[2] and stock[3] == stock[3]):
                    if (data is not None and int(stock[2]) >= fullMarketValue and int(stock[3]) >= partMarketVaule):
                        data = data.astype({'成交量': 'double'})
                        stocks_data[stock] = data
            except Exception as exc:
                print('%s(%r) generated an exception: %s' % (stock[1], stock[0], exc))

    return stocks_data
