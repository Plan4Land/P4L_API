import binascii
import os
import pymysql
import pymysql.cursors
from flask import request, jsonify
from datetime import datetime
import pytz
from contextlib import contextmanager

from routes.payment_api import schedule_payment


@contextmanager
def get_db_connection():
    conn = pymysql.connect(
        host='localhost',
        user='plan4plan',
        password='plan1234',
        database='plan_4_land_db',
        charset='utf8mb4'  # 이모지와 다양한 유니코드 문자를 지원
    )
    try:
        yield conn
    finally:
        conn.close()


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

PAY_LIST_QUERY = """
SELECT I.ID, MS.BILLING_KEY, MS.PAY_TYPE, MS.MEMBERSHIP_ID 
FROM MEMBERSHIP MS 
INNER JOIN (SELECT ID FROM MEMBER) I 
ON MS.MEMBER_UID=I.MEMBER_ID
WHERE DATE(PAYMENT_DATE) = %s AND ACTIVATE=1 AND CANCLE=0
"""

IS_MEMBERSHIP = """
UPDATE MEMBER SET ROLE=%s WHERE ID=%s
"""

# 날짜 형식 변경
def convert_datetime(iso_string, to_timezone):
    utc = pytz.utc
    target_tz = pytz.timezone(to_timezone)
    dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    dt_utc = dt.astimezone(utc)
    return dt_utc.astimezone(target_tz).strftime('%Y-%m-%d %H:%M:%S')

# 오늘 날짜 가져오기
def get_current_day(timezone='Asia/Seoul'):  
    now_utc = datetime.now(pytz.utc)  # 지정된 시간대로 변환
    target_timezone = pytz.timezone(timezone)
    now_target = now_utc.astimezone(target_timezone)
    return now_target.strftime('%Y-%m-%d')

# 결제 예약 시 당일 2시로 예약 설정
def get_time_to_pay():
    now = datetime.now(pytz.timezone('Asia/Seoul')).replace(hour=14, minute=0, second=0, microsecond=0)
    return now.isoformat()

# 참조로 사용할 uid 획득
def get_uid(user_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(GET_MEMBER_UID, (user_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]
    except Exception as e:
        print(e)
        return None

# 새 멤버십 등록
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
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("START TRANSACTION")
                cursor.execute(MEMBERSHIP_INSERT, (member_id, billing_key, expire_date, payment_date, pay_type))
                change_role(cursor, member_id, True)
                membership_id = cursor.lastrowid
                insert_record(cursor, data, membership_id)
                cursor.execute("COMMIT")
                print('Membership inserted')
            return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        conn.rollback()
        print(e)
        print('Membership Rejected')
        return jsonify({'message': str(e)}), 500
    finally:
        conn.close()

# 결제 시 기록 테이블에 삽입
def insert_record(cursor, json_data, membership_pk):
    # data = request.json
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

# 멤버십 결제/해지 시 유저 role 변경
def change_role(cursor, user_id, keep_going):
    try:
        if keep_going:
            cursor.execute(IS_MEMBERSHIP, ('ROLE_MEMBERSHIP', user_id,))
        else:
            cursor.execute(IS_MEMBERSHIP, ('ROLE_GENERAL', user_id,))
    except Exception as e:
        print(e)
        raise

# 정기결제 리스트 반환
def get_payment_list():
    today = get_current_day()
    try:
        with get_db_connection() as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(PAY_LIST_QUERY, (today,))
                result = cursor.fetchall()
                return result
    except Exception as e:
        print(e)
        print('Payment List Rejected')
        return ''

# 랜덤 결제건 ID
def random_id():
    return binascii.hexlify(os.urandom(8)).decode()

# 정기결제
def process_payments():
    payment_data = get_payment_list()

    for data in payment_data:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute('START TRANSACTION')
                    payment_id = random_id()
                    customer_id = data['ID']
                    billing_key = data['BILLING_KEY']
                    pay_type = data['PAY_TYPE']
                    membership_id = data['MEMBERSHIP_ID']
                    time_to_pay = get_time_to_pay()
                    pay_req_time = get_current_day()

                    response = schedule_payment(payment_id, billing_key, customer_id, time_to_pay)
                    insert_record_monthly(cursor, payment_id, pay_req_time, pay_type, customer_id, membership_id)

                    cursor.execute('COMMIT')
                    print(f"Payment scheduled successfully: {response}")
        except Exception as e:
            cursor.execute('ROLLBACK')
            print(f"Failed to schedule payment: {e}")

# 정기결제 기록
def insert_record_monthly(cursor, record_id, pay_time, pay_type, member_id, membership_id):
    try:
        cursor.execute(RECORD_INSERT, (record_id, pay_time, pay_type, member_id, membership_id))
        print('Record inserted')
    except Exception as e:
        print(f'Record Insert Error : {e}')
        raise
