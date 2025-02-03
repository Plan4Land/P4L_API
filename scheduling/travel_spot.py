import json  # json 직렬화 / 역직렬화
import requests  # http 통신
import time
from datetime import datetime
import pandas as pd
import pymysql

def get_tour():
    today = datetime.now().strftime('%Y%m%d')
    url = "http://apis.data.go.kr/B551011/KorService1/areaBasedList1"
    MobileOs = "ETC"
    MobileApp = "Plan4Land"
    dataType = "json"
    ## serviceKey는 각자 Decode Key 사용해주세요.. 하루 요청량이 정해져있어요ㅠㅠ
    serviceKey = "IgykVu0qTZbi+3YtfC645Gag515ri7KsHHpE3r6Ef3iTiNaSDdmKZJizindrVRYzN4DEDknnAjoziHs/KDj/6g=="
    params = {
        "MobileOS": MobileOs,
        "MobileApp": MobileApp,
        "_type": dataType,
        "modifiedtime": today,
        "serviceKey": serviceKey
    }

    try:
        response = requests.get(url, params=params)
    except requests.exceptions.RequestException as e:
        print(f"tour 정보 요청 실패 : {e}")
        return json.dumps({"에러": str(e)}, ensure_ascii=False)

    data = response.json()
    total_counts = data['response']['body']['totalCount']

    items_total = []

    if total_counts != 0 :
        for page in range(1, (total_counts//200+2)):
            params = {
                "numOfRows": 200,
                "pageNo": page,
                "MobileOS": MobileOs,
                "MobileApp": MobileApp,
                "_type": dataType,
                "modifiedtime": today,
                "serviceKey": serviceKey
            }
            response = requests.get(url, params=params)
            data = response.json()
            items = data['response']['body']['items']['item']
            items_total.extend(items)
            time.sleep(2)

        filtered_data = [
            {
                'spot_id': item['contentid'],
                'title': item['title'],
                'tel': item['tel'],
                'thumbnail': item['firstimage'],
                'area_code': item['areacode'],
                'sigungu_code': item['sigungucode'],
                'addr1': item['addr1'],
                'addr2': item['addr2'],
                'cat1': item['cat1'],
                'cat2': item['cat2'],
                'cat3': item['cat3'],
                'type_id': item['contenttypeid'],
                'created_time': item['createdtime'],
                'modified_time': item['modifiedtime'],
                'mapx': item['mapx'],
                'mapy': item['mapy']
            }
            for item in items_total
        ]
        df = pd.DataFrame(filtered_data)
    else:
        df = pd.DataFrame()

    return df

data_raw = get_tour() ## API 호출 및 데이터 받기

if data_raw.shape[0] != 0 :
    print("이거 실행함")
    data = data_raw.dropna(subset=['sigungu_code', 'mapx'])  ## 시군구 코드/좌표 값 없는 데이터 삭제
    data = data[(data['sigungu_code'] != 99) & (data['mapx'] != 0)]  ## 시군구 코드/좌표 값 에러인 데이터 삭제
    data.loc[data['type_id'].isin([12, 14, 25, 28, 38]), 'type_id'] = 100  ## 관광지 = 100
    data.loc[data['type_id'] == 32, 'type_id'] = 200  ## 숙박 = 200
    data.loc[data['type_id'] == 39, 'type_id'] = 300  ## 음식점 = 300
    data = data[data['type_id'] != 15]  ## 축제공연행사 삭제
    df = data.fillna('')  ## DB 삽입 오류 방지를 위해 null값 처리

    # MySQL 연결
    conn = pymysql.connect(
        host='localhost',
        user='plan4plan',
        password='plan1234',
        database='plan_4_land_db',
        charset='utf8mb4'  # 이모지와 다양한 유니코드 문자를 지원
    )

    cursor = conn.cursor()

    # # 1. DELETE: API에서 사라진 데이터 삭제
    # existing_ids = set(df["spot_id"])
    # delete_query = f"DELETE FROM Travel_Spot WHERE spot_id NOT IN ({','.join(['%s'] * len(existing_ids))})"
    # cursor.execute(delete_query, tuple(existing_ids))

    # 2. INSERT: 새로운 데이터 삽입
    insert_query = """
    INSERT INTO Travel_Spot (spot_id, title, tel, thumbnail, area_code, sigungu_code, addr1, addr2, cat1, cat2, cat3, type_id, created_time, modified_time, mapx, mapy)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
        title = VALUES(title),
        tel = VALUES(tel),
        thumbnail = VALUES(thumbnail),
        area_code = VALUES(area_code),
        sigungu_code = VALUES(sigungu_code),
        addr1 = VALUES(addr1),
        addr2 = VALUES(addr2),
        cat1 = VALUES(cat1),
        cat2 = VALUES(cat2),
        cat3 = VALUES(cat3),
        type_id = VALUES(type_id),
        created_time = VALUES(created_time),
        modified_time = VALUES(modified_time),
        mapx = VALUES(mapx),
        mapy = VALUES(mapy)
    """
    for _, row in df.iterrows():
        cursor.execute(insert_query, tuple(row.values))

    # # 3. UPDATE: 기존 데이터 중 수정된 데이터만 갱신
    # update_query = """
    # UPDATE Travel_Spot AS t
    # JOIN (SELECT %s AS spot_id, %s AS title, %s AS tel, %s AS thumbnail,
    #              %s AS area_code, %s AS sigungu_code, %s AS addr1, %s AS addr2,
    #              %s AS cat1, %s AS cat2, %s AS cat3, %s AS type_id,
    #              %s AS created_time, %s AS modified_time, %s AS mapx, %s AS mapy) AS n
    # ON t.spot_id = n.spot_id
    # SET t.title = n.title,
    #     t.tel = n.tel,
    #     t.thumbnail = n.thumbnail,
    #     t.area_code = n.area_code,
    #     t.sigungu_code = n.sigungu_code,
    #     t.addr1 = n.addr1,
    #     t.addr2 = n.addr2,
    #     t.cat1 = n.cat1,
    #     t.cat2 = n.cat2,
    #     t.cat3 = n.cat3,
    #     t.type_id = n.type_id,
    #     t.created_time = n.created_time,
    #     t.modified_time = n.modified_time,
    #     t.mapx = n.mapx,
    #     t.mapy = n.mapy
    # WHERE t.modified_time < n.modified_time
    # """
    # for _, row in df.iterrows():
    #     cursor.execute(update_query, tuple(row))

    # 커밋하여 데이터베이스에 반영
    conn.commit()

    # 커서 및 연결 종료
    cursor.close()
    conn.close()
