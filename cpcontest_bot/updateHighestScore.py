# import
import os
import tweepy
import dropbox
import pickle
import datetime
import requests
from bs4 import BeautifulSoup
import json

scores = {}

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global scores

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # scores をダウンロード
    dbx.files_download_to_file("atcontest_bc/scores.txt", "/atcontest_bc/scores.txt")
    dbx.files_delete("/atcontest_bc/scores.txt")
    with open("atcontest_bc/scores.txt", "rb") as f:
        scores = pickle.load(f)
    print("atcontest_bc-updateHighestScore: Downloaded scores (size : ", str(len(scores)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global scores

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # scores をアップロード
    with open("atcontest_bc/scores.txt", "wb") as f:
        pickle.dump(scores, f)
    with open("atcontest_bc/scores.txt", "rb") as f:
        dbx.files_upload(f.read(), "/atcontest_bc/scores.txt")
    print("atcontest_bc-updateHighestScore: Uploaded scores (size : ", str(len(scores)), ")")

def updateHighestScore(contests):

    global scores

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

    # 順位表から最高得点を見つける
    for contest in contests:

        # コンテスト名を取得
        topHTML = requests.get("https://atcoder.jp/contests/" + str(contest))
        try:
            topHTML.raise_for_status()
            topData = BeautifulSoup(topHTML.text, "html.parser")
        except:
            print("atcontest_bc-updateHighestScore: topHTML Error")
            break
        contestName = str(topData.contents[3].contents[1].contents[1].contents[0])[0:-10]

        # 順位表 json データを取得
        session = requests.Session()
        request = session.get(url = "https://atcoder.jp/contests/" + str(contest) + "/standings/json")
        standingsJsonData = json.loads(request.text)
        print("atcontest_bc-updateHighestScore: Downloaded standingsJsonData")

        for task in standingsJsonData["TaskInfo"]:
            if task["TaskScreenName"] not in scores:
                scores[task["TaskScreenName"]] = 0
        for task in standingsJsonData["TaskInfo"]:
            maxScore = -1
            maxUser = ""
            for rows in standingsJsonData["StandingsData"]:
                if task["TaskScreenName"] not in rows["TaskResults"]:
                    continue
                userScore = int(rows["TaskResults"][task["TaskScreenName"]]["Score"])
                if (maxScore == -1 or userScore > maxScore) and userScore > 0:
                    maxScore = int(rows["TaskResults"][task["TaskScreenName"]]["Score"])
                    maxUser = str(rows["UserScreenName"])
            if maxScore > scores[task["TaskScreenName"]]:
                scores[task["TaskScreenName"]] = maxScore
                api.update_status("〔" + contestName + " 実況〕\n" + maxUser + " さんが " +  task["Assignment"] + " 問題で " + str(maxScore / 100) + " 点を獲得し，最高得点を更新しました！\nhttps://atcoder.jp/contests/" + contest + "/standings\n" + timeStamp)
                print("atcontest_bc-updateHighestScore: detected " + str(task["TaskScreenName"]) + " updated the highest score (" + maxUser + ")")

    uploadToDropbox()

if __name__ == '__main__':
    print("atcontest_bc-FA: Running as debug...")
    updateHighestScore("abc001")
    print("atcontest_bc-FA: Debug finished")
