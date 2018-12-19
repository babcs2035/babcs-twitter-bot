# import
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import announce
import followBack

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})

# 定期ツイート（毎時 30 分）
@sched.scheduled_job('cron', minute = '30', hour = '*/1')
def scheduled_job():

    print("bot: ----- announce Start -----")
    announce.announce()
    print("bot: ----- announce End -----")
    
# フォロバ（毎時 0, 20, 40 分）
@sched.scheduled_job('cron', minute = '0, 20, 40', hour = '*/1')
def scheduled_job():

    print("bot: ----- followBack Start -----")
    followBack.followBack()
    print("bot: ----- followBack End -----")

# おまじない
sched.start()
