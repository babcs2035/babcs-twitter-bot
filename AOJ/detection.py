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
    dbx.files_download_to_file("AOJ/AOJID.txt", "/AOJ/AOJID.txt")
    with open("AOJ/AOJID.txt", "r") as f:
        AOJID.clear()
        for id in f:
            AOJID.append(id.rstrip("\n"))
    print("AOJ-detection: Downloaded AOJID (size : ", str(len(AOJID)), ")")
    
    # TwitterID をダウンロード
    dbx.files_download_to_file("AOJ/TwitterID.txt", "/AOJ/TwitterID.txt")
    with open("AOJ/TwitterID.txt", "r") as f:
        TwitterID.clear()
        for id in f:
            TwitterID.append(id.rstrip("\n"))
    print("AOJ-detection: Downloaded TwitterID (size : ", str(len(TwitterID)), ")")
    
    # lastSubID をダウンロード
    dbx.files_download_to_file("AOJ/lastSubID.txt", "/AOJ/lastSubID.txt")
    with open("AOJ/lastSubID.txt", "r") as f:
        lastSubID = f.readline()
    print("AOJ-detection: Downloaded lastSubID : ", str(lastSubID))

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global lastSubID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # lastSubID をアップロード
    with open("AOJ/lastSubID.txt", "w") as f:
        f.write(str(lastSubID))
    with open("AOJ/lastSubID.txt", "rb") as f:
        dbx.files_delete("/AOJ/lastSubID.txt")
        dbx.files_upload(f.read(), "/AOJ/lastSubID.txt")
    print("AOJ-detection: Uploaded lastSubID : ", str(lastSubID))

def detection():
    
    # グローバル変数
    global AOJID
    global TwitterID
    global lastSubID
    
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
    for sub in subs_jsonData:
        if int(sub["judgeId"]) <= int(lastSubID):
            lastSubID = int(subs_jsonData[0]["judgeId"])
            break
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
            api.update_status(str(AOJID[pos]) + " ( @" + str(TwitterID[pos]) + " ) さんが " + problemName + " を AC しました！\n提出ソースコード：" + subURL + "\n" + timeStamp)
            print("AOJ-detection: " + str(AOJID[pos]) + " ( @" + str(TwitterID[pos]) + " ) 's new AC submission (problem : " + problemName + ")")
        except:
            print("AOJ-detection: Tweet Error")

    # データをアップロード
    uploadToDropbox()

if __name__ == '__main__':
    print("AOJ-detection: Running as debug...")
    detection()
    print("AOJ-detection: Debug finished")
