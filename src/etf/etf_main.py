import akshare as ak
import pandas as pd
from datetime import datetime
from enum import Enum
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

class etf_code(Enum):
    JIU = '512690'
    XNY = '516160'
    BANDAOTI = '512480'
    HS300 = '510310'
    YILIAO = '512170'
    ZHONGYAO = '159647'
    CHUANGXINYAO = '159992'
    GUANGFU = '515790'
    JUNGONG = '512660'
    ZHONGGAIHULIANWANG = '513050'
    XITU = '516150'
    YINHANG = '512800'
    ZNJS = '516520'
    HUANGJIN = '518880'
    KECHUANG50 = '588000'
    SHANGZHENG50 = '510050'
    ZHONGZHENG500 = '510500'
    CHUANGYEBAN50 = '159949'
    NASIDAKE = '159941'
    HENGSHENG = '159920'
    BIAOPU500 = '513500'
    RENGONGZHINENG = '159819'

list_etf_code = ['512690', '516160', '512480', '510310', '512170', '159647', '159992', '515790', '512660', '513050', 
'516150', '512800', '516520', '518880', '588000', '510050', '510500', '159949', '159941', '159920', '513500', '159819']


def get_data(code, start_day, end_day, file_name):
    dfa = ak.fund_etf_fund_info_em(fund=code, start_date=start_day, end_date=end_day)
    dfa.columns = ['date', 'value', 'acc_value', 'up&down', 'buy', 'sale']
    del dfa['buy']
    del dfa['sale']
    #dfa.dropna(axis=0, how='any',subset=['value', 'up&down'])
    for i in range(len(dfa)):
        if np.isnan(dfa['value'][i]) or np.isnan(dfa['up&down'][i]):
            dfa = dfa.drop(i)
    close_value = dfa['acc_value']
    dfa['10'] = close_value.rolling(10).mean()
    dfa['20'] = close_value.rolling(20).mean()
    dfa['30'] = close_value.rolling(30).mean()
    dfa['60'] = close_value.rolling(60).mean()
    dfa = pd.concat([dfa, pd.DataFrame(columns=['operate'])], ignore_index=True)
    curr_len = len(dfa)
    if curr_len == 0:
        return False
    curr_piace = dfa.iat[curr_len - 1, 1]
    curr_up_down = dfa.iat[curr_len - 1, 2]
    ##添加数据##
    #dfa.to_csv('/home/jidu/Documents/xitong/code/etf/' + file_name + '.csv', index=False)

    ##更新数据##
    origin_data = pd.read_csv('/home/jidu/Documents/xitong/code/etf/' + file_name + '.csv')
    origin_len = len(origin_data)
    piace = origin_data.iat[origin_len - 1, 1]
    up_down =  origin_data.iat[origin_len - 1, 2]
    if abs(curr_piace - piace) > 0.0001 or abs(curr_up_down - up_down) > 0.0001:
        origin_data = pd.concat([origin_data, dfa.tail(1)], ignore_index=True)
    origin_data.to_csv('/home/jidu/Documents/xitong/code/etf/' + file_name + '.csv', index=False)
    return True

