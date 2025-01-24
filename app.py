from flask import Flask
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
#  pip install apscheduler
import atexit

from routes.payment import new_membership, process_payments
from routes.tour_api import get_tour
from routes.holiday_api import get_holiday

app = Flask(__name__)  ## __name__ : 현재 실행중인 Python 모듈의 이름
CORS(app, resources={r"/*": {"origins": "*"}})

app.add_url_rule("/api/tour", "get_tour",
                 get_tour, methods=['GET'])
app.add_url_rule("/api/holiday", "get_holiday",
                 get_holiday, methods=['GET'])

app.add_url_rule("/pay/new-membership", "insert-membership",
                 new_membership, methods=['POST'])

scheduler = BackgroundScheduler()
scheduler.add_job(process_payments, 'cron', hour=9, minute=30)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run()