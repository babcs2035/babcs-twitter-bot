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
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    dbx.files_download_to_file('lastTweetID.txt', '/lastTweetID.txt')
    print("register: Downloaded lastTweetID : ", str(lastTweetID))

# Dropbox にアップロード
def uploadToDropbox():
    f = open('lastTweetID.txt','w')
    f.write(str(lastTweetID))
    f.close()
    f = open('lastTweetID.txt','rb')
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    dbx.files_delete('/lastTweetID.txt')
    dbx.files_upload(f.read(), '/lastTweetID.txt')
    f.close()

def register():
    
    # グローバル変数
    global lastTweetID
    
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
    
    # どのツイートまで処理したか取得
    downloadFromDropbox()
    f = open('lastTweetID.txt','r')
    lastTweetID = f.readline()
    f.close()
    print("register: Uploaded lastTweetID : ", str(lastTweetID))

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
                        api.update_status("@" + str(userData["screen_name"]) + " AtCoder ID を登録しました！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                        print("register: Register new AtCoder ID : " + tweetSplited[2])
                    else:
                        api.update_status("@" + str(userData["screen_name"]) + " 正しい AtCoder ID ではありません！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                        print("register: Reject to register new AtCoder ID : " + tweetSplited[2])
        lastTweetID = int(timeline[0]["id_str"])
        uploadToDropbox()
    else:
        print("register: Twitter API Error: %d" % timeline_json.status_code)
