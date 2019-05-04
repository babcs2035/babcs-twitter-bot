# import
import os
import tweepy
import json
import dropbox
import urllib
import pickle

# グローバル変数
acCount = {}
acPoint = {}

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global acCount
    global acPoint

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # acCount をダウンロード
    dbx.files_download_to_file("AtCoder/daily_acCount.txt", "/AtCoder/daily_acCount.txt")
    with open("AtCoder/daily_acCount.txt", "rb") as f:
        acCount = pickle.load(f)
    print("AtCoder-status: Downloaded daily acCount (size : ", str(len(acCount)), ")")
    
    # acPoint をダウンロード
    dbx.files_download_to_file("AtCoder/daily_acPoint.txt", "/AtCoder/daily_acPoint.txt")
    with open("AtCoder/daily_acPoint.txt", "rb") as f:
        acPoint = pickle.load(f)
    print("AtCoder-status: Downloaded daily acPoint (size : ", str(len(acPoint)), ")")

def status(atcoderID):

    # グローバル変数
    global acCount
    global acPoint

    # 各種キー設定
    CK = os.environ["CONSUMER_KEY"]
    CS = os.environ["CONSUMER_SECRET"]
    AT = os.environ["ACCESS_TOKEN_KEY"]
    AS = os.environ["ACCESS_TOKEN_SECRET"]

    # Twitter オブジェクトの生成
    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    api = tweepy.API(auth)
    
    # データをダウンロード
    downloadFromDropbox()

    # json 形式で取得
    userJson = urllib.request.urlopen("https://kenkoooo.com/atcoder/atcoder-api/v2/user_info?user=" + urllib.parse.quote_plus(atcoderID, encoding = "utf-8"))
    userData = json.loads(userJson.read().decode("utf-8"))
    print("AtCoder-status: Downloaded " + atcoderID + "'s userData")

    tweetText = ""
    if atcoderID in acCount:
        tweetText += "今日の Unique AC 数 : " + str(int(userData["accepted_count"]) - int(acCount[atcoderID])) + "\n"
    if atcoderID in acPoint:
        tweetText += "今日の Unique AC の Rated Point Sum : " + str(int(userData["rated_point_sum"]) - int(acPoint[atcoderID])) + "\n"
    if atcoderID in acCount and atcoderID in acPoint:
        if int(userData["accepted_count"]) - int(acCount[atcoderID]) > 0:
            tweetText += "今日の Rated Point Sum / Unique AC 数 : " + str((int(userData["rated_point_sum"]) - int(acPoint[atcoderID])) / (int(userData["accepted_count"]) - int(acCount[atcoderID]))) + "\n"
    else:
        tweetText += "この AtCoder ID は登録されていません！\n"
    return tweetText

if __name__ == '__main__':
    print("AtCoder-status: Running as debug...")
    print(status("Bwambocos"))
    print("AtCoder-status: Debug finished")
