# import
import pickle
import requests
import urllib
import dropbox
import json
import datetime
import tweepy
import log
import os
import sys
sys.path.append("../")

# グローバル変数
CFIDs = set()
lastSubID = {}

# Dropbox からダウンロード


def downloadFromDropbox():

    # グローバル変数
    global CFIDs
    global lastSubID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # CFIDs をダウンロード
    dbx.files_download_to_file("CF/CFIDs.txt", "/CF/CFIDs.txt")
    with open("CF/CFIDs.txt", "rb") as f:
        CFIDs = pickle.load(f)
    log.logger.info(
        "cper_bot-CF-detection: Downloaded CFIDs (size : ", str(len(CFIDs)), ")")

    # lastSubID をダウンロード
    dbx.files_download_to_file("CF/lastSubID.txt", "/CF/lastSubID.txt")
    with open("CF/lastSubID.txt", "rb") as f:
        lastSubID = pickle.load(f)
    log.logger.info(
        "cper_bot-CF-detection: Downloaded lastSubID (size : ", str(len(lastSubID)), ")")

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
        dbx.files_upload(f.read(), "/CF/lastSubID.txt",
                         mode=dropbox.files.WriteMode.overwrite)
    log.logger.info(
        "cper_bot-CF-detection: Uploaded lastSubID (size : ", str(len(lastSubID)), ")")


def detection():

    # グローバル変数
    global CFIDs
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
    for (cfID, twitterID) in CFIDs:
        try:
            subsJsonRes = urllib.request.urlopen(
                "https://codeforces.com/api/user.status?handle=" + str(cfID))
        except:
            log.logger.info("cper_bot-CF-deteciton: subsJsonRes Error")
            continue
        subsJsonData = json.loads(subsJsonRes.read().decode("utf-8"))
        if cfID in lastSubID:
            for sub in subsJsonData["result"]:
                if int(sub["id"]) <= lastSubID[cfID]:
                    break
                if "verdict" in sub:
                    if str(sub["verdict"]) == "OK":
                        try:
                            api.update_status(cfID + " ( @" + twitterID + " ) さんが <Codeforces> " + str(
                                sub["problem"]["name"]) + " を AC しました！\n" + "https://codeforces.com/contest/" + str(sub["contestId"]) + "/submission/" + str(sub["id"]) + "\n" + timeStamp)
                            log.logger.info("cper_bot-CF-detection: " + cfID + " ( @" + twitterID +
                                            " ) 's new AC submission (problem : " + str(sub["problem"]["name"]) + ")")
                        except:
                            log.logger.info(
                                "cper_bot-CF-detection: Tweet Error")
        if len(subsJsonData["result"]) > 0:
            lastSubID[cfID] = int(subsJsonData["result"][0]["id"])
        idx = idx + 1

    # データをアップロード
    uploadToDropbox()


if __name__ == '__main__':
    log.logger.info("cper_bot-CF-detection: Running as debug...")
    detection()
    log.logger.info("cper_bot-CF-detection: Debug finished")
