# import
import os
import tweepy
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import announce

# ログ出力
def outputLog(comment):

    # 時刻表示を作成
    timeStamp = datetime.datetime.today() + datetime.timedelta(hours=9)
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    # 出力
    print(comment + " @ " + timeStamp)

# インスタンス化
sched = BlockingScheduler()

# 定期ツイート（毎時 0, 15, 30, 45 分）
@sched.scheduled_job('cron', minute = '0, 15, 30, 45', hour = '*/1')
def scheduled_job():

    # 実行
    announce.announce()

    # ログ出力
    outputLog("定期ツイート")

# おまじない
sched.start()
