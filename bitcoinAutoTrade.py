import time
import pyupbit
import datetime
import pandas

access = "2VazL4VO1lyLif4Fah60mE68vd4uHAAtk2sY38fB"
secret = "bhgEKUnwv3bEs7cVO834AMVUcHZzUowxlVBzNZaa"

def rsi(ohlc: pandas.DataFrame, period : int(14)):
    delta = ohlc["close"].diff()
    ups, downs = delta.copy(), delta.copy()    
    ups[ups < 0] = 0
    downs[downs > 0] = 0

    AU = ups.ewm(com = period-1, min_periods = period).mean()
    AD = downs.abs().ewm(com = period-1, min_periods = period).mean()
    RS = AU/AD
    
    return pandas.Series(100-(100/(1+RS))) 

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def get_amount(ticker):
    return upbit.get_amount(ticker=ticker)

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def avg_price(ticker):
    return upbit.get_avg_buy_price(ticker=ticker)

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작

target_list = ["KRW-BTC", "KRW-ETH", "KRW-BORA","KRW-SAND", "KRW-ATOM"]
balance = ["BTC", "ETH", "BORA", "SAND", "ATOM"]
already_buy = [True, True, True, True, True]

while True:
    try:
        start_time = get_start_time("KRW-BTC") # 정시
        end_time = start_time + datetime.timedelta(days=1) # 다음 날
        now = datetime.datetime.now()
        k_balance = get_balance("KRW")
        for i in range(len(target_list)):   
            data = pyupbit.get_ohlcv(ticker=target_list[i], interval="minute5")
            now_rsi = rsi(data, 14).iloc[-1]
            if start_time < now < end_time - datetime.timedelta(minutes=1) : #O시 59분까지
                target_price = get_target_price(target_list[i], 0.4) #목표가
                current_price = get_current_price(target_list[i]) # 현재가
                btc = get_balance(balance[i]) #보유 수량
                amount = get_amount(balance[i]) #매수 금액
                avg = avg_price(balance[i]) # 매수 평균가
                print(current_price)
                print(avg)
                print(btc)
                if target_price < current_price and now_rsi > 47 and now_rsi < 62 and already_buy[i] == True :
                    upbit.buy_market_order(target_list[i], k_balance*0.15)
                    already_buy[i] = False
                    if current_price > avg*1.05 :
                        upbit.sell_market_order(target_list[i], btc*0.5) #False 상태 유지
                        if current_price < target_price*1.015 :
                            already_buy[i] = True
            else:
                if current_price > avg*1.01 :
                    upbit.sell_market_order(target_list[i], btc)
                    already_buy[i] = True
                else :
                    already_buy[i] = True
            time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
