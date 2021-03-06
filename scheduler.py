import wallet_info
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=10)
def timed_job():
    print("Eseguo wallet_info ", datetime.datetime.now())
    wallet_info.get_data()

sched.start()
