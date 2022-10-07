# import
import pickle
import requests
from bs4 import BeautifulSoup
import urllib
import dropbox
import json
import datetime
import tweepy
import log
import os


# グローバル変数
YKIDs = set()
lastSubID = 0

# Dropbox からダウンロード


def downloadFromDropbox():

    # グローバル変数
    global YKIDs
    global lastSubID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # YKIDs をダウンロード
    dbx.files_download_to_file("YK/YKIDs.txt", "/YK/YKIDs.txt")
    with open("YK/YKIDs.txt", "rb") as f:
        YKIDs = pickle.load(f)
    log.logger.info(
        "cper_bot-YK-detection: Downloaded YKIDs (size : ", str(len(YKIDs)), ")")

    # lastSubID をダウンロード
    dbx.files_download_to_file("YK/lastSubID.txt", "/YK/lastSubID.txt")
    with open("YK/lastSubID.txt", "r") as f:
        lastSubID = f.readline()
    log.logger.info(
        "cper_bot-YK-detection: Downloaded lastSubID : ", str(lastSubID))

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
        dbx.files_upload(f.read(), "/YK/lastSubID.txt",
                         mode=dropbox.files.WriteMode.overwrite)
    log.logger.info(
        "cper_bot-YK-detection: Uploaded lastSubID : ", str(lastSubID))


def detection():

    # グローバル変数
    global YKIDs
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
        sublistURL = "https://yukicoder.me/submissions?page=" + \
            str(sublistPageNum)
        sublistHTML = requests.get(sublistURL)
        try:
            sublistHTML.raise_for_status()
            sublistData = BeautifulSoup(sublistHTML.text, "html.parser")
        except:
            log.logger.info("cper_bot-YK-detection: sublistHTML Error")
            break
        sublistRows = sublistData.find_all("tr")
        del sublistRows[0]
        if len(sublistRows) == 0:
            break

        # １行ずつ解析
        skipFlag = False
        for row in sublistRows:
            try:
                subID = int(row.contents[1].contents[0].contents[0])
                userID = str(row.contents[7].contents[1].contents[1])
                problemName = str(row.contents[9].contents[0].contents[0])
                status = str(row.contents[13].contents[1].contents[0])
                if newLastSubID == -1:
                    newLastSubID = subID
                if subID <= int(lastSubID) or int(lastSubID) == -1:
                    skipFlag = True
                    break
            except:
                print("cper_bot-YK-detection: row Error")
                continue
            
            subCount = subCount + 1

            # ユーザーの AC 提出かどうか判定
            if status == "AC":
                for (ykID, twitterID) in YKIDs:
                    if userID == ykID:
                        try:
                            api.update_status(userID + " ( @" + twitterID + " ) さんが <yukicoder> " + str(
                                problemName) + " を AC しました！\n" + "https://yukicoder.me/submissions/" + str(subID) + "\n" + timeStamp)
                            log.logger.info("cper_bot-YK-detection: " + userID + " ( @" + twitterID +
                                            " ) 's new AC submission (problem : " + str(problemName) + ")")
                        except:
                            log.logger.info(
                                "cper_bot-YK-detection: Tweet Error")
        if skipFlag:
            break
        sublistPageNum = sublistPageNum + 1

    # データをアップロード
    lastSubID = newLastSubID
    uploadToDropbox()


if __name__ == '__main__':
    log.logger.info("cper_bot-YK-detection: Running as debug...")
    detection()
    log.logger.info("cper_bot-YK-detection: Debug finished")