def make_decision(file_name):
    origin_data = pd.read_csv('/home/jidu/Documents/xitong/code/etf/' + file_name + '.csv')
    value = origin_data['acc_value']
    mean_20 = origin_data['20']
    mean_30 = origin_data['30']
    mean_60 = origin_data['60']
    operate = origin_data['operate']
    curr_len = len(origin_data)
    buy_point_times = 0
    last_operate = ''
    buy_i = 0
    sell_value = 0
    sell_i = 0
    for i in range(curr_len):
        origin_data.loc[i, 'operate'] = ''
        if (not np.isnan(mean_20[i])) and (not np.isnan(mean_30[i])) and (not np.isnan(mean_60[i - 1])) :
            ## check is or not buy
            k_20 = mean_20.get(i) - mean_20.get(i - 1)
            k_30 = mean_30.get(i) - mean_30.get(i - 1)
            diff_ratio_30_60 = (mean_60.get(i) - mean_30.get(i)) / value.get(i)
            is_close_60_mean = diff_ratio_30_60 > 0.0 and diff_ratio_30_60 < 0.1
            if sell_value - 0.0 < 0.001:
                down = 0.3
            else:
                down = (sell_value - value.get(i)) / sell_value
            if (k_20 >= 0.001 and k_30 >= 0.001 and i > sell_i + 10):
                if is_close_60_mean :
                    if buy_point_times > 1 and (last_operate == '' or last_operate == 'sell'):
                        origin_data.loc[i, 'operate'] = 'buy'
                        #operate.loc[i] = 'buy'
                        last_operate = 'buy'
                        buy_i = i
                        continue
                    else :
                        buy_point_times += 1
                else :
                    if last_operate == '' or last_operate == 'sell' :
                        origin_data.loc[i, 'operate'] = 'buy'
                        last_operate = 'buy'
                        buy_i = i
                        continue
        
            ## check is or not sell
            if (k_30 <= -0.001 and value.get(i) < mean_30.get(i)) :
                if (last_operate == 'buy' or last_operate == 'sell half') and i > buy_i + 5 :
                    origin_data.loc[i, 'operate'] = 'sell'
                    last_operate = 'sell'
                    sell_value = value.get(i)
                    sell_i = i
                    continue
            if (k_20 < -0.001 and value.get(i) < mean_20.get(i)) and i > buy_i + 5:
                if last_operate == 'buy' :
                    origin_data.loc[i, 'operate'] = 'sell half'
                    last_operate = 'sell half'
    origin_data.to_csv('/home/jidu/Documents/xitong/code/etf/' + file_name + '.csv', index=False)

def back_test(file_name):
    if file_name != 'jiu_etf':
        return
    init_value = 1000.0
    init_num = 0
    is_sell_half = False
    origin_data = pd.read_csv('/home/jidu/Documents/xitong/code/etf/' + file_name + '.csv')
    for i in range(len(origin_data)):
        if origin_data.loc[i, 'operate'] == 'buy':
            init_num = init_value / origin_data.loc[i, 'acc_value']
            # print('buy')
            # print(i)
            # print(init_value)
        if origin_data.loc[i, 'operate'] == 'sell half':
            is_sell_half = True
            init_value = origin_data.loc[i, 'acc_value'] * (init_num / 2)
            # print('sell half')
            # print(i)
            # print(init_value)
        if origin_data.loc[i, 'operate'] == 'sell':
            if is_sell_half :
                init_value += origin_data.loc[i, 'acc_value'] * (init_num / 2)
                # print('sell')
                # print(i)
                # print(init_value)
            else :
                init_value = origin_data.loc[i, 'acc_value'] * init_num
                # print('sell')
                # print(i)
                # print(init_value)
            is_sell_half = False
    print('last')
    print(init_value)
    up_tola = (init_value - 1000.0) / 1000.0 * 100
    year_up = up_tola / (len(origin_data) / 250)
    print(file_name)
    print('up', up_tola)
    print('year', year_up)

def plot_data(file_name):
    if file_name != 'jiu_etf':
        return
    origin_data = pd.read_csv('/home/jidu/Documents/xitong/code/etf/' + file_name + '.csv')
    x_axis = origin_data['date']
    value = origin_data['acc_value']
    mean_20 = origin_data['20']
    mean_30 = origin_data['30']
    mean_60 = origin_data['60']
    operate = origin_data['operate']
    operate_data = []
    
            #plt.text(x_axis[i], value[i], 'buy', fontdict={'size': 10, 'color': 'red'})
    plt.style.use('seaborn')
    fig, ax = plt.subplots()
    for i in range(len(operate)):
        if operate.loc[i] == 'buy':
            #ax.scatter
            ax.text(x_axis[i], value[i], 'buy', fontdict={'size': 10, 'color': 'red'})
        if operate.loc[i] == 'sell':
            ax.text(x_axis[i], value[i], 'sell2', fontdict={'size': 10, 'color': 'green'})
        if operate.loc[i] == 'sell half':
            ax.text(x_axis[i], value[i], 'sell1', fontdict={'size': 10, 'color': 'green'})
    ax.plot(x_axis, value, c='black', alpha=1.0)
    ax.plot(x_axis, mean_20, c='deeppink', alpha=0.5)
    ax.plot(x_axis, mean_30, c='green', alpha=0.5)
    ax.plot(x_axis, mean_60, c='blue', alpha=0.5)
    x_major_locator = MultipleLocator(60)
    ax.xaxis.set_major_locator(x_major_locator)
    ax.set_xlabel('', fontproperties="SimHei", fontsize=10)
    fig.autofmt_xdate()

    plt.show()

