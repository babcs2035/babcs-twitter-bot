# import
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import detection
import ranking
import contest
import vcontest
import result
import statistics

# インスタンス化
sched = BlockingScheduler(
    executors = {
        'threadpool' : ThreadPoolExecutor(max_workers = 5),
        'processpool' : ProcessPoolExecutor(max_workers = 1)
    }
)

# AtCoder AC 全検出（毎時 0, 15, 30, 45 分）
@sched.scheduled_job('cron', minute = '0, 15, 30, 45', hour = '*/1', executor = 'threadpool')
def scheduled_job():

    print("cper_bot-AtCoder-bot: ----- AtCoder-detection (All) Start -----")
    detection.detection(0)
    print("cper_bot-AtCoder-bot: ----- AtCoder-detection (All) End -----")

# AtCoder AC 部分検出（1 分ごと）
@sched.scheduled_job('interval', minutes = 1, executor = 'threadpool')
def scheduled_job():

    print("cper_bot-AtCoder-bot: ----- AtCoder-detection (Recent) Start -----")
    detection.detection(1)
    print("cper_bot-AtCoder-bot: ----- AtCoder-detection (Recent) End -----")
  
# AtCoder Daily ランキング（毎日 0:00）
@sched.scheduled_job('cron', minute = '0', hour = '0', executor = 'threadpool')
def scheduled_job():

    print("cper_bot-AtCoder-bot: ----- AtCoder-ranking (Daily) Start -----")
    ranking.ranking(0)
    print("cper_bot-AtCoder-bot: ----- AtCoder-ranking (Daily) End -----")

# AtCoder Mid Daily ランキング（毎日 12:00）
@sched.scheduled_job('cron', minute = '0', hour = '12', executor = 'threadpool')
def scheduled_job():

    print("cper_bot-AtCoder-bot: ----- AtCoder-ranking (Mid Daily) Start -----")
    ranking.ranking(1)
    print("cper_bot-AtCoder-bot: ----- AtCoder-ranking (Mid Daily) End -----")

# AtCoder Weekly ランキング（毎週月曜 0:05）
@sched.scheduled_job('cron', minute = '5', hour = '0', day_of_week = 'mon', executor = 'threadpool')
def scheduled_job():

    print("cper_bot-AtCoder-bot: ----- AtCoder-ranking (Weekly) Start -----")
    ranking.ranking(2)
    print("cper_bot-AtCoder-bot: ----- AtCoder-ranking (Weekly) End -----")

# AtCoder Monthly ランキング（毎月１日 0:15）
@sched.scheduled_job('cron', minute = '15', hour = '0', day = '1', executor = 'threadpool')
def scheduled_job():

    print("cper_bot-AtCoder-bot: ----- AtCoder-ranking (Monthly) Start -----")
    ranking.ranking(3)
    print("cper_bot-AtCoder-bot: ----- AtCoder-ranking (Monthly) End -----")

# AtCoder コンテスト一覧（毎日 0:00, 6:00, 12:00, 18:00）
@sched.scheduled_job('cron', minute = '0', hour = '0, 6, 12, 18', executor = 'threadpool')
def scheduled_job():

    print("cper_bot-AtCoder-bot: ----- AtCoder-contest Start -----")
    contest.contest()
    print("cper_bot-AtCoder-bot: ----- AtCoder-contest End -----")

# AtCoder V コンテスト一覧（毎日 0:00, 6:00, 12:00, 18:00）
@sched.scheduled_job('cron', minute = '0', hour = '0, 6, 12, 18', executor = 'threadpool')
def scheduled_job():

    print("cper_bot-AtCoder-bot: ----- AtCoder-vcontest Start -----")
    vcontest.vcontest()
    print("cper_bot-AtCoder-bot: ----- AtCoder-vcontest End -----")

# AtCoder コンテスト成績（毎日 6:00）
@sched.scheduled_job('cron', minute = '0', hour = '6', executor = 'threadpool')
def scheduled_job():

    print("cper_bot-AtCoder-bot: ----- AtCoder-result Start -----")
    result.result()
    print("cper_bot-AtCoder-bot: ----- AtCoder-result End -----")

# AtCoder 1 時間ごとの統計情報（毎時 0 分）
@sched.scheduled_job('cron', minute = '0', hour = '*/1', executor = 'threadpool')
def scheduled_job():

    print("cper_bot-AtCoder-bot: ----- AtCoder-statistics (hour) Start -----")
    statistics.statistics(0)
    print("cper_bot-AtCoder-bot: ----- AtCoder-detection (hour) End -----")

# AtCoder 1 日ごとの統計情報（毎日 0:20）
@sched.scheduled_job('cron', minute = '20', hour = '0', executor = 'threadpool')
def scheduled_job():

    print("cper_bot-AtCoder-bot: ----- AtCoder-statistics (day) Start -----")
    statistics.statistics(1)
    print("cper_bot-AtCoder-bot: ----- AtCoder-detection (day) End -----")

# おまじない
sched.start()
