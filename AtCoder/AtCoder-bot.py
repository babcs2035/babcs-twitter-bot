# import
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import detection
import ranking
import contest
import vcontest

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})

# AtCoder AC 検出（毎時 0, 15, 30, 45 分）
@sched.scheduled_job('cron', minute = '0, 15, 30, 45', hour = '*/1')
def scheduled_job():

    print("AtCoder-bot: ----- AtCoder-detection Start -----")
    detection.detection()
    print("AtCoder-bot: ----- AtCoder-detection End -----")
  
# AtCoder ランキング（毎日 0:00）
@sched.scheduled_job('cron', minute = '0', hour = '0')
def scheduled_job():

    print("AtCoder-bot: ----- AtCoder-ranking Start -----")
    ranking.ranking()
    print("AtCoder-bot: ----- AtCoder-ranking End -----")

# AtCoder コンテスト一覧（毎日 6:00, 18:00）
@sched.scheduled_job('cron', minute = '0', hour = '6, 18')
def scheduled_job():

    print("AtCoder-bot: ----- AtCoder-contest Start -----")
    contest.contest()
    print("AtCoder-bot: ----- AtCoder-contest End -----")

# AtCoder V コンテスト一覧（毎日 0:00, 6:00, 12:00, 18:00）
@sched.scheduled_job('cron', minute = '0', hour = '0, 6, 12, 18')
def scheduled_job():

    print("AtCoder-bot: ----- AtCoder-vcontest Start -----")
    vcontest.vcontest()
    print("AtCoder-bot: ----- AtCoder-vcontest End -----")

# おまじない
sched.start()
