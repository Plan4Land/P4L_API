
import requests
import json
import dotenv
import os



dotenv.load_dotenv()

def schedule_payment(payment_id, billing_key, customer_id, time_to_pay):
    url = f"https://api.portone.io/payments/{payment_id}/schedule"

    headers = {
        "Authorization": f"PortOne {os.getenv('PORT_ONE_SECRET')}",
        "Content-Type": "application/json",
    }

    data = {
        "payment": {
            "billingKey": billing_key,
            "orderName": "PLAN4LAND 정기결제",
            "customer": {
                "id": customer_id,
            },
            "amount": {
                "total": 8900,
            },
            "currency": "KRW",
        },
        "timeToPay": time_to_pay
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code != 200:
        raise Exception(f"scheduleResponse: {response.json()}")

    return response.json()



