# import
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
import time
import json
import requests
import urllib
import pickle
import dropbox
import datetime
import tweepy
import os


# グローバル変数
CFIDs = set()

# Dropbox からダウンロード


def downloadFromDropbox():

    # グローバル変数
    global CFIDs

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # CFIDs をダウンロード
    dbx.files_download_to_file("CF/CFIDs.txt", "/CF/CFIDs.txt")
    with open("CF/CFIDs.txt", "rb") as f:
        CFIDs = pickle.load(f)
    print(
        "cper_bot-CF-result: Downloaded CFIDs (size : ", str(len(CFIDs)), ")")


def epoch_to_datetime(epoch):
    return datetime.datetime(*time.localtime(epoch)[:6])


def makeRanking(type, listData):

    global CFIDs

    flag = int(listData[0][str(type)]) > int(
        listData[len(listData) - 1][str(type)])
    rankNum = 1
    countNum = 1
    rankingFont = ImageFont.truetype("CF/data/fontR.ttc", 32)
    rankingFontS = ImageFont.truetype("CF/data/fontB.ttc", 32)
    rankingFirstImg = Image.open(
        "CF/data/result/" + str(type) + "RankingImg (first).jpg")
    resImg = Image.new(
        "RGB", (738 * int((len(listData) + 19) / 20), 65 + 63 * min(len(listData), 20)))
    awardsList = []
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

        if rankNum <= 5:
            awardsList.append("@" + listData[idx]["twitterID"])
            rankingDraw.text((10, 7), str(rankNum),
                             fill=(0, 0, 0), font=rankingFontS)
            rankingDraw.text((120, 7), listData[idx]["cfID"], fill=(
                0, 0, 0), font=rankingFontS)
            rankingDraw.text((560, 7), str(listData[idx][str(type)]), fill=(
                0, 0, 0), font=rankingFontS)
        else:
            rankingDraw.text((10, 7), str(rankNum),
                             fill=(0, 0, 0), font=rankingFont)
            rankingDraw.text((120, 7), listData[idx]["cfID"], fill=(
                0, 0, 0), font=rankingFont)
            rankingDraw.text((560, 7), str(
                listData[idx][str(type)]), fill=(0, 0, 0), font=rankingFont)
        resImg.paste(rankingImg, (738 * int(idx / 20), 65 + 63 * (idx % 20)))
    resImg.save("CF/data/result/" + str(type) + "RankingImg_fixed.jpg")
    tweetText = " ランキング TOP " + \
        str(rankNum) + "\n入賞の " + " , ".join(awardsList) + " さん おめでとうございます！\n"
    return tweetText


def result():

    # グローバル変数
    global CFIDs

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

    # コンテスト結果のランキング処理
    # 取得すべきコンテストを取得
    contestsJsonRes = urllib.request.urlopen(
        "https://codeforces.com/api/contest.list")
    contestsJsonData = json.loads(contestsJsonRes.read().decode("utf-8"))
    print("cper_bot-CF-result: Downloaded contestsJsonData")
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
        for (cfID, twitterID) in CFIDs:
            try:
                reslistJsonRes = urllib.request.urlopen(
                    "https://codeforces.com/api/user.rating?handle=" + str(cfID))
            except:
                print("cper_bot-CF-result: reslistJsonRes Error")
                continue
            reslistJsonData = json.loads(reslistJsonRes.read().decode("utf-8"))
            print("cper_bot-CF-result: Downloaded " +
                            str(cfID) + "'s reslistData")
            for row in reslistJsonData["result"]:
                if str(contest) == str(row["contestName"]):
                    rankList.append({"cfID": str(cfID), "twitterID": str(
                        twitterID), "rank": int(row["rank"])})
                    diffList.append({"cfID": str(cfID), "twitterID": str(
                        twitterID), "diff": (int(row["newRating"]) - int(row["oldRating"]))})
                    break
        print("cper_bot-CF-result: Checked " +
                        str(contest) + " result")

        # ランキングを作成
        if len(rankList) > 0:
            rankList.sort(key=lambda x: x["rank"])
            tweetText = str(contest) + " 順位表" + makeRanking("rank", rankList)
            api.update_status_with_media(
                filename="CF/data/result/rankRankingImg_fixed.jpg", status=tweetText + "\n" + timeStamp)
            print("cper_bot-CF-result: Tweeted " +
                            str(contest) + " rankRanking")
        if len(diffList) > 0:
            diffList.sort(key=lambda x: x["diff"], reverse=True)
            tweetText = str(contest) + " レート変動値" + \
                makeRanking("diff", diffList)
            api.update_status_with_media(
                filename="CF/data/result/diffRankingImg_fixed.jpg", status=tweetText + "\n" + timeStamp)
            print("cper_bot-CF-result: Tweeted " +
                            str(contest) + " diffRanking")


if __name__ == '__main__':
    print("cper_bot-CF-result: Running as debug...")
    result()
    print("cper_bot-CF-result: Debug finished")
