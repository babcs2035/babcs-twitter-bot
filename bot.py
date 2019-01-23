# import
import subprocess
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import announce
import followBack
import newrelic.agent

@newrelic.agent.wsgi_application()
def application(environ, start_response):

    # インスタンス化
    sched = BlockingScheduler(job_defaults = {'max_instances' : 5})
    
    # 定期ツイート（毎時 30 分）
    @sched.scheduled_job('cron', minute = '30', hour = '*/1')
    def scheduled_job():
    
        print("bot: ----- announce Start -----")
        # announce.announce()
        print("bot: announce has been passed")
        print("bot: ----- announce End -----")
        
    # フォロバ（毎時 0, 20, 40 分）
    @sched.scheduled_job('cron', minute = '0, 20, 40', hour = '*/1')
    def scheduled_job():
    
        print("bot: ----- followBack Start -----")
        followBack.followBack()
        print("bot: ----- followBack End -----")
    
    # 各種 Bot を呼び出す
    subprocess.Popen(["python", "register.py"])
    subprocess.Popen(["python", "AtCoder/AtCoder-bot.py"])
    subprocess.Popen(["python", "AOJ/AOJ-bot.py"])
    subprocess.Popen(["python", "CF/CF-bot.py"])
    subprocess.Popen(["python", "YK/YK-bot.py"])
    
    # おまじない
    sched.start()

application(os.environ, True)
