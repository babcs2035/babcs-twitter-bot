# import
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import detection
import ranking

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})

# AOJ AC 検出（15 秒ごと）
@sched.scheduled_job('interval', seconds = 15)
def scheduled_job():
    
    print("AOJ-bot: ----- AOJ-detection Start -----")
    detection.detection()
    print("AOJ-bot: ----- AOJ-detection End -----")

# AOJ ランキング（毎日 0:00）
@sched.scheduled_job('cron', minute = '0', hour = '0')
def scheduled_job():
    
    print("AOJ-bot: ----- AOJ-ranking Start -----")
    ranking.ranking()
    print("AOJ-bot: ----- AOJ-ranking End -----")
    
# おまじない
sched.start()
