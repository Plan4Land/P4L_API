from flask import Flask, jsonify
import requests
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/holiday', methods=['GET'])
def get_holiday():
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
            response.raise_for_status()  # HTTP 에러 발생 시 예외 처리

            # 응답이 JSON이 아니거나, 예상한 형식이 아닌 경우 처리
            try:
                data = response.json()
            except ValueError:
                return jsonify({"error": "응답 데이터가 올바른 JSON 형식이 아닙니다."}), 500

            # 데이터가 비어있거나 예상한 형식이 아닌 경우 처리
            if not data.get('response', {}).get('body', {}).get('items'):
                continue  # 해당 월에 공휴일이 없다면 넘어감

            # 공휴일 데이터 추출
            items = data['response']['body']['items']['item']
            if isinstance(items, dict):  # 단일 데이터인 경우 리스트로 변환
                items = [items]

            holidays.extend([
                {
                    "dateName": item.get("dateName", ""),  # 공휴일 이름
                    "locdate": item.get("locdate", ""),  # 날짜
                    "isHoliday": item.get("isHoliday", ""),  # 공휴일 여부
                    "seq": item.get("seq", ""),  # 고유 번호
                    "year": year  # 해당 연도 추가
                }
                for item in items
            ])

        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"API 요청 실패: {e}"}), 500
        except KeyError:
            continue  # 공휴일 데이터가 없는 경우 건너뜀

    return jsonify(holidays)


if __name__ == '__main__':
    app.run(debug=True)
