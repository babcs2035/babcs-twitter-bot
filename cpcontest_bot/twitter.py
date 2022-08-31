# import
import register
from requests_oauthlib import OAuth1Session
from apscheduler.schedulers.blocking import BlockingScheduler
import dropbox
import urllib.request
import json
import datetime
import tweepy
import log
import os


# グローバル変数
lastTweetID = 0
idFixedFlag = False

# Dropbox からダウンロード


def downloadFromDropbox():

    # グローバル変数
    global lastTweetID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # lastTweetID をダウンロード
    dbx.files_download_to_file(
        "cpcontest_bot/lastTweetID.txt", "/cpcontest_bot/lastTweetID.txt")
    with open("cpcontest_bot/lastTweetID.txt", "r") as f:
        lastTweetID = f.readline()
    log.logger.info(
        "cpcontest_bot-twitter: Downloaded lastTweetID : ", str(lastTweetID))

# Dropbox にアップロード


def uploadToDropbox():

    # グローバル変数
    global lastTweetID
    global idFixedFlag

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    if idFixedFlag:

        # lastTweetID をアップロード
        with open("cpcontest_bot/lastTweetID.txt", "w") as f:
            f.write(str(lastTweetID))
        with open("cpcontest_bot/lastTweetID.txt", "rb") as f:
            dbx.files_delete("/cpcontest_bot/lastTweetID.txt")
            dbx.files_upload(f.read(), "/cpcontest_bot/lastTweetID.txt")
        log.logger.info(
            "cpcontest_bot-twitter: Uploaded lastTweetID : ", str(lastTweetID))


# インスタンス化
sched = BlockingScheduler(job_defaults={'max_instances': 5})


@sched.scheduled_job('interval', seconds=60)
def scheduled_job():

    # グローバル変数
    global lastTweetID
    global idFixedFlag

    log.logger.info("cpcontest_bot-twitter: ----- twitter Start -----")

    # 各種キー設定
    CK = os.environ["CONSUMER_KEY2"]
    CS = os.environ["CONSUMER_SECRET2"]
    AT = os.environ["ACCESS_TOKEN_KEY2"]
    AS = os.environ["ACCESS_TOKEN_SECRET2"]

    # Twitter オブジェクトの生成
    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    api = tweepy.API(auth)

    # OAuth でツイートを取得
    api_OAuth = OAuth1Session(CK, CS, AT, AS)
    timeline_json = api_OAuth.get(
        "https://api.twitter.com/1.1/statuses/mentions_timeline.json")

    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    # データをダウンロード
    downloadFromDropbox()

    # ツイートを解析
    myTwitterID = "cpcontest_bot"
    defSubID = 0
    idFixedFlag = False
    if timeline_json.status_code == 200:
        timeline = json.loads(timeline_json.text)
        for tweet in timeline:
            if int(tweet["id_str"]) <= int(lastTweetID):
                break
            idFixedFlag = True
            lastTweetID = int(timeline[0]["id_str"])
            tweetSplited = str(tweet["text"]).split()
            userData_json = api_OAuth.get(
                "https://api.twitter.com/1.1/users/show.json?user_id=" + tweet["user"]["id_str"])
            userData = json.loads(userData_json.text)

            if len(tweetSplited) >= 3:

                # register
                if tweetSplited[1] == "reg":
                    tweetText = register.register(
                        tweetSplited[2], str(userData["screen_name"]), 0)
                    api.update_status(tweetText + timeStamp,
                                      in_reply_to_status_id=tweet["id"])
                    log.logger.info(
                        "cpcontest_bot-twitter: Tweeted " + tweetText)

                # unregister
                if tweetSplited[1] == "del":
                    tweetText = register.register(
                        tweetSplited[2], str(userData["screen_name"]), 1)
                    api.update_status(tweetText + timeStamp,
                                      in_reply_to_status_id=tweet["id"])
                    log.logger.info(
                        "cpcontest_bot-twitter: Tweeted " + tweetText)

        # 変更されたデータをアップロード
        lastTweetID = int(timeline[0]["id_str"])
        uploadToDropbox()

    else:
        log.logger.info("cpcontest_bot-twitter: Twitter API Error: %d" %
                        timeline_json.status_code)

    log.logger.info("cpcontest_bot-twitter: ----- twitter End -----")


# おまじない
sched.start()
