# import
import subprocess
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import followBack
import getLiveContestID
import FA
import updateHighestScore
import top20

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})
    
# フォロバ（毎時 0, 20, 40 分）
@sched.scheduled_job('cron', minute = '0, 20, 40', hour = '*/1')
def scheduled_job():

    print("cpcontest_bot: ----- followBack Start -----")
    followBack.followBack()
    print("cpcontest_bot: ----- followBack End -----")

liveContestIDs = []

# 開催中のコンテストを取得
@sched.scheduled_job('interval', seconds = 30)
def scheduled_job():
    
    print("cpcontest_bot: ----- getLiveContestID Start -----")

    global liveContestIDs
    liveContestIDs = getLiveContestID.get()

    print("cpcontest_bot: ----- getLiveContestID End -----")

# FA を見つける
@sched.scheduled_job('interval', seconds = 60)
def scheduled_job():
    
    print("cpcontest_bot: ----- FA Start -----")

    global liveContestIDs
    if len(liveContestIDs) > 0:
        FA.FA(liveContestIDs)

    print("cpcontest_bot: ----- FA End -----")
    
# 問題ごとの最高得点更新を検知
@sched.scheduled_job('interval', seconds = 60)
def scheduled_job():
    
    print("cpcontest_bot: ----- updateHighestScore Start -----")

    global liveContestIDs
    if len(liveContestIDs) > 0:
        updateHighestScore.updateHighestScore(liveContestIDs)

    print("cpcontest_bot: ----- updateHighestScore End -----")

# 20 位以内に浮上したユーザーを検知
@sched.scheduled_job('interval', seconds = 60)
def scheduled_job():
    
    print("cpcontest_bot: ----- top20 Start -----")

    global liveContestIDs
    if len(liveContestIDs) > 0:
        top20.top20(liveContestIDs)

    print("cpcontest_bot: ----- top20 End -----")

# おまじない
sched.start()
print("cpcontest_bot: started cpcontest_bot")
