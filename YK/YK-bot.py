# import
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import detection
import ranking
import contest

# インスタンス化
sched = BlockingScheduler(
    executors = {
        'threadpool' : ThreadPoolExecutor(max_workers = 2),
        'processpool' : ProcessPoolExecutor(max_workers = 1)
    }
)

# yukicoder AC 検出（1 分ごと）
@sched.scheduled_job('interval', minutes = 1, executor = 'threadpool')
def scheduled_job():
    
    print("cper_bot-YK-bot: ----- YK-detection Start -----")
    detection.detection()
    print("cper_bot-YK-bot: ----- YK-detection End -----")

# yukicoder Unique AC 数ランキング（毎日 0:00）
@sched.scheduled_job('cron', minute = '0', hour = '0', executor = 'threadpool')
def scheduled_job():
    
    print("cper_bot-YK-bot: ----- YK-ranking Start -----")
    ranking.ranking()
    print("cper_bot-YK-bot: ----- YK-ranking End -----")

# yukicoder コンテスト予定（毎日 0, 6, 12, 18 時）
@sched.scheduled_job('cron', minute = '0', hour = '0, 6, 12, 18', executor = 'threadpool')
def scheduled_job():
    
    print("cper_bot-YK-bot: ----- YK-contest Start -----")
    contest.contest()
    print("cper_bot-YK-bot: ----- YK-contest End -----")

# おまじない
sched.start()
