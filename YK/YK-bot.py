# import
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})
 
# おまじない
sched.start()
