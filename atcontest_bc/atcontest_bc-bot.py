# import
import subprocess
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import followBack
import getLiveContestID
import FA

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})
    
# フォロバ（毎時 0, 20, 40 分）
@sched.scheduled_job('cron', minute = '0, 20, 40', hour = '*/1')
def scheduled_job():

    print("atcontest_bc-bot: ----- followBack Start -----")
    followBack.followBack()
    print("atcontest_bc-bot: ----- followBack End -----")

liveContestIDs = []

# 開催中のコンテストを取得
@sched.scheduled_job('interval', seconds = 15)
def scheduled_job():
    
    print("atcontest_bc-bot: ----- detect live contests Start -----")

    global liveContestIDs
    liveContestIDs = getLiveContestID.get()

    print("atcontest_bc-bot: ----- detect live contests End -----")

# FA を見つける
@sched.scheduled_job('interval', seconds = 30)
def scheduled_job():
    
    print("atcontest_bc-bot: ----- detect FA Start -----")

    global liveContestIDs
    FA.FA(liveContestIDs)

    print("atcontest_bc-bot: ----- detect FA End -----")

# おまじない
sched.start()
