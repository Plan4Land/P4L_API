import json  # json 직렬화 / 역직렬화
import requests  # http 통신
import time
import pandas as pd

def get_tour():
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
        "serviceKey": serviceKey
    }

    # response = requests.get(url, params=params)
    # soup = BeautifulSoup(response.text, "html.parser")
    try:
        response = requests.get(url, params=params)
    except requests.exceptions.RequestException as e:
        print(f"tour 정보 요청 실패 : {e}")
        return json.dumps({"에러": str(e)}, ensure_ascii=False)

    data = response.json()
    total_counts = data['response']['body']['totalCount']
    print(total_counts)

    items_total = []

    for page in range(1, (total_counts//200+2)):
        params = {
            "numOfRows": 200,
            "pageNo": page,
            "MobileOS": MobileOs,
            "MobileApp": MobileApp,
            "_type": dataType,
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
    df.to_csv("D:/dev/Plan4Land/Plan4Land_API/tour.csv", index=False)
