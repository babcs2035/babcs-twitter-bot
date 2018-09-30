# import
import os
import tweepy
import datetime
import json
import urllib.request
import dropbox
from requests_oauthlib import OAuth1Session

# 最後に取得したツイート ID
lastTweetID = 0
AtCoderID = []
TwitterID = []

# AtCoder ID が存在するか確認
def checkID(atcoderID):

    # AtCoder ユーザーページにアクセス
    try:
        html = urllib.request.urlopen("https://beta.atcoder.jp/users/" + atcoderID)
        print("register: " + atcoderID + " is correct AtCoder ID")
        return True
    except:
        print("register: " + atcoderID + " is not correct AtCoder ID")
        return False

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global lastTweetID
    global AtCoderID
    global TwitterID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # lastTweetID をダウンロード
    dbx.files_download_to_file("lastTweetID.txt", "/lastTweetID.txt")
    with open("lastTweetID.txt", "r") as f:
        lastTweetID = f.readline()
    print("register: Downloaded lastTweetID : ", str(lastTweetID))
    
    # AtCoderID をダウンロード
    dbx.files_download_to_file("AtCoderID.txt", "/AtCoderID.txt")
    with open("AtCoderID.txt", "r") as f:
        AtCoderID.clear()
        for id in f:
            AtCoderID.append(id.rstrip("\n"))
    print("register: Downloaded AtCoderID (size : ", str(len(AtCoderID)), ")")

    # TwitterID をダウンロード
    dbx.files_download_to_file("TwitterID.txt", "/TwitterID.txt")
    with open("TwitterID.txt", "r") as f:
        TwitterID.clear()
        for id in f:
            TwitterID.append(id.rstrip("\n"))
    print("register: Downloaded TwitterID (size : ", str(len(TwitterID)), ")")

# Dropbox にアップロード
def uploadToDropbox():

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # lastTweetID をアップロード
    with open("lastTweetID.txt", "w") as f:
        f.write(str(lastTweetID))
    with open("lastTweetID.txt", "rb") as f:
        dbx.files_delete("/lastTweetID.txt")
        dbx.files_upload(f.read(), "/lastTweetID.txt")
    print("register: Uploaded lastTweetID : ", str(lastTweetID))
    
    # AtCoderID をアップロード
    with open("AtCoderID.txt", "w") as f:
        for id in AtCoderID:
            f.write(str(id) + "\n")
    with open("AtCoderID.txt", "rb") as f:
        dbx.files_delete("/AtCoderID.txt")
        dbx.files_upload(f.read(), "/AtCoderID.txt")
    print("register: Uploaded AtCoderID (size : ", str(len(AtCoderID)), ")")

    # TwitterID をアップロード
    with open("TwitterID.txt", "w") as f:
        for id in TwitterID:
            f.write(str(id) + "\n")
    with open("TwitterID.txt", "rb") as f:
        dbx.files_delete("/TwitterID.txt")
        dbx.files_upload(f.read(), "/TwitterID.txt")
    print("register: Uploaded TwitterID (size : ", str(len(TwitterID)), ")")

def register():
    
    # グローバル変数
    global lastTweetID
    global AtCoderID
    global TwitterID
    
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
    timeStamp = datetime.datetime.today() + datetime.timedelta(hours=9)
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # データをダウンロード
    downloadFromDropbox()

    # ツイートを解析
    myTwitterID = "babcs_bot"
    likedCnt = 0
    if timeline_json.status_code == 200:
        timeline = json.loads(timeline_json.text)
        for tweet in timeline:
            if int(tweet["id_str"]) <= int(lastTweetID):
                break
            tweetText = str(tweet["text"])
            tweetSplited = tweetText.split()
            if len(tweetSplited) >= 3:
                if tweetSplited[1] == "reg":
                    userData_json = api_OAuth.get("https://api.twitter.com/1.1/users/show.json?user_id=" + tweet["user"]["id_str"])
                    userData = json.loads(userData_json.text)
                    if checkID(tweetSplited[2]):
                        AtCoderID.append(tweetSplited[2])
                        TwitterID.append(userData["screen_name"])
                        api.update_status("@" + str(userData["screen_name"]) + " AtCoder ID を登録しました！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                        print("register: Register new AtCoder ID : " + tweetSplited[2])
                    else:
                        api.update_status("@" + str(userData["screen_name"]) + " 正しい AtCoder ID ではありません！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                        print("register: Reject to register new AtCoder ID : " + tweetSplited[2])
        lastTweetID = int(timeline[0]["id_str"])

        # データをアップロード
        uploadToDropbox()
    else:
        print("register: Twitter API Error: %d" % timeline_json.status_code)
