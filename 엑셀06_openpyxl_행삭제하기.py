import requests
from openpyxl import Workbook


URL = "https://stock.naver.com/api/domestic/market/stock/default"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://stock.naver.com/market/stock/kr",
}
PAGE_SIZE = 200
TARGET_COUNT = 200

params = {
    "tradeType": "KRX",
    "marketType": "KOSPI",
    "orderType": "marketSum",
    "startIdx": 0,
    "pageSize": PAGE_SIZE,
}

stocks = []
for start_idx in range(0, TARGET_COUNT, PAGE_SIZE):
    params["startIdx"] = start_idx
    response = requests.get(URL, params=params, headers=HEADERS, timeout=30)
    response.raise_for_status()
    page = response.json()
    stocks.extend(page)
    if not page:
        break

stocks = stocks[:TARGET_COUNT]

wb = Workbook()
ws = wb.active
ws.title = "KOSPI 200"

headers = [
    "종목명", "종목코드", "현재가", "전일대비", "등락률(%)",
    "거래량", "시가", "고가", "저가", "시가총액",
]
ws.append(headers)

for stock in stocks:
    ws.append([
        stock.get("itemname"),
        stock.get("itemcode"),
        stock.get("nowPrice"),
        stock.get("prevChangePrice"),
        stock.get("prevChangeRate"),
        stock.get("tradeVolume"),
        stock.get("openPrice"),
        stock.get("highPrice"),
        stock.get("lowPrice"),
        stock.get("marketSum"),
    ])

wb.save("kospi200.xlsx")
print(f"{len(stocks)}개 종목을 kospi200.xlsx에 저장했습니다.")