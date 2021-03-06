# import
import subprocess
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import followBack
import getLiveContestID
import cpcontest

# インスタンス化
sched = BlockingScheduler(
    executors = {
        'threadpool' : ThreadPoolExecutor(max_workers = 2),
        'processpool' : ProcessPoolExecutor(max_workers = 1)
    }
)

# フォロバ（毎時 0, 20, 40 分）
@sched.scheduled_job('cron', minute = '0, 20, 40', hour = '*/1', executor = 'threadpool')
def scheduled_job():

    print("cpcontest_bot: ----- followBack Start -----")
    followBack.followBack()
    print("cpcontest_bot: ----- followBack End -----")

liveContestIDs = []

# 開催中のコンテストを取得
@sched.scheduled_job('interval', seconds = 30, executor = 'threadpool')
def scheduled_job():
    
    global liveContestIDs

    print("cpcontest_bot: ----- getLiveContestID Start -----")
    liveContestIDs = getLiveContestID.get()
    print("cpcontest_bot: ----- getLiveContestID End -----")

@sched.scheduled_job('interval', seconds = 60, executor = 'threadpool')
def scheduled_job():
    
    global liveContestIDs
    if len(liveContestIDs) > 0:
        cpcontest.cpcontest(liveContestIDs)

# おまじない
sched.start()
