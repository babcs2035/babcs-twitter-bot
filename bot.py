# import
import os
import tweepy
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import announce
import followBack
import register
import detection

# ログ出力
def outputLog(comment):

    # 時刻表示を作成
    timeStamp = datetime.datetime.today() + datetime.timedelta(hours=9)
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    # 出力
    print(comment + " @ " + timeStamp)

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})

# 定期ツイート（毎時 0, 15, 30, 45 分）
@sched.scheduled_job('cron', minute = '0, 15, 30, 45', hour = '*/1')
def scheduled_job():
    
    # 開始ログ出力
    outputLog("--- 定期ツイート 開始 ---")

    # 実行
    announce.announce()

    # 終了ログ出力
    outputLog("--- 定期ツイート 終了 ---")
    
# フォロバ（毎時 0, 30 分）
@sched.scheduled_job('cron', minute = '0, 30', hour = '*/1')
def scheduled_job():

    # 開始ログ出力
    outputLog("--- フォロバ 開始 ---")

    # 実行
    followBack.followBack()

    # 終了ログ出力
    outputLog("--- フォロバ 終了 ---")

# AtCoder ID 登録 & AC 検出（12 秒ごと）
@sched.scheduled_job('interval', seconds = 12)
def scheduled_job():

    # AtCoder ID 登録 実行
    register.register()

    # AtCoder AC 検出 実行
    detection.detection()

# おまじない
sched.start()
