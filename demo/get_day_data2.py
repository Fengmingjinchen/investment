import akshare as ak
import pandas as pd
from datetime import datetime
import numpy as np

#df = ak.stock_zh_a_hist(symbol='600519', period='daily',start_date='20050101', end_date='20230511', adjust='qfq')
#df.to_csv("/home/jidu/Documents/xitong/code/a.csv", index=False)

#etf

# get today data
data_today = datetime.today()
year = str(data_today.year)
if (data_today.month < 10) :
    month = '0'+ str(data_today.month)
else :
    month = str(data_today.month)

if (data_today.day < 10) :
    day = '0' + str(data_today.day)
else :
    day = str(data_today.day)

data = year+month+day
# dfa = ak.fund_etf_hist_em(symbol='515030',period='daily' ,start_date='20200304', end_date='data',adjust='qfq')
# dfa.to_csv("/home/jidu/Documents/xitong/code/xinnengyuan_etf_2.csv", index=False)
dfa = ak.fund_etf_fund_info_em(fund='512690', start_date='20200304', end_date='data')
dfa.to_csv("/home/jidu/Documents/xitong/code/xinnengyuan_etf_2.csv", index=False)
# dfa.columns = ['date', 'value', 'acc_value', 'up&down', 'buy', 'sale']
# del dfa['acc_value']
# del dfa['buy']
# del dfa['sale']
# #dfa.dropna(axis=0, how='any',subset=['value', 'up&down'])
# for i in range(len(dfa)):
#   if np.isnan(dfa['value'][i]) or np.isnan(dfa['up&down'][i]):
#     dfa = dfa.drop(i)
# close_value = dfa['value']
# dfa['10'] = close_value.rolling(10).mean()
# dfa['20'] = close_value.rolling(20).mean()
# dfa['30'] = close_value.rolling(30).mean()
# dfa['60'] = close_value.rolling(60).mean()
# curr_len = len(dfa)
# curr_time = dfa.iat[curr_len - 1, 2]
# mean_20 = dfa['20']
# for i in range(20):
#         if (not np.isnan(mean_20[i])):
#             print(i)
#             print(dfa['20'][20])
# dfa.tail(1).to_csv("/home/jidu/Documents/xitong/code/xinnengyuan_etf_a.csv", index=False)

# origin_data = pd.read_csv("/home/jidu/Documents/xitong/code/xinnengyuan_etf.csv")
# origin_len = len(origin_data)
# origin_time =  origin_data.iat[origin_len - 1, 2]
# if abs(curr_time - origin_time) < 0.000001 :
#     origin_data = pd.concat([origin_data, dfa.tail(1)], ignore_index=True)
#     #origin_data.loc[origin_len] = [dfa.iat[curr_len - 1, 0], dfa.iat[curr_len - 1, 1], dfa.iat[curr_len - 1, 2]]
# origin_data.to_csv("/home/jidu/Documents/xitong/code/xinnengyuan_etf.csv", index=False)



#dfa.to_csv("/home/jidu/Documents/xitong/code/xinnengyuan_etf.csv", index=False)

# df = ak.stock_a_indicator_lg(symbol='600519')
# df.to_csv("/home/jidu/Documents/xitong/code/maotai_a.csv", index=False)