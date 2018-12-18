# import
import os
import tweepy
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import announce
from AtCoder import followBack
from AtCoder import register
from AtCoder import detection
from AtCoder import ranking
from AtCoder import contest
import AOJ.register
import AOJ.detection

# ログ出力
def outputLog(comment):

    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    # 出力
    print(comment + " @ " + timeStamp)

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})

# 定期ツイート（毎時 30 分）
@sched.scheduled_job('cron', minute = '30', hour = '*/1')
def scheduled_job():
    
    # 開始ログ出力
    outputLog("--- 定期ツイート 開始 ---")

    # 実行
    announce.announce()

    # 終了ログ出力
    outputLog("--- 定期ツイート 終了 ---")
    
# フォロバ & AtCoder AC 検出（毎時 0, 20, 40 分）
@sched.scheduled_job('cron', minute = '0, 20, 40', hour = '*/1')
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

# AOJ AC 検出（30 秒ごと）
@sched.scheduled_job('interval', seconds = 30)
def scheduled_job():
    
    # 開始ログ出力
    outputLog("--- AOJ AC 検出 開始 ---")

    # 実行
    AOJ.detection.detection()
    
    # 終了ログ出力
    outputLog("--- AOJ AC 検出 終了 ---")

# AtCoder & AOJ ID 登録（20 秒ごと）
@sched.scheduled_job('interval', seconds = 20)
def scheduled_job():
    
    # 開始ログ出力
    outputLog("--- AtCoder ID 登録 開始 ---")

    # 実行
    register.register()
    
    # 終了ログ出力
    outputLog("--- AtCoder ID 登録 終了 ---")

    # 開始ログ出力
    outputLog("--- AOJ ID 登録 開始 ---")

    # 実行
    AOJ.register.register()
    
    # 終了ログ出力
    outputLog("--- AOJ ID 登録 終了 ---")
    
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
