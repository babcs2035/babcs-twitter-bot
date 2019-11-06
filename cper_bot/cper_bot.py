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

# おまじない
sched.start()
