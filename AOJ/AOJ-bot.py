# import
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import detection

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})

# AOJ AC 検出（15 秒ごと）
@sched.scheduled_job('interval', seconds = 15)
def scheduled_job():
    
    print("AOJ-bot: ----- AOJ-detection Start -----")
    detection.detection()
    print("AOJ-bot: ----- AOJ-detection End -----")
    
# おまじない
sched.start()
