# import
import os
import tweepy
import datetime
import random

announceMessages = ["この Bot の名前を募集中です．リプライ・DM にて受付中です！",
    "この Bot は開発中です．AtCoder Problems の API を使用する予定です．何かご意見がありましたら，リプライ・DM にて受付中です！",
    "この Bot の作者は Bwambocos ( @babcs2035 ) です．意見・不満・批判はこちらへお願いします！"]

def announce():

    # 各種キー設定
    CK = os.environ["CONSUMER_KEY"]
    CS = os.environ["CONSUMER_SECRET"]
    AT = os.environ["ACCESS_TOKEN_KEY"]
    AS = os.environ["ACCESS_TOKEN_SECRET"]
    
    # Twitter オブジェクトの生成
    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    api = tweepy.API(auth)

    # 時刻表示を作成
    timeStamp = datetime.datetime.today() + datetime.timedelta(hours=9)
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # ツイート
    announceMessage = announceMessages[random.randrange(len(announceMessages))]
    api.update_status("＜定期＞\n" + announceMessage + "\n" + timeStamp)
    print("announce: ツイート完了：" + announceMessage)
