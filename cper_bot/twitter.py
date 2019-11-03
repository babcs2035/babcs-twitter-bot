# import
import os
import tweepy
import datetime
import json
import urllib.request
import dropbox
from apscheduler.schedulers.blocking import BlockingScheduler
from requests_oauthlib import OAuth1Session
import AtCoder.status
import AtCoder.register
import AtCoder.detection
import AOJ.register
import CF.register
import YK.register
import info

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
    dbx.files_download_to_file("lastTweetID.txt", "/lastTweetID.txt")
    with open("lastTweetID.txt", "r") as f:
        lastTweetID = f.readline()
    print("twitter: Downloaded lastTweetID : ", str(lastTweetID))

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
        with open("lastTweetID.txt", "w") as f:
            f.write(str(lastTweetID))
        with open("lastTweetID.txt", "rb") as f:
            dbx.files_delete("/lastTweetID.txt")
            dbx.files_upload(f.read(), "/lastTweetID.txt")
        print("twitter: Uploaded lastTweetID : ", str(lastTweetID))

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})

@sched.scheduled_job('interval', seconds = 20)
def scheduled_job():

    # グローバル変数
    global lastTweetID
    global idFixedFlag

    print("cper_bot-twitter: ----- twitter Start -----")

    # 各種キー設定
    CK = os.environ["CONSUMER_KEY"]
    CS = os.environ["CONSUMER_SECRET"]
    AT = os.environ["ACCESS_TOKEN_KEY"]
    AS = os.environ["ACCESS_TOKEN_SECRET"]
    
    # Twitter オブジェクトの生成
    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    api = tweepy.API(auth)
    
    # OAuth でツイートを取得
    api_OAuth = OAuth1Session(CK, CS, AT, AS)
    timeline_json = api_OAuth.get("https://api.twitter.com/1.1/statuses/mentions_timeline.json")
    
    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # データをダウンロード
    downloadFromDropbox()

    # ツイートを解析
    myTwitterID = "cper_bot"
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
            userData_json = api_OAuth.get("https://api.twitter.com/1.1/users/show.json?user_id=" + tweet["user"]["id_str"])
            userData = json.loads(userData_json.text)

            if len(tweetSplited) == 4:

                # AtCoder-detection (setFlag)
                if tweetSplited[1] == "setFlag_atcoder" and (tweetSplited[3] == "on" or tweetSplited[3] == "off"):
                    tweetText = "@" + str(userData["screen_name"]) + "\n"
                    tweetText += AtCoder.detection.setFlag(tweetSplited[2], str(userData["screen_name"]), tweetSplited[3])
                    api.update_status(tweetText + timeStamp, in_reply_to_status_id = tweet["id"])
                    print("cper_bot-twitter: Tweeted " + tweetSplited[2] + "'s AtCoder detection flag change")

            if len(tweetSplited) >= 3:
                
                # AtCoder-status
                if tweetSplited[1] == "status_atcoder":
                    tweetText = "@" + str(userData["screen_name"]) + "\n"
                    tweetText += AtCoder.status.status(tweetSplited[2])
                    api.update_status(tweetText + timeStamp, in_reply_to_status_id = tweet["id"])
                    print("cper_bot-twitter: Tweeted " + tweetSplited[2] + "'s AtCoder status")
                    
                # AtCoder-register (register)
                if tweetSplited[1] == "reg_atcoder":
                    tweetText = AtCoder.register.register(tweetSplited[2], str(userData["screen_name"]), 0)
                    api.update_status(tweetText + timeStamp, in_reply_to_status_id = tweet["id"])
                    print("cper_bot-twitter: Tweeted " + tweetText)

                # AtCoder-register (unregister)
                if tweetSplited[1] == "del_atcoder":
                    tweetText = AtCoder.register.register(tweetSplited[2], str(userData["screen_name"]), 1)
                    api.update_status(tweetText + timeStamp, in_reply_to_status_id = tweet["id"])
                    print("cper_bot-twitter: Tweeted " + tweetText)

                # AOJ-register (register)
                if tweetSplited[1] == "reg_aoj":
                    tweetText = AOJ.register.register(tweetSplited[2], str(userData["screen_name"]), 0)
                    api.update_status(tweetText + timeStamp, in_reply_to_status_id = tweet["id"])
                    print("cper_bot-twitter: Tweeted " + tweetText)

                # AOJ-register (unregister)
                if tweetSplited[1] == "del_aoj":
                    tweetText = AOJ.register.register(tweetSplited[2], str(userData["screen_name"]), 1)
                    api.update_status(tweetText + timeStamp, in_reply_to_status_id = tweet["id"])
                    print("cper_bot-twitter: Tweeted " + tweetText)

                # CF-register (register)
                if tweetSplited[1] == "reg_cf":
                    tweetText = CF.register.register(tweetSplited[2], str(userData["screen_name"]), 0)
                    api.update_status(tweetText + timeStamp, in_reply_to_status_id = tweet["id"])
                    print("cper_bot-twitter: Tweeted " + tweetText)

                # CF-register (unregister)
                if tweetSplited[1] == "del_cf":
                    tweetText = CF.register.register(tweetSplited[2], str(userData["screen_name"]), 1)
                    api.update_status(tweetText + timeStamp, in_reply_to_status_id = tweet["id"])
                    print("cper_bot-twitter: Tweeted " + tweetText)

                # YK-register (register)
                if tweetSplited[1] == "reg_yk":
                    tweetText = YK.register.register(tweetSplited[2], str(userData["screen_name"]), 0)
                    api.update_status(tweetText + timeStamp, in_reply_to_status_id = tweet["id"])
                    print("cper_bot-twitter: Tweeted " + tweetText)

                # YK-register (unregister)
                if tweetSplited[1] == "del_yk":
                    tweetText = YK.register.register(tweetSplited[2], str(userData["screen_name"]), 1)
                    api.update_status(tweetText + timeStamp, in_reply_to_status_id = tweet["id"])
                    print("cper_bot-twitter: Tweeted " + tweetText)

            if len(tweetSplited) == 2:

                # info
                if tweetSplited[1] == "info":
                    tweetText = info.info()
                    api.update_status(tweetText + timeStamp, in_reply_to_status_id = tweet["id"])
                    print("cper_bot-twitter: Tweeted " + tweetText)

        # 変更されたデータをアップロード
        lastTweetID = int(timeline[0]["id_str"])
        uploadToDropbox()

    else:
        print("cper_bot-twitter: Twitter API Error: %d" % timeline_json.status_code)

    print("cper_bot-twitter: ----- twitter End -----")

# おまじない
sched.start()
