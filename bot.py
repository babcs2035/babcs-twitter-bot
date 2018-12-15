# import
import os
import tweepy
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import announce
import followBack
import register
import detection
import ranking
import contest

# ログ出力
def outputLog(comment):

    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    # 出力
    print(comment + " @ " + timeStamp)

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})

# 定期ツイート（毎時 0, 30 分）
@sched.scheduled_job('cron', minute = '0, 30', hour = '*/1')
def scheduled_job():
    
    # 開始ログ出力
    outputLog("--- 定期ツイート 開始 ---")

    # 実行
    announce.announce()

    # 終了ログ出力
    outputLog("--- 定期ツイート 終了 ---")
    
# フォロバ & AtCoder AC 検出（毎時 0, 15, 30, 45 分）
@sched.scheduled_job('cron', minute = '0, 15, 30, 45', hour = '*/1')
def scheduled_job():

    # 開始ログ出力
    outputLog("--- フォロバ 開始 ---")

    # 実行
    followBack.followBack()

    # 終了ログ出力
    outputLog("--- フォロバ 終了 ---")

    # 開始ログ出力
    outputLog("--- AtCoder AC 検出 開始 ---")

    # 実行
    detection.detection()

    # 終了ログ出力
    outputLog("--- AtCoder AC 検出 終了 ---")

# AtCoder ID 登録（15 秒ごと）
@sched.scheduled_job('interval', seconds = 15)
def scheduled_job():
    
    # 開始ログ出力
    outputLog("--- AtCoder ID 登録 開始 ---")

    # 実行
    register.register()
    
    # 終了ログ出力
    outputLog("--- AtCoder ID 登録 終了 ---")
    
# Unique AC ランキング（毎日 0:00）
@sched.scheduled_job('cron', minute = '0', hour = '0')
def scheduled_job():

    # 開始ログ出力
    outputLog("--- Unique AC ランキング 開始 ---")

    # 実行
    ranking.ranking()

    # 終了ログ出力
    outputLog("--- Unique AC ランキング 終了 ---")

# コンテスト一覧（毎日 6:00, 18:00）
@sched.scheduled_job('cron', minute = '0', hour = '6, 18')
def scheduled_job():

    # 開始ログ出力
    outputLog("--- コンテスト一覧 開始 ---")

    # 実行
    contest.contest()

    # 終了ログ出力
    outputLog("--- コンテスト一覧 終了 ---")

# おまじない
sched.start()
