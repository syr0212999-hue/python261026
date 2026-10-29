import sys
from pathlib import Path

import requests
from openpyxl import Workbook

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

UPBIT_MARKETS_URL = "https://api.upbit.com/v1/market/all"
UPBIT_TICKERS_URL = "https://api.upbit.com/v1/ticker/all"
HEADERS = {"User-Agent": "Mozilla/5.0"}
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_EXCEL_PATH = BASE_DIR / "kimpga_coin_top20.xlsx"


def fetch_json(url, params=None):
    response = requests.get(url, params=params, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_top20():
    market_info = fetch_json(UPBIT_MARKETS_URL, {"isDetails": "false"})
    krw_markets = {item["market"]: item for item in market_info if item["market"].startswith("KRW-")}

    all_tickers = fetch_json(UPBIT_TICKERS_URL, {"quote_currencies": "KRW"})
    krw_tickers = [ticker for ticker in all_tickers if ticker["market"] in krw_markets]
    top20 = sorted(krw_tickers, key=lambda item: item["acc_trade_price_24h"], reverse=True)[:20]

    rows = []
    for rank, ticker in enumerate(top20, 1):
        market = ticker["market"]
        rows.append([
            rank,
            krw_markets[market]["korean_name"],
            market.replace("KRW-", ""),
            ticker["trade_price"],
            ticker["acc_trade_price_24h"],
            ticker["signed_change_rate"] * 100,
        ])
    return rows


def save_to_excel(rows, file_path=DEFAULT_EXCEL_PATH):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "상위 20개 코인"
    sheet.append(["순위", "종목명", "심볼", "업비트 원화가격", "24시간 거래대금", "등락률(%)"])
    for row in rows:
        sheet.append(row)

    for column, width in {"A": 8, "B": 18, "C": 12, "D": 18, "E": 22, "F": 12}.items():
        sheet.column_dimensions[column].width = width

    workbook.save(file_path)
    return Path(file_path)


if __name__ == "__main__":
    top20 = fetch_top20()
    for rank, name, symbol, price, trade_volume, change_rate in top20:
        print(f"{rank:<4}{name:<12}{symbol:<10}{price:>16,.0f}{trade_volume:>18,.0f}{change_rate:>10.2f}")
    print(f"\n상위 20개 코인 정보를 {save_to_excel(top20)}에 저장했습니다.")
