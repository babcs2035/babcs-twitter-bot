# import
import subprocess
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import getLiveContestID
import FA
import updateHighestScore
import ranking

# インスタンス化
sched = BlockingScheduler(
    executors = {
        'threadpool' : ThreadPoolExecutor(max_workers = 2),
        'processpool' : ProcessPoolExecutor(max_workers = 1)
    }
)

liveContestIDs = []

# 開催中のコンテストを取得
@sched.scheduled_job('interval', seconds = 30, executor = 'threadpool')
def scheduled_job():
    
    global liveContestIDs
    if len(liveContestIDs) == 0:

        print("cpcontest_bot: ----- getLiveContestID Start -----")
        liveContestIDs = getLiveContestID.get()
        print("cpcontest_bot: ----- getLiveContestID End -----")

@sched.scheduled_job('interval', seconds = 60, executor = 'threadpool')
def scheduled_job():
    
    global liveContestIDs
    if len(liveContestIDs) > 0:
        
        # FA を見つける (旧 AtCoder 非対応)
        # print("cpcontest_bot: ----- FA Start -----")
        # FA.FA(liveContestIDs)
        # print("cpcontest_bot: ----- FA End -----")

        # 10 位以内に浮上したユーザーを検知
        print("cpcontest_bot: ----- ranking Start -----")
        ranking.ranking(liveContestIDs)
        print("cpcontest_bot: ----- ranking End -----")

        # 問題ごとの最高得点更新を検知
        print("cpcontest_bot: ----- updateHighestScore Start -----")
        updateHighestScore.updateHighestScore(liveContestIDs)
        print("cpcontest_bot: ----- updateHighestScore End -----")

        # 開催中のコンテストを更新
        print("cpcontest_bot: ----- getLiveContestID Start -----")
        liveContestIDs = getLiveContestID.get()
        print("cpcontest_bot: ----- getLiveContestID End -----")

# おまじない
sched.start()
