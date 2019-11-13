# import
import os
import tweepy
import datetime
import json
import dropbox
import urllib
from bs4 import BeautifulSoup
import requests

# グローバル変数
AOJID = []
TwitterID = []
lastSubID = 0
lastSubFixedFlag = True

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global AOJID
    global TwitterID
    global lastSubID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # AOJID をダウンロード
    dbx.files_download_to_file("cper_bot/AOJ/AOJID.txt", "/cper_bot/AOJ/AOJID.txt")
    with open("cper_bot/AOJ/AOJID.txt", "r") as f:
        AOJID.clear()
        for id in f:
            AOJID.append(id.rstrip("\n"))
    print("cper_bot-AOJ-detection: Downloaded AOJID (size : ", str(len(AOJID)), ")")
    
    # TwitterID をダウンロード
    dbx.files_download_to_file("cper_bot/AOJ/TwitterID.txt", "/cper_bot/AOJ/TwitterID.txt")
    with open("cper_bot/AOJ/TwitterID.txt", "r") as f:
        TwitterID.clear()
        for id in f:
            TwitterID.append(id.rstrip("\n"))
    print("cper_bot-AOJ-detection: Downloaded TwitterID (size : ", str(len(TwitterID)), ")")
    
    # lastSubID をダウンロード
    dbx.files_download_to_file("cper_bot/AOJ/lastSubID.txt", "/cper_bot/AOJ/lastSubID.txt")
    with open("cper_bot/AOJ/lastSubID.txt", "r") as f:
        lastSubID = f.readline()
    print("cper_bot-AOJ-detection: Downloaded lastSubID : ", str(lastSubID))

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global lastSubID
    global lastSubFixedFlag

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    if lastSubFixedFlag:
        # lastSubID をアップロード
        with open("cper_bot/AOJ/lastSubID.txt", "w") as f:
            f.write(str(lastSubID))
        with open("cper_bot/AOJ/lastSubID.txt", "rb") as f:
            dbx.files_delete("/cper_bot/AOJ/lastSubID.txt")
            dbx.files_upload(f.read(), "/cper_bot/AOJ/lastSubID.txt")
        print("cper_bot-AOJ-detection: Uploaded lastSubID : ", str(lastSubID))

def detection():
    
    # グローバル変数
    global AOJID
    global TwitterID
    global lastSubID
    global lastSubFixedFlag
    
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
    downloadFromDropbox()

    # 提出を解析
    subs_jsonRes = urllib.request.urlopen("https://judgeapi.u-aizu.ac.jp/submission_records/recent")
    subs_jsonData = json.loads(subs_jsonRes.read().decode("utf-8"))
    lastSubFixedFlag = False
    for sub in subs_jsonData:
        if int(sub["judgeId"]) <= int(lastSubID):
            break
        lastSubFixedFlag = True
        if sub["status"] != 4:
            continue

        # AOJ ID に当てはまるか調べる
        pos = -1
        idx = 0
        for id in AOJID:
            if id == str(sub["userId"]):
                pos = idx
                break
            idx = idx + 1
        if pos == -1:
            continue

        subURL = "https://onlinejudge.u-aizu.ac.jp/recent_judges/" + str(sub["problemId"]) + "/judge/" + str(sub["judgeId"]) + "/" + str(id) + "/" + str(sub["language"])
        problemName = str(sub["problemTitle"])
        try:
            api.update_status(str(AOJID[pos]) + " ( @" + str(TwitterID[pos]) + " ) さんが <AOJ> " + problemName + " を AC しました！\n" + subURL + "\n" + timeStamp)
            print("cper_bot-AOJ-detection: " + str(AOJID[pos]) + " ( @" + str(TwitterID[pos]) + " ) 's new AC submission (problem : " + problemName + ")")
        except:
            print("cper_bot-AOJ-detection: Tweet Error")

    # データをアップロード
    lastSubID = int(subs_jsonData[0]["judgeId"])
    uploadToDropbox()

if __name__ == '__main__':
    print("cper_bot-AOJ-detection: Running as debug...")
    detection()
    print("cper_bot-AOJ-detection: Debug finished")
