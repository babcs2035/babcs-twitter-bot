# import
import os
import tweepy
import datetime

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
    followers = api.followers_ids("babcs_bot")
    friends = api.friends_ids("babcs_bot")
    set_apr = set(followers) - set(friends)
    list_apr = list(set_apr)
    followedCnt = 0
    for user in list_apr:
        try:
            api.create_friendship(user)
            print("Created friendship with %s" %user) 
            followedCnt = followedCnt + 1
        except tweepy.error.TweepError:
            print("Could not create friendship with %s" %user)
    followStr = "新しく " + str(followedCnt) + " 人をフォローしました！"

    # 時刻表示を作成
    timeStamp = datetime.datetime.today() + datetime.timedelta(hours=9)
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # ツイート
    api.update_status(followStr + "\n" + timeStamp)
