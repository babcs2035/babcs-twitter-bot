# import
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import detection
import ranking

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})

# yukicoder AC 検出（1 分ごと）
@sched.scheduled_job('interval', minutes = 1)
def scheduled_job():
    
    print("YK-bot: ----- YK-detection Start -----")
    detection.detection()
    print("YK-bot: ----- YK-detection End -----")

# yukicoder Unique AC 数ランキング（毎日 0:00）
@sched.scheduled_job('cron', minute = '0', hour = '0')
def scheduled_job():
    
    print("YK-bot: ----- YK-ranking Start -----")
    ranking.ranking()
    print("YK-bot: ----- YK-ranking End -----")

# おまじない
sched.start()
