# import
import subprocess

# 各 Bot を開始
subprocess.Popen(["python", "cper_bot/cper_bot.py"])
subprocess.Popen(["python", "cper_bot/twitter.py"])
subprocess.Popen(["python", "cper_bot/AtCoder/AtCoder-bot.py"])
subprocess.Popen(["python", "cper_bot/AOJ/AOJ-bot.py"])
subprocess.Popen(["python", "cper_bot/CF/CF-bot.py"])
subprocess.Popen(["python", "cper_bot/YK/YK-bot.py"])
subprocess.Popen(["python", "cpcontest_bot/cpcontest_bot.py"])
