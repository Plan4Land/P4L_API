from datetime import datetime
import requests
import json
import pandas as pd
from pandas import json_normalize


def get_holiday():
    from datetime import datetime
    import requests
    import json

    year = datetime.now().strftime("%Y")
    serviceKey = "2hAlR4x+io6b+4PdHgQASiIx+PVniZdTxHNFzmtJ0bWUQaqyIWka7e/y6Ksl/HxqrzujRUGgBf8o2H+Dfn1dBg=="
    pageNo = 1
    numOfRows = 100

    url = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getHoliDeInfo"
    params = {
        'serviceKey': serviceKey,
        'pageNo': pageNo,
        'numOfRows': numOfRows,
        'solYear': year,
        '_type': 'json'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
    except requests.exceptions.RequestException as e:
        print(f"공휴일 요청 실패: {e}")
        return {"error": str(e)}

    try:
        dict_data = response.json()
        holiday_items = dict_data['response']['body']['items']['item']
        formatted_holidays = [
            {
                "dateKind": item.get("dateKind", ""),
                "dateName": item.get("dateName", ""),
                "isHoliday": item.get("isHoliday", ""),
                "locdate": item.get("locdate", ""),
                "seq": item.get("seq", "")
            }
            for item in holiday_items
        ]

        # 화면에 표시될 데이터 출력
        print(json.dumps(formatted_holidays, indent=2, ensure_ascii=False))
        return formatted_holidays
    except KeyError:
        # 공휴일 데이터가 없는 경우 처리
        print("공휴일 데이터가 없습니다.")
        return {"message": "No holiday data found."}


# 함수 호출
if __name__ == "__main__":
    holidays = get_holiday()
