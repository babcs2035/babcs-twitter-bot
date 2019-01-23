# import
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import detection

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})

# yukicoder AC 検出（1 分ごと）
@sched.scheduled_job('interval', minutes = 1)
def scheduled_job():
    
    print("YK-bot: ----- YK-detection Start -----")
    detection.detection()
    print("YK-bot: ----- YK-detection End -----")

# おまじない
sched.start()
