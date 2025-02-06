import pandas as pd
import pymysql
import requests
from datetime import datetime

def fetch_holidays():
    today = datetime.today()
    solYear = today.year
    years = [solYear - 2, solYear - 1, solYear, solYear + 1, solYear + 2]

    holidays = []
    serviceKey = "2hAlR4x+io6b+4PdHgQASiIx+PVniZdTxHNFzmtJ0bWUQaqyIWka7e/y6Ksl/HxqrzujRUGgBf8o2H+Dfn1dBg=="
    url = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getHoliDeInfo"

    for year in years:
        params = {
            'serviceKey': serviceKey,
            'pageNo': 1,
            'numOfRows': 50,
            'solYear': year,
            '_type': 'json'
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if not data.get('response', {}).get('body', {}).get('items'):
                continue

            items = data['response']['body']['items']['item']
            if isinstance(items, dict):
                items = [items]

            holidays.extend([
                {
                    "holiday_name": item.get("dateName", ""),
                    "is_holiday": item.get("isHoliday", ""),
                    "holiday_date": item.get("locdate", ""),
                    "sequence": item.get("seq", ""),
                    "year": year
                }
                for item in items
            ])

        except requests.exceptions.RequestException as e:
            print(f"API 요청 실패: {e}")
            continue

    return holidays

def save_holidays_to_db(holidays):
    # 데이터프레임 생성
    df = pd.DataFrame(holidays)
    df['holiday_date'] = pd.to_datetime(df['holiday_date'], format='%Y%m%d')  # 날짜 형식 변환

    # ID 자동 생성
    df['holiday_id'] = df.index + 1

    # 컬럼 재정렬
    df = df[['holiday_id', 'holiday_name', 'is_holiday', 'holiday_date', 'sequence', 'year']]

    # MySQL 연결
    conn = pymysql.connect(
        host='localhost',
        user='plan4plan',
        password='plan1234',
        database='plan_4_land_db',
        charset='utf8mb4'
    )

    cursor = conn.cursor()

    # 기존 데이터 삭제
    delete_query = "DELETE FROM Holiday"
    cursor.execute(delete_query)
    conn.commit()

    # 데이터 삽입 쿼리
    insert_query = """
    INSERT INTO Holiday (holiday_id, holiday_name, is_holiday, holiday_date, seq, year)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    # 데이터 삽입
    for _, row in df.iterrows():
        cursor.execute(insert_query, tuple(row))

    # 커밋 및 종료
    conn.commit()
    cursor.close()
    conn.close()

    print("공휴일 데이터가 데이터베이스에 저장되었습니다.")

holidays = fetch_holidays()
if holidays:
    save_holidays_to_db(holidays)
else:
    print("저장할 공휴일 데이터가 없습니다.")
