# import
import subprocess
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import followBack

# インスタンス化
sched = BlockingScheduler(
    executors = {
        'threadpool' : ThreadPoolExecutor(max_workers = 1),
        'processpool' : ProcessPoolExecutor(max_workers = 1)
    }
)
   
# フォロバ（毎時 0, 20, 40 分）
@sched.scheduled_job('cron', minute = '0, 20, 40', hour = '*/1', executor = 'threadpool')
def scheduled_job():

    print("bot: ----- followBack Start -----")
    followBack.followBack()
    print("bot: ----- followBack End -----")
    
# 各 Bot を呼び出し
subprocess.Popen(["python", "twitter.py"])
subprocess.Popen(["python", "AtCoder/AtCoder-bot.py"])
subprocess.Popen(["python", "AOJ/AOJ-bot.py"])
subprocess.Popen(["python", "CF/CF-bot.py"])
subprocess.Popen(["python", "YK/YK-bot.py"])
subprocess.Popen(["python", "cpcontest_bot/cpcontest_bot.py"])
subprocess.Popen(["python", "cpcontest_bot/twitter.py"])

# おまじない
sched.start()
