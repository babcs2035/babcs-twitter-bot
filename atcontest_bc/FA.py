# import
import os
import tweepy
import datetime
import requests
from bs4 import BeautifulSoup
import json

def sec_to_time(sec):
    return str(int(sec / 60)) + ":" + str(int(sec % 60)).zfill(2)

FAFlags = {}

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

    # 順位表から FA を見つける
    for contest in contests:

        # コンテスト名を取得
        topHTML = requests.get("https://atcoder.jp/contests/" + str(contest))
        try:
            topHTML.raise_for_status()
            topData = BeautifulSoup(topHTML.text, "html.parser")
        except:
            print("atcontest_bc-FA: topHTML Error")
            break
        contestName = str(topData.contents[3].contents[1].contents[1].contents[0])[0:-10]

        # 順位表 json データを取得
        session = requests.Session()
        request = session.get(url = "https://atcoder.jp/contests/" + str(contest) + "/standings/json")
        standingsJsonData = json.loads(request.text)
        print("atcontest_bc-FA: Downloaded standingsJsonData")

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
                api.update_status("〔" + contestName + " 実況〕\n" + task["Assignment"] + " 問題の FA を " + str(sec_to_time(minTime)) + " で " + minUser + " さんが獲得しました！！！おめでとうございます！\nhttps://atcoder.jp/users/" + minUser + "\n" + timeStamp)
                print("atcontest_bc-FA: detected " + str(task["TaskScreenName"]) + " FA (" + minUser + ")")

if __name__ == '__main__':
    print("atcontest_bc-FA: Running as debug...")
    FA("abc001")
    print("atcontest_bc-FA: Debug finished")