is_make_decision = False
is_back_test = False
is_plot = False

def process(code, start_day, end_day, file_name):
    #if datetime.now().hour() > 22 or datetime.now().hour() < 9 :
    is_get_data_success = get_data(code, start_day, end_day, file_name)
    if not is_get_data_success:
        get_data(code, start_day, end_day, file_name)
    if is_make_decision:
        make_decision(file_name)
    if is_back_test :
        back_test(file_name)
    if is_plot:
        plot_data(file_name)

def main():
     ###get today time###
    date_today = datetime.today()
    year = str(date_today.year)
    if (date_today.month < 10) :
        month = '0'+ str(date_today.month)
    else :
        month = str(date_today.month)

    if (date_today.day < 10) :
        day = '0' + str(date_today.day)
    else :
        day = str(date_today.day)
    date = year+month+day
    
    ###get today data###
    for i in range(len(list_etf_code)):
        #todo:add value or acc_value
        if (list_etf_code[i] == etf_code.JIU.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20190506', date, 'jiu_etf')
        if (list_etf_code[i] == etf_code.XNY.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20210204', date, 'xinnengyuan_etf')
        if (list_etf_code[i] == etf_code.BANDAOTI.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20190612', date, 'bandaoti_etf')
        if (list_etf_code[i] == etf_code.HS300.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20120528', date, 'hushen300_etf')
        if (list_etf_code[i] == etf_code.YILIAO.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20190617', date, 'yiliao_etf')
        if (list_etf_code[i] == etf_code.ZHONGYAO.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20220728', date, 'zhongyao_etf')
        if (list_etf_code[i] == etf_code.CHUANGXINYAO.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20200410', date, 'chuangxinyao_etf')
        if (list_etf_code[i] == etf_code.GUANGFU.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20201218', date, 'guangfu_etf')
        if (list_etf_code[i] == etf_code.JUNGONG.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20160808', date, 'jungong_etf')
        if (list_etf_code[i] == etf_code.ZHONGGAIHULIANWANG.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20170118', date, 'zhonggaihulianwang_etf')
        if (list_etf_code[i] == etf_code.XITU.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20210317', date, 'hxitu_etf')
        if (list_etf_code[i] == etf_code.YINHANG.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20170803', date, 'yinhang_etf')
        if (list_etf_code[i] == etf_code.ZNJS.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20210301', date, 'zhinengjiashi_etf')
        if (list_etf_code[i] == etf_code.HUANGJIN.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20130729', date, 'huangjin_etf')
        if (list_etf_code[i] == etf_code.KECHUANG50.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20201116', date, 'kechuang50_etf')
        if (list_etf_code[i] == etf_code.SHANGZHENG50.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20100105', date, 'shangzheng50_etf')
        if (list_etf_code[i] == etf_code.ZHONGZHENG500.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20130315', date, 'zhongzheng500_etf')
        if (list_etf_code[i] == etf_code.CHUANGYEBAN50.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20160722', date, 'chuangyeban50_etf')
        if (list_etf_code[i] == etf_code.NASIDAKE.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20150713', date, 'nasidake_etf')
        if (list_etf_code[i] == etf_code.HENGSHENG.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20150126', date, 'hengsheng_etf')
        if (list_etf_code[i] == etf_code.BIAOPU500.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20140115', date, 'biaopu500_etf')
        if (list_etf_code[i] == etf_code.RENGONGZHINENG.value):
            print(list_etf_code[i])
            process(list_etf_code[i], '20200923', date, 'rengongzhineng_etf')

if __name__ == '__main__':
    main()