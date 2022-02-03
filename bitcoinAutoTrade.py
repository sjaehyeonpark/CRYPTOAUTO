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
    df = pyupbit.get_ohlcv(ticker, interval="minute240", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute240", count=1)
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

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작

coinlist = ["KRW-BTC", "KRW-ETH", "KRW-XRP","KRW-BORA"]
balance = ["BTC", "ETH", "XRP", "BORA"]
already_buy = []

while True:
    try:
        start_time = get_start_time("KRW-BTC") # 정시
        end_time = start_time + datetime.timedelta(hours=4) # 시작시간 + 1시간
        now = datetime.datetime.now()
        k_balance = get_balance("KRW")
        for i in range(len(coinlist)):   
            data = pyupbit.get_ohlcv(ticker=coinlist[i], interval="minute5")
            now_rsi = rsi(data, 14).iloc[-1]
            already_buy.append(True)
            if start_time < now < end_time - datetime.timedelta(minutes=1): #O시 59분까지
                target_price = get_target_price(coinlist[i], 0.3)
                current_price = get_current_price(coinlist[i])
                if target_price < current_price and now_rsi <= 53 and already_buy[i] == True:
                    upbit.buy_market_order(coinlist[i], k_balance*0.1)
                    already_buy[i] = False
                    btc = get_balance(balance[i])
                    amount = get_amount(balance[i])
            else:
                if (btc*1.005) > amount and already_buy[i] == False :
                    upbit.sell_market_order(coinlist[i], btc)
                    already_buy[i] = True
            time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)