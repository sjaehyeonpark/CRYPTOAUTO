import pyupbit

access = "2VazL4VO1lyLif4Fah60mE68vd4uHAAtk2sY38fB"          # 본인 값으로 변경
secret = "bhgEKUnwv3bEs7cVO834AMVUcHZzUowxlVBzNZaa"          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-XRP"))     # KRW-XRP 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회