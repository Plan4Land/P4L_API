import pandas as pd
import pymysql
## pip install pymysql

data_raw = pd.read_csv("tour.csv")
data = data_raw.dropna(subset=['sigungu_code', 'mapx'])
data = data[(data['sigungu_code'] != 99) & (data['mapx'] != 0)]
data.loc[data['type_id'].isin([12, 14, 25, 28, 38]), 'type_id'] = 100
data.loc[data['type_id'] == 32, 'type_id'] = 200
data.loc[data['type_id'] == 39, 'type_id'] = 300
data = data[data['type_id'] != 15]
data['thumbnail'] = data['thumbnail'].str.replace("http://", "https://", regex=False)
df = data.fillna('')

# MySQL 연결
conn = pymysql.connect(
    host='localhost',
    user='plan4plan',
    password='plan1234',
    database='plan_4_land_db',
    charset='utf8mb4'
)

cursor = conn.cursor()
delete_query = "DELETE FROM travel_spot"

cursor.execute(delete_query)
conn.commit()

# 데이터 삽입 쿼리
insert_query = """
INSERT INTO travel_spot (spot_id, title, tel, thumbnail, area_code, sigungu_code, addr1, addr2, cat1, cat2, cat3, type_id, created_time, modified_time, mapx, mapy)
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
