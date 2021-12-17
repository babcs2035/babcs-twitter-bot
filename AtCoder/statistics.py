# import
import os
import tweepy
import datetime
import dropbox
import requests
import pickle
import json
from bs4 import BeautifulSoup
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import re

# グローバル変数
subCount = []

# Dropbox からダウンロード
# type = 0 : 1 hour
# type = 1 : 1 day
def downloadFromDropbox(type):
    
    # グローバル変数
    global subCount

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    if type == 0:

        # subCount_hour をダウンロード
        dbx.files_download_to_file("AtCoder/subCount_hour.txt", "/AtCoder/subCount_hour.txt")
        with open("AtCoder/subCount_hour.txt", "rb") as f:
            subCount = pickle.load(f)
        print("cper_bot-AtCoder-statistics: Downloaded subCount_hour (size : ", str(len(subCount)), ")")

    if type == 1:

        # subCount_day をダウンロード
        dbx.files_download_to_file("AtCoder/subCount_day.txt", "/AtCoder/subCount_day.txt")
        with open("AtCoder/subCount_day.txt", "rb") as f:
            subCount = pickle.load(f)
        print("cper_bot-AtCoder-statistics: Downloaded subCount_day (size : ", str(len(subCount)), ")")
    
# Dropbox にアップロード
# type = 0 : 1 hour
# type = 1 : 1 day
def uploadToDropbox(type):
    
    # グローバル変数
    global subCount

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    if type == 0:

        # subCount_hour をアップロード
        with open("AtCoder/subCount_hour.txt", "wb") as f:
            pickle.dump(subCount, f)
        with open("AtCoder/subCount_hour.txt", "rb") as f:
            dbx.files_upload(f.read(), "/AtCoder/subCount_hour.txt", mode = dropbox.files.WriteMode.overwrite)
        print("cper_bot-AtCoder-statistics: Uploaded subCount_hour (size : ", str(len(subCount)), ")")

    if type == 1:

        # subCount_day をアップロード
        with open("AtCoder/subCount_day.txt", "wb") as f:
            pickle.dump(subCount, f)
        with open("AtCoder/subCount_day.txt", "rb") as f:
            dbx.files_upload(f.read(), "/AtCoder/subCount_day.txt", mode = dropbox.files.WriteMode.overwrite)
        print("cper_bot-AtCoder-statistics: Uploaded subCount_day (size : ", str(len(subCount)), ")")

# type = 0 : 1 hour
# type = 1 : 1 day
def statistics(type):
    
    # グローバル変数
    global subCount
    
    # 各種キー設定
    CK = os.environ["CONSUMER_KEY"]
    CS = os.environ["CONSUMER_SECRET"]
    AT = os.environ["ACCESS_TOKEN_KEY"]
    AS = os.environ["ACCESS_TOKEN_SECRET"]
    
    # Twitter オブジェクトの生成
    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    api = tweepy.API(auth)
    
    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # データをダウンロード
    downloadFromDropbox(type)

    # コンテストごとに提出を解析
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    session = requests.Session()
    request = session.get(url = "https://kenkoooo.com/atcoder/resources/contests.json", headers = headers)
    contestsJsonData = json.loads(request.text)
    print("cper_bot-AtCoder-statistics: Downloaded contestsJsonData")
    maxSubID = -1
    for contest in contestsJsonData:

        # ページ送り
        sublistURL = "https://atcoder.jp/contests/" + str(contest["id"]) + "/submissions"
        sublistHTML = requests.get(sublistURL)
        try:
            sublistHTML.raise_for_status()
            sublistData = BeautifulSoup(sublistHTML.text, "html.parser")
        except:
            print("cper_bot-AtCoder-statistics: sublistHTML Error")
            continue
        sublistTable = sublistData.find_all("table", class_ = "table table-bordered table-striped small th-center")
        if len(sublistTable) == 0:
            continue

        # １行目を解析
        sublistRows = sublistTable[0].find_all("tr")
        del sublistRows[0]
        links = sublistRows[0].find_all("a")
        subID = int(str(links[4].get("href")).split("/")[4])
        maxSubID = max(maxSubID, subID)

    # グラフを描画・ツイート
    xs = []
    ys = []
    subCount.append((timeStamp, maxSubID))
    while (type == 0 and len(subCount) > 72) or (type == 1 and len(subCount) > 90):
        del subCount[0]
    for i in range(1, len(subCount)):
        if type == 0:
            xs.append(str(subCount[i - 1][0][5:10]) + "\n" + str(subCount[i - 1][0][11:16]) + "\n~\n" + str(subCount[i][0][5:10]) + "\n" + str(subCount[i][0][11:16]))
        if type == 1:
            xs.append(str(subCount[i - 1][0][5:10]) + "\n~\n" + str(subCount[i][0][5:10]))
        ys.append(int(subCount[i][1] - subCount[i - 1][1]))
    fig, ax = plt.subplots()
    fig = plt.figure(figsize=(20.0, 8.0))
    ax = fig.add_subplot(111)
    plt.subplots_adjust(left = 0.1, right = 0.95, bottom = 0.2, top = 0.95)
    plt.bar(xs, ys)
    ticks = 6
    plt.xticks(range(0, len(xs), ticks), xs[::ticks])
    prefix = ""
    if type == 0:
        prefix = "hour"
    if type == 1:
        prefix = "day"
    plt.savefig("AtCoder/subCount_" + prefix + ".png")
    api.update_with_media(filename = "AtCoder/subCount_" + prefix + ".png", status = "AtCoder で " + str(xs[len(xs) - 1]).replace("\n", " ") + " の間に約 " + str(ys[len(ys) - 1]).replace("\n", " ") + " 回提出がありました．\n" + timeStamp)
    print("cper_bot-AtCoder-statistics: Tweeted subCount_" + prefix + ".png")

    # データをアップロード
    uploadToDropbox(type)

if __name__ == '__main__':
    print("cper_bot-AtCoder-statistics: Running as debug...")
    statistics(0)
    print("cper_bot-AtCoder-statistics: Debug finished")
