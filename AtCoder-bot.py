# import
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from AtCoder import register
from AtCoder import detection
from AtCoder import ranking
from AtCoder import contest

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})

# AtCoder ID 登録（20 秒ごと）
@sched.scheduled_job('interval', seconds = 20)
def scheduled_job():

    print("AtCoder-bot: ----- AtCoder-register Start -----")
    register.register()
    print("AtCoder-bot: ----- AtCoder-register End -----")

# AtCoder AC 検出（毎時 0, 15, 30, 45 分）
@sched.scheduled_job('cron', minute = '0, 15, 30, 45', hour = '*/1')
def scheduled_job():

    print("AtCoder-bot: ----- AtCoder-detection Start -----")
    detection.detection()
    print("AtCoder-bot: ----- AtCoder-detection End -----")
  
# AtCoder ランキング（毎日 0:00）
@sched.scheduled_job('cron', minute = '0', hour = '0')
def scheduled_job():

    print("AtCoder-bot: ----- AtCoder-raning Start -----")
    ranking.ranking()
    print("AtCoder-bot: ----- AtCoder-raning End -----")

# AtCoder コンテスト一覧（毎日 6:00, 18:00）
@sched.scheduled_job('cron', minute = '0', hour = '6, 18')
def scheduled_job():

    print("AtCoder-bot: ----- AtCoder-contest Start -----")
    contest.contest()
    print("AtCoder-bot: ----- AtCoder-contest End -----")

# おまじない
sched.start()
