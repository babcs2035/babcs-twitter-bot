# import
import subprocess

# 各 Bot を開始
subprocess.Popen(["python", "cper_bot/cper_bot.py"])
print("main: started cper_bot")
subprocess.Popen(["python", "cpcontest_bot/cpcontest_bot.py"])
print("main: started cpcontest_bot")
