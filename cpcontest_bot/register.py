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
        log.logger.info("cpcontest_bot-register: " +
                        atcoderID + " is correct AtCoder ID")
        return True
    except:
        log.logger.info("cpcontest_bot-register: " +
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
        "cpcontest_bot/AtCoderIDs.txt", "/cpcontest_bot/AtCoderIDs.txt")
    with open("cpcontest_bot/AtCoderIDs.txt", "rb") as f:
        AtCoderIDs = pickle.load(f)
    log.logger.info(
        "cpcontest_bot-register: Downloaded AtCoderIDs (size : ", str(len(AtCoderIDs)), ")")

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
        with open("cpcontest_bot/AtCoderIDs.txt", "wb") as f:
            pickle.dump(AtCoderIDs, f)
        with open("cpcontest_bot/AtCoderIDs.txt", "rb") as f:
            dbx.files_delete("/cpcontest_bot/AtCoderIDs.txt")
            dbx.files_upload(f.read(), "/cpcontest_bot/AtCoderIDs.txt")
        log.logger.info(
            "cpcontest_bot-register: Uploaded AtCoderIDs (size : ", str(len(AtCoderIDs)), ")")

# AtCoder ID 登録・解除


def register(atcoderID, twitterID, flag):

    log.logger.info("cpcontest_bot-register: ----- register Start -----")

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
                AtCoderIDs.append((atcoderID, twitterID))
                tweetText = "@" + str(twitterID) + " AtCoder ID を登録しました！\n"
                log.logger.info(
                    "cpcontest_bot-register: Registered new AtCoder ID : " + atcoderID)
                AtCoderIDsFixedFlag = True
            else:
                tweetText = "@" + str(twitterID) + \
                    " この AtCoder ID は既に登録されています！\n"
                log.logger.info(
                    "cpcontest_bot-register: Rejected to register AtCoder ID : " + atcoderID)
        else:
            tweetText = "@" + str(twitterID) + " 正しい AtCoder ID ではありません！\n"
            log.logger.info(
                "cpcontest_bot-register: Rejected to register new AtCoder ID : " + atcoderID)
    if flag == 1:
        if checkAtCoderID(atcoderID):
            if (atcoderID, twitterID) in AtCoderIDs:
                AtCoderIDs.remove((atcoderID, twitterID))
                tweetText = "@" + str(twitterID) + " AtCoder ID を登録解除しました！\n"
                log.logger.info(
                    "cpcontest_bot-register: Unregistered AtCoder ID : " + atcoderID)
                AtCoderIDsFixedFlag = True
            else:
                tweetText = "@" + str(twitterID) + \
                    " この AtCoder ID は登録されていません！\n"
                log.logger.info(
                    "cpcontest_bot-register: Rejected to unregister AtCoder ID : " + atcoderID)
        else:
            tweetText = "@" + str(twitterID) + " 正しい AtCoder ID ではありません！\n"
            log.logger.info(
                "cpcontest_bot-register: Rejected to unregister AtCoder ID : " + atcoderID)

    # 変更されたデータをアップロード
    uploadToDropbox()

    log.logger.info("cpcontest_bot-register: ----- register End -----")
    return tweetText
