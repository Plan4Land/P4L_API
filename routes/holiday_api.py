from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 공휴일 데이터를 조회하는 함수
def get_holiday():
    # Flask에서 파라미터 추출
    solYear = request.args.get('solYear')
    solMonth = request.args.get('solMonth')

    if not solYear or not solMonth:
        return jsonify({"error": "연도와 월이 필요합니다."}), 400

    serviceKey = "2hAlR4x+io6b+4PdHgQASiIx+PVniZdTxHNFzmtJ0bWUQaqyIWka7e/y6Ksl/HxqrzujRUGgBf8o2H+Dfn1dBg=="
    url = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getHoliDeInfo"
    params = {
        'serviceKey': serviceKey,
        'pageNo': 1,
        'numOfRows': 50,
        'solYear': solYear,
        'solMonth': f"{int(solMonth):02d}",  # 월이 1자리면 0을 붙임
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
            return jsonify({"message": "해당 월에 공휴일이 없습니다."}), 200

        # 공휴일 데이터 추출
        items = data['response']['body']['items']['item']
        if isinstance(items, dict):  # 단일 데이터인 경우 리스트로 변환
            items = [items]

        holidays = [
            {
                "dateName": item.get("dateName", ""),  # 공휴일 이름
                "locdate": item.get("locdate", ""),    # 날짜
                "isHoliday": item.get("isHoliday", ""), # 공휴일 여부
                "seq": item.get("seq", "")             # 고유 번호
            }
            for item in items
        ]
        return jsonify(holidays)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API 요청 실패: {e}"}), 500
    except KeyError:
        return jsonify({"error": "공휴일 데이터가 없습니다."}), 404
