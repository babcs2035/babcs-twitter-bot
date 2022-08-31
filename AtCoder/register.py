# import
import pickle
import dropbox
import urllib.request
import datetime
import log
import os
import sys
sys.path.append("../")

# グローバル変数
AtCoderIDsFixedFlag = False
AtCoderIDs = []


# AtCoder ID が存在するか確認
def checkAtCoderID(atcoderID):

    try:
        html = urllib.request.urlopen("https://atcoder.jp/users/" + atcoderID)
        log.logger.info("cper_bot-AtCoder-register: " +
                        atcoderID + " is correct AtCoder ID")
        return True
    except:
        log.logger.info("cper_bot-AtCoder-register: " +
                        atcoderID + " is not correct AtCoder ID")
        return False


# Dropbox からダウンロード
def downloadFromDropbox():

    # グローバル変数
    global AtCoderIDs

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # AtCoderIDs をダウンロード
    dbx.files_download_to_file(
        "AtCoder/AtCoderIDs.txt", "/AtCoder/AtCoderIDs.txt")
    with open("AtCoder/AtCoderIDs.txt", "rb") as f:
        AtCoderIDs = pickle.load(f)
    log.logger.info(
        "cper_bot-AtCoder-register: Downloaded AtCoderIDs (size : ", str(len(AtCoderIDs)), ")")


# Dropbox にアップロード
def uploadToDropbox():

    # グローバル変数
    global AtCoderIDs
    global AtCoderIDsFixedFlag

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    if AtCoderIDsFixedFlag:

        # AtCoderIDs をアップロード
        with open("AtCoder/AtCoderIDs.txt", "wb") as f:
            pickle.dump(AtCoderIDs, f)
        with open("AtCoder/AtCoderIDs.txt", "rb") as f:
            dbx.files_upload(f.read(), "/AtCoder/AtCoderIDs.txt",
                             mode=dropbox.files.WriteMode.overwrite)
        log.logger.info(
            "cper_bot-AtCoder-register: Uploaded AtCoderIDs (size : ", str(len(AtCoderIDs)), ")")


# AtCoder ID 登録・解除
def register(atcoderID, twitterID, flag):

    log.logger.info(
        "cper_bot-AtCoder-register: ----- AtCoder-register Start -----")

    # グローバル変数
    global AtCoderIDs
    global AtCoderIDsFixedFlag

    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    # データをダウンロード
    downloadFromDropbox()

    # 登録・解除処理
    AtCoderIDsFixedFlag = False
    tweetText = ""
    if flag == 0:
        if checkAtCoderID(atcoderID):
            if (atcoderID, twitterID) not in AtCoderIDs:
                AtCoderIDs.add((atcoderID, twitterID))
                tweetText = "@" + str(twitterID) + " AtCoder ID を登録しました！\n"
                log.logger.info(
                    "cper_bot-AtCoder-register: Registered new AtCoder ID : " + atcoderID)
                AtCoderIDsFixedFlag = True
            else:
                tweetText = "@" + str(twitterID) + \
                    " この AtCoder ID は既に登録されています！\n"
                log.logger.info(
                    "cper_bot-AtCoder-register: Rejected to register AtCoder ID : " + atcoderID)
        else:
            tweetText = "@" + str(twitterID) + " 正しい AtCoder ID ではありません！\n"
            log.logger.info(
                "cper_bot-AtCoder-register: Rejected to AtCoder-register new AtCoder ID : " + atcoderID)
    if flag == 1:
        if checkAtCoderID(atcoderID):
            if (atcoderID, twitterID) in AtCoderIDs:
                AtCoderIDs.remove((atcoderID, twitterID))
                tweetText = "@" + str(twitterID) + " AtCoder ID を登録解除しました！\n"
                log.logger.info(
                    "cper_bot-AtCoder-register: Unregistered AtCoder ID : " + atcoderID)
                AtCoderIDsFixedFlag = True
            else:
                tweetText = "@" + str(twitterID) + \
                    " この AtCoder ID は登録されていません！\n"
                log.logger.info(
                    "cper_bot-AtCoder-register: Rejected to unregister AtCoder ID : " + atcoderID)
        else:
            tweetText = "@" + str(twitterID) + " 正しい AtCoder ID ではありません！\n"
            log.logger.info(
                "cper_bot-AtCoder-register: Rejected to unregister AtCoder ID : " + atcoderID)

    # 変更されたデータをアップロード
    uploadToDropbox()

    log.logger.info(
        "cper_bot-AtCoder-register: ----- AtCoder-register End -----")
    return tweetText
