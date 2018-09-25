# import
import os
import tweepy
import datetime
import json
from requests_oauthlib import OAuth1Session

# 最後に取得したツイート ID
lastTweetID = 0

def register():
    
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
    timeline_json = api_OAuth.get("https://api.twitter.com/1.1/statuses/home_timeline.json", params = {"count" : 200})
    
    # 時刻表示を作成
    timeStamp = datetime.datetime.today() + datetime.timedelta(hours=9)
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # ツイートを解析
    myTwitterID = "babcs_bot"
    likedCnt = 0
    if timeline_json.status_code == 200:
        timeline = json.loads(timeline_json.text)
        for tweet in timeline:
            if int(tweet["id_str"]) <= lastTweetID:
                break
            tweetText = str(tweet["text"])
            tweetSplited = tweetText.split()
            if len(tweetSplited) >= 3:
                if tweetSplited[1] == "reg":
                    if tweetSplited[2].encode('utf-8').isalpha():
                        api.update_status("@" + str(userData["screen_name"]) + " AtCoder ID を登録しました！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                        print("Register new AtCoder ID : " + tweetSplited[2])
                    else:
                        userData_json = api_OAuth.get("https://api.twitter.com/1.1/users/show.json?user_id=" + tweet["user"]["id_str"])
                        userData = json.loads(userData_json.text)
                        api.update_status("@" + str(userData["screen_name"]) + " AtCoder ID の形式を満たしていません！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                        print("Reject to register new AtCoder ID : " + tweetSplited[2])
        lastTweetID = int(timeline[0]["id_str"])
    else:
        print("Error: %d" % req.status_code)
