# import
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import detection
import ranking

# インスタンス化
sched = BlockingScheduler(
    executors = {
        'threadpool' : ThreadPoolExecutor(max_workers = 2),
        'processpool' : ProcessPoolExecutor(max_workers = 1)
    }
)

# AOJ AC 検出（1 分ごと）
@sched.scheduled_job('interval', minutes = 1, executor = 'threadpool')
def scheduled_job():
    
    print("cper_bot-AOJ-bot: ----- AOJ-detection Start -----")
    detection.detection()
    print("cper_bot-AOJ-bot: ----- AOJ-detection End -----")

# AOJ ランキング（毎日 0:00）
@sched.scheduled_job('cron', minute = '0', hour = '0', executor = 'threadpool')
def scheduled_job():
    
    print("cper_bot-AOJ-bot: ----- AOJ-ranking Start -----")
    ranking.ranking()
    print("cper_bot-AOJ-bot: ----- AOJ-ranking End -----")
    
# おまじない
sched.start()
