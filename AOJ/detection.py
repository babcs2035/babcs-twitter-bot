# import
from bs4 import BeautifulSoup
import json
import pickle
import requests
import urllib
import dropbox
import datetime
import tweepy
import log
import os


# グローバル変数
AOJIDs = set()
lastSubID = 0
lastSubFixedFlag = True


# Dropbox からダウンロード
def downloadFromDropbox():

    # グローバル変数
    global AOJIDs
    global lastSubID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # AOJID をダウンロード
    dbx.files_download_to_file("AOJ/AOJIDs.txt", "/AOJ/AOJIDs.txt")
    with open("AOJ/AOJIDs.txt", "rb") as f:
        AOJIDs = pickle.load(f)
    log.logger.info(
        "cper_bot-AOJ-detection: Downloaded AOJIDs (size : ", str(len(AOJIDs)), ")")

    # lastSubID をダウンロード
    dbx.files_download_to_file("AOJ/lastSubID.txt", "/AOJ/lastSubID.txt")
    with open("AOJ/lastSubID.txt", "r") as f:
        lastSubID = f.readline()
    log.logger.info(
        "cper_bot-AOJ-detection: Downloaded lastSubID : ", str(lastSubID))


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
        with open("AOJ/lastSubID.txt", "w") as f:
            f.write(str(lastSubID))
        with open("AOJ/lastSubID.txt", "rb") as f:
            dbx.files_upload(f.read(), "/AOJ/lastSubID.txt",
                             mode=dropbox.files.WriteMode.overwrite)
        log.logger.info(
            "cper_bot-AOJ-detection: Uploaded lastSubID : ", str(lastSubID))


def detection():

    # グローバル変数
    global AOJIDs
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
    subs_jsonRes = urllib.request.urlopen(
        "https://judgeapi.u-aizu.ac.jp/submission_records/recent")
    subs_jsonData = json.loads(subs_jsonRes.read().decode("utf-8"))
    lastSubFixedFlag = False
    for sub in subs_jsonData:
        if int(sub["judgeId"]) <= int(lastSubID):
            break
        lastSubFixedFlag = True
        if sub["status"] != 4:
            continue

        # AOJ ID に当てはまるか調べる
        AOJID = "-1"
        twitterID = "-1"
        for (id1, id2) in AOJIDs:
            if id1 == str(sub["userId"]):
                AOJID = id1
                twitterID = id2
                break
        if AOJID == "-1":
            continue

        subURL = "https://onlinejudge.u-aizu.ac.jp/recent_judges/" + \
            str(sub["problemId"]) + "/judge/" + str(sub["judgeId"]) + \
            "/" + AOJID + "/" + str(sub["language"])
        problemName = str(sub["problemTitle"])
        try:
            api.update_status(AOJID + " ( @" + twitterID + " ) さんが <AOJ> " +
                              problemName + " を AC しました！\n" + subURL + "\n" + timeStamp)
            log.logger.info("cper_bot-AOJ-detection: " + AOJID + " ( @" + twitterID +
                            " ) 's new AC submission (problem : " + problemName + ")")
        except:
            log.logger.info("cper_bot-AOJ-detection: Tweet Error")

    # データをアップロード
    lastSubID = int(subs_jsonData[0]["judgeId"])
    uploadToDropbox()


if __name__ == '__main__':
    log.logger.info("cper_bot-AOJ-detection: Running as debug...")
    detection()
    log.logger.info("cper_bot-AOJ-detection: Debug finished")
