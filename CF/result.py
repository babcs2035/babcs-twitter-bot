# import
import os
import tweepy
import datetime
import dropbox
import pickle
import urllib
import requests
import json
import time
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

# グローバル変数
CFID = []
TwitterID = []

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global CFID
    global TwitterID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # CFID をダウンロード
    dbx.files_download_to_file("CF/CFID.txt", "/CF/CFID.txt")
    with open("CF/CFID.txt", "r") as f:
        CFID.clear()
        for id in f:
            CFID.append(id.rstrip("\n"))
    print("CF-result: Downloaded CFID (size : ", str(len(CFID)), ")")
    
    # TwitterID をダウンロード
    dbx.files_download_to_file("CF/TwitterID.txt", "/CF/TwitterID.txt")
    with open("CF/TwitterID.txt", "r") as f:
        TwitterID.clear()
        for id in f:
            TwitterID.append(id.rstrip("\n"))
    print("CF-result: Downloaded TwitterID (size : ", str(len(TwitterID)), ")")

def epoch_to_datetime(epoch):
    return datetime.datetime(*time.localtime(epoch)[:6])

# list 内の要素の添え字を返す（無い場合は -1）
def myIndex(x, l):
    if x in l:
        return l.index(x)
    else:
        return -1

def makeRanking(type, listData, unit):

    global CFID
    global TwitterID

    flag = int(listData[0][str(type)]) > int(listData[len(listData) - 1][str(type)])
    rankNum = 1
    countNum = 1
    rankingFont = ImageFont.truetype("CF/data/fontR.ttc", 32)
    rankingFirstImg = Image.open("CF/data/result/" + str(type) + "RankingImg (first).jpg")
    resImg = Image.new("RGB", (738 * int((len(listData) + 19) / 20), 65 + 63 * min(len(listData), 20)))
    tweetText = ""
    for idx in range(len(listData)):
        if idx % 20 == 0:
            resImg.paste(rankingFirstImg, (738 * int(idx / 20), 0))
        rankingImg = Image.open("CF/data/result/rankingImg (cell).jpg")
        rankingDraw = ImageDraw.Draw(rankingImg)
        if idx > 0:
            if flag and int(listData[idx - 1][str(type)]) > int(listData[idx][str(type)]):
                rankNum = rankNum + countNum
                countNum = 1
            elif (not flag) and int(listData[idx - 1][str(type)]) < int(listData[idx][str(type)]):
                rankNum = rankNum + countNum
                countNum = 1
            else:
                countNum = countNum + 1
        
        if rankNum + countNum - 1 <= 3:
            tweetText += str(rankNum) + " 位 " + listData[idx]["user"] + " ( @" + str(TwitterID[myIndex(listData[idx]["user"], CFID)]) + " ) " + str(listData[idx][str(type)]) + " " + str(unit) + "\n"
        
        rankingDraw.text((10, 19), str(rankNum), fill = (0, 0, 0), font = rankingFont)
        rankingDraw.text((120, 19), listData[idx]["user"], fill = (0, 0, 0), font = rankingFont)
        rankingDraw.text((560, 19), str(listData[idx][str(type)]), fill = (0, 0, 0), font = rankingFont)
        resImg.paste(rankingImg, (738 * int(idx / 20), 65 + 63 * (idx % 20)))
    resImg.save("CF/data/result/" + str(type) + "RankingImg_fixed.jpg")
    tweetText = " ランキング TOP " + str(rankNum) + "\n" + tweetText
    return tweetText

def result():
    
    # グローバル変数
    global CFID
    global TwitterID

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

    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    ## コンテスト結果のランキング処理
    # 取得すべきコンテストを取得
    contestsJsonRes = urllib.request.urlopen("https://codeforces.com/api/contest.list")
    contestsJsonData = json.loads(contestsJsonRes.read().decode("utf-8"))
    print("CF-result: Downloaded contestsJsonData")
    newcontests = []
    yesterday = datetime.datetime.today() - datetime.timedelta(1)
    for contest in contestsJsonData["result"]:
        date = epoch_to_datetime(contest["startTimeSeconds"])
        if yesterday <= date and date < datetime.datetime.today():
            newcontests.append(str(contest["name"]))

    # コンテストごとに処理
    for contest in newcontests:
        rankList = []
        diffList = []

        # ユーザーの成績を取得
        for user in CFID:
            reslistJsonRes = urllib.request.urlopen("https://codeforces.com/api/user.rating?handle=" + str(user))
            reslistJsonData = json.loads(reslistJsonRes.read().decode("utf-8"))
            print("CF-result: Downloaded " + str(user) + "'s reslistData")
            for row in reslistJsonData["result"]:
                if str(contest) == str(row["contestName"]):
                    rankList.append({ "user" : str(user), "rank" : int(row["rank"]) })
                    diffList.append({ "user" : str(user), "diff" : (int(row["newRating"]) - int(row["oldRating"])) })
                    break
        print("CF-result: Checked " + str(contest) + " result")

        # ランキングを作成
        if len(rankList) > 0:
            rankList.sort(key = lambda x: x["rank"])
            tweetText = str(contest) + " 順位表" + makeRanking("rank", rankList, "位")
            api.update_with_media(filename = "CF/data/result/rankRankingImg_fixed.jpg", status = tweetText + "\n" + timeStamp)
            print("CF-result: Tweeted " + str(contest) + " rankRanking")
        if len(diffList) > 0:
            diffList.sort(key = lambda x: x["diff"], reverse = True)
            tweetText = str(contest) + " レート変動値" + makeRanking("diff", diffList, "")
            api.update_with_media(filename = "CF/data/result/diffRankingImg_fixed.jpg", status = tweetText + "\n" + timeStamp)
            print("CF-result: Tweeted " + str(contest) + " diffRanking")

if __name__ == '__main__':
    print("CF-result: Running as debug...")
    result()
    print("CF-result: Debug finished")
