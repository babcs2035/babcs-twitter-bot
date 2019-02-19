# import
import os
import tweepy
import datetime
import json
import dropbox
import urllib
from bs4 import BeautifulSoup
import requests
import pickle

# グローバル変数
AtCoderID = []
TwitterID = []
lastSubID = {}

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global AtCoderID
    global TwitterID
    global lastSubID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # AtCoderID をダウンロード
    dbx.files_download_to_file("AtCoder/AtCoderID.txt", "/AtCoder/AtCoderID.txt")
    with open("AtCoder/AtCoderID.txt", "r") as f:
        AtCoderID.clear()
        for id in f:
            AtCoderID.append(id.rstrip("\n"))
    print("AtCoder-detection: Downloaded AtCoderID (size : ", str(len(AtCoderID)), ")")
    
    # TwitterID をダウンロード
    dbx.files_download_to_file("AtCoder/TwitterID.txt", "/AtCoder/TwitterID.txt")
    with open("AtCoder/TwitterID.txt", "r") as f:
        TwitterID.clear()
        for id in f:
            TwitterID.append(id.rstrip("\n"))
    print("AtCoder-detection: Downloaded TwitterID (size : ", str(len(TwitterID)), ")")
    
    #lastSubID をダウンロード
    dbx.files_download_to_file("AtCoder/lastSubID.txt", "/AtCoder/lastSubID.txt")
    with open("AtCoder/lastSubID.txt", "rb") as f:
        lastSubID = pickle.load(f)
    print("AtCoder-detection: Downloaded lastSubID (size : ", str(len(lastSubID)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global lastSubID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # lastSubID をアップロード
    with open("AtCoder/lastSubID.txt", "wb") as f:
        pickle.dump(lastSubID, f)
    with open("AtCoder/lastSubID.txt", "rb") as f:
        dbx.files_delete("/AtCoder/lastSubID.txt")
        dbx.files_upload(f.read(), "/AtCoder/lastSubID.txt")
    print("AtCoder-detection: Uploaded lastSubID (size : ", str(len(lastSubID)), ")")

def detection():
    
    # グローバル変数
    global AtCoderID
    global TwitterID
    global lastSubID
    
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
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # データをダウンロード
    downloadFromDropbox()

    # コンテストごとに提出を解析
    contestsJsonRes = urllib.request.urlopen("https://kenkoooo.com/atcoder/resources/contests.json")
    contestsJsonData = json.loads(contestsJsonRes.read().decode("utf-8"))
    print("AtCoder-detection: Downloaded contestsJsonData")

    for contest in contestsJsonData:

        # ページ送り
        sublistPageNum = 1
        subCount = 0
        newLastSubID = -1

        while True:
            sublistURL = "https://atcoder.jp/contests/" + str(contest["id"]) + "/submissions?page=" + str(sublistPageNum)
            sublistHTML = requests.get(sublistURL)
            try:
                sublistHTML.raise_for_status()
                sublistData = BeautifulSoup(sublistHTML.text, "html.parser")
            except:
                print("AtCoder-detection: sublistHTML Error")
                break
            sublistTable = sublistData.find_all("table", class_ = "table table-bordered table-striped small th-center")
            if len(sublistTable) == 0:
                break

            # １行ずつ解析
            sublistRows = sublistTable[0].find_all("tr")
            del sublistRows[0]
            skipFlag = False
            for row in sublistRows:
                links = row.find_all("a")
                subID = int(str(links[3].get("href")).split("/")[4])
                userID = str(links[1].get("href")).split("/")[2]
                if newLastSubID == -1:
                    newLastSubID = subID
                if subID <= int(lastSubID[str(contest["id"])]) or int(lastSubID[str(contest["id"])]) == -1:
                    skipFlag = True
                    break
                subCount = subCount + 1

                # ユーザーの AC 提出かどうか判定
                subData = [cell.get_text() for cell in row.select("td")]
                if subData[6] == "AC":
                    idx = 0
                    for ids in AtCoderID:
                        if userID == ids:
                            # score = int(float(str(subData[4])))
                            # imagePath = "AtCoder/data/detection/"
                            # if score <= 100:
                            #     imagePath = imagePath + "100"
                            # elif score <= 200:
                            #     imagePath = imagePath + "200"
                            # elif score <= 300:
                            #     imagePath = imagePath + "300"
                            # elif score <= 400:
                            #     imagePath = imagePath + "400"
                            # elif score <= 600:
                            #     imagePath = imagePath + "600"
                            # elif score <= 800:
                            #     imagePath = imagePath + "800"
                            # elif score <= 1100:
                            #     imagePath = imagePath + "1100"
                            # elif score <= 1500:
                            #     imagePath = imagePath + "1500"
                            # elif score <= 1900:
                            #     imagePath = imagePath + "1900"
                            # else:
                            #     imagePath = imagePath + "2000"
                            # imagePath = imagePath + ".png"
                            try:
                                # api.update_with_media(filename = imagePath, status = userID + " ( @" + TwitterID[idx] + " ) さんが " + str(contest["title"]) + "：" + str(subData[1]) + " を AC しました！\n提出ソースコード：" + "https://atcoder.jp" + str(links[3].get("href")) + "\n" + timeStamp)
                                api.update_status(userID + " ( @" + TwitterID[idx] + " ) さんが <AtCoder> " + str(contest["title"]) + "：" + str(subData[1]) + " を AC しました！\nhttps://atcoder.jp" + str(links[3].get("href")) + "\n" + timeStamp)
                                print("AtCoder-detection: " + userID + " ( @" + TwitterID[idx] + " ) 's new AC submission (contest : " + str(contest["title"]) + ", problem : " + str(subData[1]) + ")")
                            except:
                                print("AtCoder-detection: Tweet Error")
                        idx = idx + 1
            if skipFlag:
                break
            sublistPageNum = sublistPageNum + 1

        # lastSubID を更新
        lastSubID[str(contest["id"])] = newLastSubID
        print("AtCoder-detection: Checked " + contest["title"] + " submissions (subCount : " + str(subCount) + ", newlastSubID : " + str(lastSubID[str(contest["id"])]) + ")")

    # データをアップロード
    uploadToDropbox()

if __name__ == '__main__':
    print("AtCoder-detection: Running as debug...")
    detection()
    print("AtCoder-detection: Debug finished")
