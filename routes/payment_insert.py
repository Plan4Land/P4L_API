import pymysql
from flask import request, jsonify
from datetime import datetime
import pytz

conn = pymysql.connect(
    host='localhost',
    user='plan4plan',
    password='plan1234',
    database='plan_4_land_db',
    charset='utf8mb4'  # 이모지와 다양한 유니코드 문자를 지원
)

GET_MEMBER_UID = """
SELECT member_id FROM member WHERE id=%s
"""

MEMBERSHIP_INSERT = """
INSERT INTO MEMBERSHIP (MEMBER_UID, BILLING_KEY, EXPIRY_DATE, PAYMENT_DATE, PAY_TYPE)
VALUES (%s, %s, %s, %s, %s)
"""

RECORD_INSERT = """
INSERT INTO PAY_RECORD (RECORD_ID, PAY_TIME, PAY_TYPE, MEMBER_ID, MEMBERSHIP_ID)
VALUES (%s, %s, %s, %s, %s)
"""


def convert_datetime(iso_string, to_timezone):
    utc = pytz.utc
    target_tz = pytz.timezone(to_timezone)
    dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    dt_utc = dt.astimezone(utc)
    return dt_utc.astimezone(target_tz).strftime('%Y-%m-%d %H:%M:%S')


def get_uid(user_id):
    try:
        cursor = conn.cursor()
        cursor.execute(GET_MEMBER_UID, (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
    except Exception as e:
        print(e)
        return None


def new_membership():
    print('new membership')
    data = request.json
    print(data)
    member_id = get_uid(data['userId'])
    billing_key = data['billingKey']
    expire_date = convert_datetime(data['expireDate'], 'Asia/Seoul')
    payment_date = convert_datetime(data['paymentDate'], 'Asia/Seoul')
    pay_type = data['payType']
    print(member_id)

    try:
        with conn.cursor() as cursor:
            cursor.execute(MEMBERSHIP_INSERT, (member_id, billing_key, expire_date, payment_date, pay_type))
            membership_id = cursor.lastrowid
            insert_record(cursor, data, membership_id)
            conn.commit()
            print('Membership inserted')
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        conn.rollback()
        print(e)
        print('Membership Rejected')
        return jsonify({'message': str(e)}), 500
    finally:
        conn.close()


def insert_record(cursor, json_data, membership_pk):
    #data = request.json
    data = json_data
    record_id = data['payId']
    pay_time = convert_datetime(data['payTime'], 'Asia/Seoul')
    pay_type = data['payType']
    member_id = data['userId']
    membership_id = membership_pk
    try:
        cursor.execute(RECORD_INSERT, (record_id, pay_time, pay_type, member_id, membership_id))
        print('Record inserted')
    except Exception as e:
        print(f'Record Insert Error : {e}')
        raise

