# import
import os
import tweepy
import datetime
import json
import urllib.request
import dropbox
from apscheduler.schedulers.blocking import BlockingScheduler
from requests_oauthlib import OAuth1Session

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

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # lastTweetID をアップロード
    if idFixedFlag:
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

    print("twitter: ----- twitter Start -----")

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
    myTwitterID = "babcs_bot"
    defSubID = 0
    idFixedFlag = False
    if timeline_json.status_code == 200:
        timeline = json.loads(timeline_json.text)
        for tweet in timeline:
            if int(tweet["id_str"]) <= int(lastTweetID):
                break
            idFixedFlag = True
        lastTweetID = int(timeline[0]["id_str"])

        # 変更されたデータをアップロード
        uploadToDropbox()

    else:
        print("twitter: Twitter API Error: %d" % timeline_json.status_code)

    print("twitter: ----- twitter End -----")

# おまじない
sched.start()
