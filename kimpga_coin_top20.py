import sys

import requests
from openpyxl import Workbook

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

UPBIT_MARKETS_URL = "https://api.upbit.com/v1/market/all"
UPBIT_TICKERS_URL = "https://api.upbit.com/v1/ticker/all"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_json(url, params=None):
    response = requests.get(url, params=params, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


# 업비트 종목 정보에서 심볼별 한글 이름을 가져온다.
market_info = fetch_json(UPBIT_MARKETS_URL, {"isDetails": "false"})
krw_markets = {item["market"]: item for item in market_info if item["market"].startswith("KRW-")}

# 거래대금 기준 상위 20개 KRW 마켓 코인
all_tickers = fetch_json(UPBIT_TICKERS_URL, {"quote_currencies": "KRW"})
krw_tickers = [ticker for ticker in all_tickers if ticker["market"] in krw_markets]
top20 = sorted(krw_tickers, key=lambda item: item["acc_trade_price_24h"], reverse=True)[:20]

print(f"{'순위':<4}{'종목명':<12}{'심볼':<10}{'업비트 원화가격':>16}{'24시간 거래대금':>18}{'등락률(%)':>10}")
print("-" * 72)

wb = Workbook()
ws = wb.active
ws.title = "상위 20개 코인"
ws.append(["순위", "종목명", "심볼", "업비트 원화가격", "24시간 거래대금", "등락률(%)"])

for rank, ticker in enumerate(top20, 1):
    market = ticker["market"]
    symbol = market.replace("KRW-", "")
    market_name = krw_markets[market]["korean_name"]
    price = ticker["trade_price"]
    trade_volume = ticker["acc_trade_price_24h"]
    change_rate = ticker["signed_change_rate"] * 100

    print(f"{rank:<4}{market_name:<12}{symbol:<10}{price:>16,.0f}{trade_volume:>18,.0f}{change_rate:>10.2f}")
    ws.append([rank, market_name, symbol, price, trade_volume, change_rate])

for column, width in {"A": 8, "B": 18, "C": 12, "D": 18, "E": 22, "F": 12}.items():
    ws.column_dimensions[column].width = width

wb.save("kimpga_coin_top20.xlsx")
print("\n상위 20개 코인 정보를 kimpga_coin_top20.xlsx에 저장했습니다.")
