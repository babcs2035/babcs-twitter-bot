# import
import os
import tweepy
import datetime
from requests_oauthlib import OAuth1Session
import json

def followBack():

    # 各種キー設定
    CK = os.environ["CONSUMER_KEY"]
    CS = os.environ["CONSUMER_SECRET"]
    AT = os.environ["ACCESS_TOKEN_KEY"]
    AS = os.environ["ACCESS_TOKEN_SECRET"]
    
    # Twitter オブジェクトの生成
    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    api = tweepy.API(auth)
    
    # フォロバ
    followers = api.followers_ids("cper_bot")
    friends = api.friends_ids("cper_bot")
    set_apr = set(followers) - set(friends)
    list_apr = list(set_apr)
    followedCnt = 0
    followedList = []
    for user in list_apr:
        try:
            api.create_friendship(user)
            print("cper_bot-followBack: Created friendship with %s" % user) 
            followedCnt = followedCnt + 1
            # OAuth でツイートを取得
            api_OAuth = OAuth1Session(CK, CS, AT, AS)
            user_json = api_OAuth.get("https://api.twitter.com/1.1/users/show.json?user_id=" + str(user))
            user_data = json.loads(user_json.text)
            followedList.append({"user_name" : user_data["name"], "user_id" : user_data["screen_name"]})
        except tweepy.error.TweepError:
            print("cper_bot-followBack: Could not create friendship with %s" % user)
    followStr = "新しく " + str(followedCnt) + " 人をフォローしました：\n"
    for user in followedList:
        followStr += str(user["user_name"]) + " ( @" + str(user["user_id"]) + " )\n"

    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # ツイート
    if followedCnt > 0:
        api.update_status(followStr + "\n" + timeStamp)
    print("cper_bot-followBack: 新規フォロー " + str(followedCnt) + " 人")

if __name__ == '__main__':
    print("cper_bot-followBack: Running as debug...")
    followBack()
    print("cper_bot-followBack: Debug finished")
