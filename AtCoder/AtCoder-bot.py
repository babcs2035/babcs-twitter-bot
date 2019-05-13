# import
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import detection
import ranking
import contest
import vcontest
import result

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})

# AtCoder AC 全検出（毎時 0, 15, 30, 45 分）
@sched.scheduled_job('cron', minute = '0, 15, 30, 45', hour = '*/1')
def scheduled_job():

    print("AtCoder-bot: ----- AtCoder-detection (All) Start -----")
    detection.detection(0)
    print("AtCoder-bot: ----- AtCoder-detection (All) End -----")

# AtCoder AC 部分検出（1 分ごと）
@sched.scheduled_job('interval', minutes = 1)
def scheduled_job():

    print("AtCoder-bot: ----- AtCoder-detection (Recent) Start -----")
    # detection.detection(1)
    print("AtCoder-bot: AtCoder-detection (Recent) passed")
    print("AtCoder-bot: ----- AtCoder-detection (Recent) End -----")
  
# AtCoder Daily ランキング（毎日 0:00）
@sched.scheduled_job('cron', minute = '0', hour = '0')
def scheduled_job():

    print("AtCoder-bot: ----- AtCoder-ranking (Daily) Start -----")
    ranking.ranking(0)
    print("AtCoder-bot: ----- AtCoder-ranking (Daily) End -----")

# AtCoder Mid Daily ランキング（毎日 12:00）
@sched.scheduled_job('cron', minute = '0', hour = '12')
def scheduled_job():

    print("AtCoder-bot: ----- AtCoder-ranking (Mid Daily) Start -----")
    ranking.ranking(1)
    print("AtCoder-bot: ----- AtCoder-ranking (Mid Daily) End -----")

# AtCoder Weekly ランキング（毎週月曜 0:01）
@sched.scheduled_job('cron', minute = '1', hour = '0', day_of_week = 'mon')
def scheduled_job():

    print("AtCoder-bot: ----- AtCoder-ranking (Weekly) Start -----")
    ranking.ranking(2)
    print("AtCoder-bot: ----- AtCoder-ranking (Weekly) End -----")

# AtCoder Monthly ランキング（毎月１日 0:02）
@sched.scheduled_job('cron', minute = '2', hour = '0', day = '1')
def scheduled_job():

    print("AtCoder-bot: ----- AtCoder-ranking (Monthly) Start -----")
    ranking.ranking(3)
    print("AtCoder-bot: ----- AtCoder-ranking (Monthly) End -----")

# AtCoder コンテスト一覧（毎日 0:00, 6:00, 12:00, 18:00）
@sched.scheduled_job('cron', minute = '0', hour = '0, 6, 12, 18')
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

# AtCoder コンテスト成績（毎日 6:00）
@sched.scheduled_job('cron', minute = '0', hour = '6')
def scheduled_job():

    print("AtCoder-bot: ----- AtCoder-result Start -----")
    result.result()
    print("AtCoder-bot: ----- AtCoder-result End -----")

# おまじない
sched.start()
