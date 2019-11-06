# import
import os
import tweepy
import dropbox
import pickle
import datetime
import requests
from bs4 import BeautifulSoup
import json

def sec_to_time(sec):
    return str(int(sec / 60)) + ":" + str(int(sec % 60)).zfill(2)

FAFlags = {}

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global FAFlags

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # FAFlags をダウンロード
    dbx.files_download_to_file("cpcontest_bot/FAFlags.txt", "/cpcontest_bot/FAFlags.txt")
    dbx.files_delete("/cpcontest_bot/FAFlags.txt")
    with open("cpcontest_bot/FAFlags.txt", "rb") as f:
        FAFlags = pickle.load(f)
    print("cpcontest_bot-top20: Downloaded FAFlags (size : ", str(len(FAFlags)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global FAFlags

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # FAFlags をアップロード
    with open("cpcontest_bot/FAFlags.txt", "wb") as f:
        pickle.dump(FAFlags, f)
    with open("cpcontest_bot/FAFlags.txt", "rb") as f:
        dbx.files_upload(f.read(), "/cpcontest_bot/FAFlags.txt")
    print("cpcontest_bot-top20: Uploaded FAFlags (size : ", str(len(FAFlags)), ")")

def FA(contests):

    global FAFlags

    # 各種キー設定
    CK = os.environ["CONSUMER_KEY2"]
    CS = os.environ["CONSUMER_SECRET2"]
    AT = os.environ["ACCESS_TOKEN_KEY2"]
    AS = os.environ["ACCESS_TOKEN_SECRET2"]
    
    # Twitter オブジェクトの生成
    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    api = tweepy.API(auth)

    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    downloadFromDropbox()

    # 順位表から FA を見つける
    for contest in contests:

        # コンテスト名を取得
        topHTML = requests.get("https://atcoder.jp/contests/" + str(contest))
        try:
            topHTML.raise_for_status()
            topData = BeautifulSoup(topHTML.text, "html.parser")
        except:
            print("cpcontest_bot-FA: topHTML Error")
            break
        contestName = str(topData.contents[3].contents[1].contents[1].contents[0])[0:-10]

        # 順位表 json データを取得
        session = requests.Session()
        request = session.get(url = "https://atcoder.jp/contests/" + str(contest) + "/standings/json")
        standingsJsonData = json.loads(request.text)
        print("cpcontest_bot-FA: Downloaded standingsJsonData")

        for task in standingsJsonData["TaskInfo"]:
            if task["TaskScreenName"] not in FAFlags:
                FAFlags[task["TaskScreenName"]] = False
        for task in standingsJsonData["TaskInfo"]:
            if FAFlags[task["TaskScreenName"]]:
                continue
            minTime = -1
            minUser = ""
            for rows in standingsJsonData["StandingsData"]:
                if task["TaskScreenName"] not in rows["TaskResults"]:
                    continue
                userTime = int(rows["TaskResults"][task["TaskScreenName"]]["Elapsed"])
                if (minTime == -1 or userTime < minTime) and userTime > 0:
                    minTime = int(rows["TaskResults"][task["TaskScreenName"]]["Elapsed"])
                    minUser = str(rows["UserScreenName"])
            if minTime != -1:
                FAFlags[task["TaskScreenName"]] = True
                minTime /= 1000000000
                api.update_status("〔" + contestName + " 実況〕\n" + task["Assignment"] + " 問題の FA を " + str(sec_to_time(minTime)) + " で " + minUser + " さんが獲得しました！\nhttps://atcoder.jp/contests/" + contest + "/standings\n" + timeStamp)
                print("cpcontest_bot-FA: detected " + str(task["TaskScreenName"]) + " FA (" + minUser + ")")

    uploadToDropbox()

if __name__ == '__main__':
    print("cpcontest_bot-FA: Running as debug...")
    FA(["abc001"])
    print("cpcontest_bot-FA: Debug finished")
