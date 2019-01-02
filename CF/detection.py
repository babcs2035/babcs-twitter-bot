# import
import os
import tweepy
import datetime
import json
import dropbox
import urllib
import requests
import pickle

# グローバル変数
CFID = []
TwitterID = []
lastSubID = {}

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global CFID
    global TwitterID
    global lastSubID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # CFID をダウンロード
    dbx.files_download_to_file("CF/CFID.txt", "/CF/CFID.txt")
    with open("CF/CFID.txt", "r") as f:
        CFID.clear()
        for id in f:
            CFID.append(id.rstrip("\n"))
    print("CF-detection: Downloaded CFID (size : ", str(len(CFID)), ")")
    
    # TwitterID をダウンロード
    dbx.files_download_to_file("CF/TwitterID.txt", "/CF/TwitterID.txt")
    with open("CF/TwitterID.txt", "r") as f:
        TwitterID.clear()
        for id in f:
            TwitterID.append(id.rstrip("\n"))
    print("CF-detection: Downloaded TwitterID (size : ", str(len(TwitterID)), ")")
    
    # lastSubID をダウンロード
    dbx.files_download_to_file("CF/lastSubID.txt", "/CF/lastSubID.txt")
    with open("CF/lastSubID.txt", "rb") as f:
        lastSubID = pickle.load(f)
    print("CF-detection: Downloaded lastSubID (size : ", str(len(lastSubID)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global lastSubID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # lastSubID をアップロード
    with open("CF/lastSubID.txt", "wb") as f:
        pickle.dump(lastSubID, f)
    with open("CF/lastSubID.txt", "rb") as f:
        dbx.files_delete("/CF/lastSubID.txt")
        dbx.files_upload(f.read(), "/CF/lastSubID.txt")
    print("CF-detection: Uploaded lastSubID (size : ", str(len(lastSubID)), ")")

def detection():
    
    # グローバル変数
    global CFID
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
    idx = 0
    for user in CFID:
        subsJsonRes = urllib.request.urlopen("https://codeforces.com/api/user.status?handle=" + str(user))
        subsJsonData = json.loads(subsJsonRes.read().decode("utf-8"))
        if user in lastSubID:
            for sub in subsJsonData["result"]:
                if int(sub["id"]) <= lastSubID[user]:
                    break
                if str(sub["verdict"]) == "OK":
                    try:
                        api.update_status(user + " ( @" + TwitterID[idx] + " ) さんが " + str(sub["problem"]["name"]) + " を AC しました！\n提出ソースコード：" + "https://codeforces.com/contest/" + str(sub["contestId"]) + "/submission/" + str(sub["id"]) + "\n" + timeStamp)
                        print("CF-detection: " + user + " ( @" + TwitterID[idx] + " ) 's new AC submission (problem : " + str(sub["problem"]["name"]) + ")")
                    except:
                        print("CF-detection: Tweet Error")
        lastSubID[user] = int(subsJsonData["result"][0]["id"])
        idx = idx + 1

    # データをアップロード
    uploadToDropbox()

if __name__ == '__main__':
    print("CF-detection: Running as debug...")
    detection()
    print("CF-detection: Debug finished")
