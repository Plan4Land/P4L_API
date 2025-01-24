import pandas as pd
import pymysql
## pip install pymysql

data_raw = pd.read_csv("tour.csv")
# sigungu_code와 mapx가 없는 행 제거
data = data_raw.dropna(subset=['sigungu_code', 'mapx'])
# mapx 값이 0인 행 제거
data = data[data['mapx'] != 0]
# sigungu_code가 99인 행 제거
data = data[data['sigungu_code'] != 99]
# type_id 값 변경
#    - [12, 14, 25, 28, 38] → 100
#    - 32 → 200
#    - 39 → 300
data['type_id'] = data['type_id'].replace({12: 100, 14: 100, 25: 100, 28: 100, 38: 100, 32: 200, 39: 300})
# type_id가 15인 행 제거
data = data[data['type_id'] != 15]
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
delete_query = "DELETE FROM Travel_Spot"

cursor.execute(delete_query)
conn.commit()

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
