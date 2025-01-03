import pandas as pd
import mysql.connector

data = pd.read_csv("D:/dev/Plan4Land/Plan4Land_API/tour.csv")

df = data.iloc[:5, :]
df = df.fillna('')

print("연결 시작")
# MySQL 연결
connection = mysql.connector.connect(
    host='127.0.0.1',
    user='plan4plan',
    password='plan1234',
    database='plan_4_land_db',
    port=3306
)

print("접속 시작")

cursor = connection.cursor()

# 데이터 삽입 쿼리
insert_query = """
INSERT INTO Travel_Spot (spot_id, title, tel, thumbnail, area_code, sigungu_code, addr1, addr2, cat1, cat2, cat3, type_id, created_time, modified_time, mapx, mapy)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

print("여기는 오니?")

# 데이터프레임의 각 행을 데이터베이스에 삽입
for index, row in df.iterrows():
    cursor.execute(insert_query, tuple(row))

# 커밋하여 데이터베이스에 반영
connection.commit()

# 커서 및 연결 종료
cursor.close()
connection.close()

print("데이터가 성공적으로 삽입되었습니다.")
