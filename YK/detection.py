# import
import os
import tweepy
import datetime
import json
import dropbox
import urllib
from bs4 import BeautifulSoup
import requests
import pickle

# グローバル変数
YKID = []
TwitterID = []
lastSubID = 0

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global YKID
    global TwitterID
    global lastSubID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # YKID をダウンロード
    dbx.files_download_to_file("YK/YKID.txt", "/YK/YKID.txt")
    with open("YK/YKID.txt", "r") as f:
        YKID.clear()
        for id in f:
            YKID.append(id.rstrip("\n"))
    print("cper_bot-YK-detection: Downloaded YKID (size : ", str(len(YKID)), ")")
    
    # TwitterID をダウンロード
    dbx.files_download_to_file("YK/TwitterID.txt", "/YK/TwitterID.txt")
    with open("YK/TwitterID.txt", "r") as f:
        TwitterID.clear()
        for id in f:
            TwitterID.append(id.rstrip("\n"))
    print("cper_bot-YK-detection: Downloaded TwitterID (size : ", str(len(TwitterID)), ")")
    
    # lastSubID をダウンロード
    dbx.files_download_to_file("YK/lastSubID.txt", "/YK/lastSubID.txt")
    with open("YK/lastSubID.txt", "r") as f:
        lastSubID = f.readline()
    print("cper_bot-YK-detection: Downloaded lastSubID : ", str(lastSubID))

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global lastSubID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # lastSubID をアップロード
    with open("YK/lastSubID.txt", "w") as f:
        f.write(str(lastSubID))
    with open("YK/lastSubID.txt", "rb") as f:
        dbx.files_delete("/YK/lastSubID.txt")
        dbx.files_upload(f.read(), "/YK/lastSubID.txt")
    print("cper_bot-YK-detection: Uploaded lastSubID : ", str(lastSubID))

def detection():
    
    # グローバル変数
    global YKID
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

    # ページ送り
    sublistPageNum = 1
    subCount = 0
    newLastSubID = -1
    while True:
        sublistURL = "https://yukicoder.me/submissions?page=" + str(sublistPageNum)
        sublistHTML = requests.get(sublistURL)
        try:
            sublistHTML.raise_for_status()
            sublistData = BeautifulSoup(sublistHTML.text, "html.parser")
        except:
            print("cper_bot-YK-detection: sublistHTML Error")
            break
        sublistRows = sublistData.find_all("tr")
        del sublistRows[0]
        if len(sublistRows) == 0:
            break

        # １行ずつ解析
        skipFlag = False
        for row in sublistRows:
            subID = int(row.contents[1].contents[0].contents[0])
            userID = str(row.contents[7].contents[1].contents[1])
            problemName = str(row.contents[9].contents[0].contents[0])
            status = str(row.contents[13].contents[1].contents[0])
            if newLastSubID == -1:
                newLastSubID = subID
            if subID <= int(lastSubID) or int(lastSubID) == -1:
                skipFlag = True
                break
            subCount = subCount + 1

            # ユーザーの AC 提出かどうか判定
            if status == "AC":
                idx = 0
                for ids in YKID:
                    if userID == ids:
                        try:
                            api.update_status(userID + " ( @" + TwitterID[idx] + " ) さんが <yukicoder> " + str(problemName) + " を AC しました！\n" + "https://yukicoder.me/submissions/" + str(subID) + "\n" + timeStamp)
                            print("cper_bot-YK-detection: " + userID + " ( @" + TwitterID[idx] + " ) 's new AC submission (problem : " + str(problemName) + ")")
                        except:
                            print("cper_bot-YK-detection: Tweet Error")
                    idx = idx + 1
        if skipFlag:
            break
        sublistPageNum = sublistPageNum + 1

    # データをアップロード
    lastSubID = newLastSubID
    uploadToDropbox()

if __name__ == '__main__':
    print("CF-detection: Running as debug...")
    detection()
    print("CF-detection: Debug finished")
