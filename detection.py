# import
import os
import tweepy
import datetime
import json
import dropbox
import urllib.request

# グローバル変数
lastTweetID = 0
AtCoderID = []
TwitterID = []
lastSubID = []

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global lastTweetID
    global AtCoderID
    global TwitterID
    global lastSubID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # AtCoderID をダウンロード
    dbx.files_download_to_file("AtCoderID.txt", "/AtCoderID.txt")
    with open("AtCoderID.txt", "r") as f:
        AtCoderID.clear()
        for id in f:
            AtCoderID.append(id.rstrip("\n"))
    print("detection: Downloaded AtCoderID (size : ", str(len(AtCoderID)), ")")
    
    # TwitterID をダウンロード
    dbx.files_download_to_file("TwitterID.txt", "/TwitterID.txt")
    with open("TwitterID.txt", "r") as f:
        TwitterID.clear()
        for id in f:
            TwitterID.append(id.rstrip("\n"))
    print("detection: Downloaded TwitterID (size : ", str(len(TwitterID)), ")")

    # lastSubID をダウンロード
    dbx.files_download_to_file("lastSubID.txt", "/lastSubID.txt")
    with open("lastSubID.txt", "r") as f:
        lastSubID.clear()
        for id in f:
            lastSubID.append(id.rstrip("\n"))
    print("detection: Downloaded lastSubID (size : ", str(len(lastSubID)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global lastTweetID
    global AtCoderID
    global TwitterID
    global lastSubID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # lastSubID をアップロード
    with open("lastSubID.txt", "w") as f:
        for id in lastSubID:
            f.write(str(id) + "\n")
    with open("lastSubID.txt", "rb") as f:
        dbx.files_delete("/lastSubID.txt")
        dbx.files_upload(f.read(), "/lastSubID.txt")
    print("detection: Uploaded lastSubID (size : ", str(len(lastSubID)), ")")

def detection():
    
    # グローバル変数
    global lastTweetID
    global AtCoderID
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
    timeStamp = datetime.datetime.today() + datetime.timedelta(hours=9)
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # データをダウンロード
    downloadFromDropbox()

    # AtCoder ID ごとに提出を確認
    idx = 0
    for userID in AtCoderID:

        # JSON ファイルを取得
        jsonURL = "https://kenkoooo.com/atcoder/atcoder-api/results?user=" + userID
        jsonRes = urllib.request.urlopen(jsonURL)
        jsonData = json.loads(jsonRes.read().decode("utf-8"))
        jsonData.sort(key = lambda x: x["id"], reverse = True)

        # 提出を解析
        for sub in jsonData:
            if int(str(sub["id"])) <= int(lastSubID[idx]):
                break
            if str(sub["result"]) == "AC":
                api.update_status(userID + " ( @" + TwitterID[idx] + " ) さんが " + str(sub["contest_id"]) + " の " + str(sub["problem_id"]) + " を AC しました！\n提出コード：" + "https://beta.atcoder.jp/contests/" + str(sub["contest_id"]) + "/submissions/" + str(sub["id"]) + "\n" + timeStamp)
                print("detection: " + userID + " ( @" + TwitterID[idx] + " ) made a new AC submission (contest_id : " + str(sub["contest_id"]) + ", problem_id : " + str(sub["problem_id"]) + ")")
        
        # 後処理
        if len(jsonData) > 0:
            lastSubID[idx] = str(jsonData[0]["id"])
        else:
            lastSubID[idx] = -1
        idx = idx + 1

    # データをアップロード
    uploadToDropbox()
