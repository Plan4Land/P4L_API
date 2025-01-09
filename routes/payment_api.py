from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

PORTONE_API_SECRET = ''
UNIQUE_PAYMENT_ID = 'your_unique_payment_id'
BILLING_KEY_HERE = ''
CUSTOMER_ID_HERE = 'your_customer_id'


@app.route('/schedule_payment', methods=['POST'])
def schedule_payment():
    url = f"https://api.portone.io/payments/{UNIQUE_PAYMENT_ID}/schedule"

    headers = {
        'Authorization': f'PortOne {PORTONE_API_SECRET}',
        'Content-Type': 'application/json'
    }

    data = {
        "payment": {
            "billingKey": BILLING_KEY_HERE,
            "orderName": "PLAN4LAND 멤버십 정기결제",
            "customer": {
                "id": CUSTOMER_ID_HERE,
                # 고객 정보가 필요한 경우 API 명세에 따라 추가해주세요.
            },
            "amount": {
                "total": 1,
            },
            "currency": "KRW",
        },
        "timeToPay": "2023-08-24T14:15:22Z"  # 결제를 시도할 시각
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code != 200:
        return jsonify({'error': response.json()}), response.status_code

    return jsonify(response.json())

if __name__ == '__main__':
    with app.app_context():
        print(schedule_payment())
    app.run(port=5000)



