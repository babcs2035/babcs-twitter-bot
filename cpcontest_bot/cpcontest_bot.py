# import
import log
import subprocess
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import getLiveContestID
import cpcontest


# インスタンス化
sched = BlockingScheduler(
    executors={
        'threadpool': ThreadPoolExecutor(max_workers=2),
        'processpool': ProcessPoolExecutor(max_workers=1)
    }
)

liveContestIDs = []

# 開催中のコンテストを取得


@sched.scheduled_job('interval', seconds=30, executor='threadpool')
def scheduled_job():

    global liveContestIDs

    log.logger.info("cpcontest_bot: ----- getLiveContestID Start -----")
    liveContestIDs = getLiveContestID.get()
    log.logger.info("cpcontest_bot: ----- getLiveContestID End -----")


@sched.scheduled_job('interval', seconds=60, executor='threadpool')
def scheduled_job():

    global liveContestIDs
    if len(liveContestIDs) > 0:
        cpcontest.cpcontest(liveContestIDs)


# おまじない
sched.start()
