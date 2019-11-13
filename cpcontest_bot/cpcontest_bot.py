# import
import subprocess
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import getLiveContestID
import FA
import updateHighestScore
import top20

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 10})

liveContestIDs = []

# 開催中のコンテストを取得
@sched.scheduled_job('interval', seconds = 30)
def scheduled_job():
    
    print("cpcontest_bot: ----- getLiveContestID Start -----")

    global liveContestIDs
    liveContestIDs = getLiveContestID.get()

    print("cpcontest_bot: ----- getLiveContestID End -----")

@sched.scheduled_job('interval', seconds = 60)
def scheduled_job():
    
    global liveContestIDs
    if len(liveContestIDs) > 0:
        
        # FA を見つける
        print("cpcontest_bot: ----- FA Start -----")
        FA.FA(liveContestIDs)
        print("cpcontest_bot: ----- FA End -----")

        # 問題ごとの最高得点更新を検知
        print("cpcontest_bot: ----- updateHighestScore Start -----")
        updateHighestScore.updateHighestScore(liveContestIDs)
        print("cpcontest_bot: ----- updateHighestScore End -----")

        # 20 位以内に浮上したユーザーを検知
        print("cpcontest_bot: ----- top20 Start -----")
        top20.top20(liveContestIDs)
        print("cpcontest_bot: ----- top20 End -----")

# おまじない
sched.start()
