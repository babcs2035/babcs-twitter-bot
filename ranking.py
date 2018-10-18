# import
import os
import tweepy
import datetime
import json
import dropbox
import urllib

# グローバル変数
AtCoderID = []
TwitterID = []
acCount = []

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global AtCoderID
    global TwitterID
    global acCount

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # AtCoderID をダウンロード
    dbx.files_download_to_file("AtCoderID.txt", "/AtCoderID.txt")
    with open("AtCoderID.txt", "r") as f:
        AtCoderID.clear()
        for id in f:
            AtCoderID.append(id.rstrip("\n"))
    print("ranking: Downloaded AtCoderID (size : ", str(len(AtCoderID)), ")")
    
    # TwitterID をダウンロード
    dbx.files_download_to_file("TwitterID.txt", "/TwitterID.txt")
    with open("TwitterID.txt", "r") as f:
        TwitterID.clear()
        for id in f:
            TwitterID.append(id.rstrip("\n"))
    print("ranking: Downloaded TwitterID (size : ", str(len(TwitterID)), ")")

    # acCount をダウンロード
    dbx.files_download_to_file("acCount.txt", "/acCount.txt")
    with open("acCount.txt", "r") as f:
        acCount.clear()
        for acs in f:
            acCount.append(int(acs.rstrip("\n")))
    print("ranking: Downloaded acCount (size : ", str(len(acCount)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global acCount
    
    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # acCount をアップロード
    with open("acCount.txt", "w") as f:
        for acs in acCount:
            f.write(str(acs) + "\n")
    with open("acCount.txt", "rb") as f:
        dbx.files_delete("/acCount.txt")
        dbx.files_upload(f.read(), "/acCount.txt")
    print("ranking: Uploaded acCount (size : ", str(len(acCount)), ")")

def ranking():
    
    # グローバル変数
    global acCount

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
    timeStamp = datetime.datetime.today() + datetime.timedelta(hours=9)
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # データをダウンロード
    downloadFromDropbox()

    # AC 数を取得する
    acCountJson = urllib.request.urlopen("https://kenkoooo.com/atcoder/atcoder-api/info/ac")
    acCountData = json.loads(acCountJson.read().decode("utf-8"))
    resCount = []
    for user in acCountData:
        if user["user_id"] in AtCoderID:
            resCount.append(({"user_id" : str(user["user_id"]), "count" : int(user["problem_count"])}))
    nowACCount = []   
    for id in AtCoderID:
        for user in resCount:
            if id == user["user_id"]:
                nowACCount.append(user["count"])
                break
    newACCount = []
    for idx in range(len(AtCoderID)):
        newACCount.append(({"user_id" : AtCoderID[idx], "count" : nowACCount[idx] - acCount[idx]}))
    newACCount.sort(key = lambda x: x["count"], reverse = True)

    # データをアップロード
    acCount = nowACCount
    uploadToDropbox()
