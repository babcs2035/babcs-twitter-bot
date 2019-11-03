# import
import os
import tweepy
import dropbox
import pickle
import datetime
import requests
from bs4 import BeautifulSoup
import json

top20s = {}

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global top20s

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # top20s をダウンロード
    dbx.files_download_to_file("atcontest_bc/top20s.txt", "/atcontest_bc/top20s.txt")
    dbx.files_delete("/atcontest_bc/top20s.txt")
    with open("atcontest_bc/top20s.txt", "rb") as f:
        top20s = pickle.load(f)
    print("atcontest_bc-top20: Downloaded top20s (size : ", str(len(top20s)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global top20s

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # top20s をアップロード
    with open("atcontest_bc/top20s.txt", "wb") as f:
        pickle.dump(top20s, f)
    with open("atcontest_bc/top20s.txt", "rb") as f:
        dbx.files_upload(f.read(), "/atcontest_bc/top20s.txt")
    print("atcontest_bc-top20: Uploaded top20s (size : ", str(len(top20s)), ")")

def top20(contests):

    global top20s

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

    # 順位表から順位の浮上を見つける
    for contest in contests:

        # コンテスト名を取得
        topHTML = requests.get("https://atcoder.jp/contests/" + str(contest))
        try:
            topHTML.raise_for_status()
            topData = BeautifulSoup(topHTML.text, "html.parser")
        except:
            print("atcontest_bc-top20: topHTML Error")
            break
        contestName = str(topData.contents[3].contents[1].contents[1].contents[0])[0:-10]

        # 順位表 json データを取得
        session = requests.Session()
        request = session.get(url = "https://atcoder.jp/contests/" + str(contest) + "/standings/json")
        standingsJsonData = json.loads(request.text)
        print("atcontest_bc-top20: Downloaded standingsJsonData")

        newData = {}
        for rows in standingsJsonData["StandingsData"]:
            if contest in top20s:
                if rows["UserScreenName"] in top20s[contest]:
                    if top20s[contest][rows["UserScreenName"]] > rows["Rank"] and rows["Rank"] <= 20:
                        api.update_status("〔" + contestName + " 実況〕\n" + rows["UserScreenName"] + " さんが " + str(top20s[contest][rows["UserScreenName"]]) + " 位から " + str(rows["Rank"]) + " 位に浮上しました！\nhttps://atcoder.jp/contests/" + contest + "/standings\n" + timeStamp)
                        print("atcontest_bc-top20: detected top20 updated (" + rows["UserScreenName"] + ")")
            newData[rows["UserScreenName"]] = rows["Rank"]
        top20s[contest] = newData
    uploadToDropbox()

if __name__ == '__main__':
    print("atcontest_bc-top20: Running as debug...")
    top20(["abc001"])
    print("atcontest_bc-top20: Debug finished")
