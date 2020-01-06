# import
import subprocess
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import followBack

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 10})
    
# フォロバ（毎時 0, 20, 40 分）
@sched.scheduled_job('cron', minute = '0, 20, 40', hour = '*/1')
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
