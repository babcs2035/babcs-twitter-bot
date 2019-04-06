# import
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import contest
import detection
import ranking

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})

# Codeforces コンテスト一覧（毎日 0:00, 6:00, 12:00, 18:00）
@sched.scheduled_job('cron', minute = '0', hour = '0, 6, 12, 18')
def scheduled_job():

    print("CF-bot: ----- CF-contest Start -----")
    contest.contest()
    print("CF-bot: ----- CF-contest End -----")

# Codeforces AC 検出（毎時 10, 25, 40, 55 分）
@sched.scheduled_job('cron', minute = '10, 25, 40, 55', hour = '*/1')
def scheduled_job():

    print("CF-bot: ----- CF-detection Start -----")
    detection.detection()
    print("CF-bot: ----- CF-detection End -----")

# Codeforces AC 提出数ランキング（毎日 0:00）
@sched.scheduled_job('cron', minute = '0', hour = '0')
def scheduled_job():

    print("CF-bot: ----- CF-ranking Start -----")
    ranking.ranking()
    print("CF-bot: ----- CF-ranking End -----")

# おまじない
sched.start()
