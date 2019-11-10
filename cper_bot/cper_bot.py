# import
import subprocess
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import followBack

# インスタンス化
sched = BlockingScheduler()
    
# フォロバ（毎時 0, 20, 40 分）
@sched.scheduled_job('cron', minute = '0, 20, 40', hour = '*/1')
def scheduled_job():

    print("cper_bot: ----- followBack Start -----")
    followBack.followBack()
    print("cper_bot: ----- followBack End -----")
    
# 各 Bot を呼び出し
subprocess.Popen(["python", "cper_bot/twitter.py"])
subprocess.Popen(["python", "cper_bot/AtCoder/AtCoder-bot.py"])
subprocess.Popen(["python", "cper_bot/AOJ/AOJ-bot.py"])
subprocess.Popen(["python", "cper_bot/CF/CF-bot.py"])
subprocess.Popen(["python", "cper_bot/YK/YK-bot.py"])

# おまじない
sched.start()
