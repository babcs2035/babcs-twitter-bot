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
AtCoderIDs = []

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global scores
    global AtCoderIDs

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # scores をダウンロード
    dbx.files_download_to_file("cpcontest_bot/scores.txt", "/cpcontest_bot/scores.txt")
    dbx.files_delete("/cpcontest_bot/scores.txt")
    with open("cpcontest_bot/scores.txt", "rb") as f:
        scores = pickle.load(f)
    print("cpcontest_bot-updateHighestScore: Downloaded scores (size : ", str(len(scores)), ")")

    # AtCoderIDs をダウンロード
    dbx.files_download_to_file("cpcontest_bot/AtCoderIDs.txt", "/cpcontest_bot/AtCoderIDs.txt")
    with open("cpcontest_bot/AtCoderIDs.txt", "rb") as f:
        AtCoderIDs = pickle.load(f)
    print("cpcontest_bot-updateHighestScore: Downloaded AtCoderIDs (size : ", str(len(AtCoderIDs)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global scores

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # scores をアップロード
    with open("cpcontest_bot/scores.txt", "wb") as f:
        pickle.dump(scores, f)
    with open("cpcontest_bot/scores.txt", "rb") as f:
        dbx.files_upload(f.read(), "/cpcontest_bot/scores.txt")
    print("cpcontest_bot-updateHighestScore: Uploaded scores (size : ", str(len(scores)), ")")

def sec_to_time(sec):
    return str(int(sec / 60)) + ":" + str(int(sec % 60)).zfill(2)

def updateHighestScore(contests):

    global scores
    global AtCoderIDs

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
    login_info = {
        "name": os.environ["ATCODER_ID"],
        "password" : os.environ["ATCODER_PASSWORD"]
    }
    for contest in contests:

        # コンテスト名を取得
        session = requests.session()
        topHTML = session.post("https://" + str(contest) + ".contest.atcoder.jp/login", data = login_info)
        try:
            topHTML.raise_for_status()
            topData = BeautifulSoup(topHTML.text, "html.parser")
        except:
            print("cpcontest_bot-updateHighestScore: topHTML Error (contest = " + contest + ")")
            break
        contestName = str(topData.find("h1", class_ = "site-title").contents[0])[11:-7]

        # 順位表 json データを取得
        session = requests.Session()
        request = session.post("https://" + str(contest) + ".contest.atcoder.jp/standings/json", data = login_info)
        try:
            standingsJsonData = json.loads(request.text)
            print("cpcontest_bot-updateHighestScore: Downloaded standingsJsonData")
        except:
            print("cpcontest_bot-updateHighestScore: standingsJsonData Error")
            break


        for task in standingsJsonData["response"][0]["tasks"]:
            if task["task_screen_name"] not in scores:
                scores[task["task_screen_name"]] = 0
        taskIndex = 0
        for task in standingsJsonData["response"][0]["tasks"]:
            maxScore = -1
            minTime = "-1"
            maxUser = ""
            firstFlag = True
            for rows in standingsJsonData["response"]:
                if firstFlag:
                    firstFlag = False
                    continue
                if rows["tasks"][taskIndex]["score"] == 0:
                    continue
                userScore = int(rows["tasks"][taskIndex]["score"])
                userTime = str(rows["tasks"][taskIndex]["elapsed_time"])
                if (maxScore == -1 or userScore >= maxScore) and userScore > 0 and (minTime == "-1" or userTime < minTime):
                    maxScore = userScore
                    minTime = userTime
                    maxUser = str(rows["user_screen_name"])
            if maxScore > scores[task["task_screen_name"]]:
                flag = False
                userTwitterID = ""
                for atcoderID, twitterID in AtCoderIDs:
                    if atcoderID == maxUser:
                        flag = True
                        userTwitterID = twitterID
                        break
                scores[task["task_screen_name"]] = maxScore
                assign = chr(ord('A') + taskIndex)
                if flag:
                    api.update_status("〔" + contestName + " 実況〕\n" + maxUser + " ( @" + userTwitterID + " ) さんが " + assign + " 問題で " + str(maxScore) + " 点を " + minTime + " に獲得し，最高得点を更新しました！\nhttps://atcoder.jp/contests/" + contest + "/standings\n" + timeStamp)
                else:
                    api.update_status("〔" + contestName + " 実況〕\n" + maxUser + " さんが " + assign + " 問題で " + str(maxScore) + " 点を " + minTime + " に獲得し，最高得点を更新しました！\nhttps://atcoder.jp/contests/" + contest + "/standings\n" + timeStamp)
                print("cpcontest_bot-updateHighestScore: detected " + str(task["task_screen_name"]) + " updated the highest score (" + maxUser + ")")
            taskIndex += 1
    uploadToDropbox()

if __name__ == '__main__':
    print("cpcontest_bot-FA: Running as debug...")
    updateHighestScore(["abc001"])
    print("cpcontest_bot-FA: Debug finished")
