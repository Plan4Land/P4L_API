import pandas as pd
import pymysql
## pip install pymysql

data_raw = pd.read_csv("tour.csv")
data = data_raw.dropna(subset=['sigungu_code']) ## 시군구코드 없는애들 그냥 뺐어요
df = data.fillna('')

# MySQL 연결
conn = pymysql.connect(
    host='localhost',
    user='plan4plan',
    password='plan1234',
    database='plan_4_land_db',
    charset='utf8mb4' # 이모지와 다양한 유니코드 문자를 지원
)

cursor = conn.cursor()

# 데이터 삽입 쿼리
insert_query = """
INSERT INTO Travel_Spot (spot_id, title, tel, thumbnail, area_code, sigungu_code, addr1, addr2, cat1, cat2, cat3, type_id, created_time, modified_time, mapx, mapy)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# 데이터프레임의 각 행을 데이터베이스에 삽입
for index, row in df.iterrows():
    cursor.execute(insert_query, tuple(row))

# 커밋하여 데이터베이스에 반영
conn.commit()

# 커서 및 연결 종료
cursor.close()
conn.close()
