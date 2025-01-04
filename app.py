from flask import Flask
from routes.tour_api import get_tour
from routes.holiday_api import get_holiday

app = Flask(__name__)  ## __name__ : 현재 실행중인 Python 모듈의 이름

app.add_url_rule("/api/tour", "get_tour",
                 get_tour, methods=['GET'])
app.add_url_rule("/api/holiday", "get_holiday",
                 get_holiday, methods=['GET'])

if __name__ == "__main__":
    app.run()