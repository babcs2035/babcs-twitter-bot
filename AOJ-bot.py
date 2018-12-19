# import
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from AOJ import register
from AOJ import detection

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})

# AOJ ID 登録（20 秒ごと）
@sched.scheduled_job('interval', seconds = 20)
def scheduled_job():
    
    print("AOJ-bot: ----- AOJ-register Start -----")
    register.register()
    print("AOJ-bot: ----- AOJ-register End -----")

# AOJ AC 検出（15 秒ごと）
@sched.scheduled_job('interval', seconds = 15)
def scheduled_job():
    
    print("AOJ-bot: ----- AOJ-detection Start -----")
    detection.detection()
    print("AOJ-bot: ----- AOJ-detection End -----")
    
# おまじない
sched.start()
