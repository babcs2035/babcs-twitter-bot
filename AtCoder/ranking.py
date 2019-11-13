# import
import os
import tweepy
import datetime
import time
import dropbox
import requests
import pickle
import json
from PIL import Image, ImageDraw, ImageFont

# グローバル変数
AtCoderIDs = []
acCount = {}
acPoint = {}
ratings = {}

# 定数
acCountReachNum = 50
acPointReachNum = 5000

# Dropbox からダウンロード
def downloadFromDropbox(type):
    
    # グローバル変数
    global AtCoderIDs
    global acCount
    global acPoint
    global ratings

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # AtCoderIDs をダウンロード
    dbx.files_download_to_file("cper_bot/AtCoder/AtCoderIDs.txt", "/cper_bot/AtCoder/AtCoderIDs.txt")
    with open("cper_bot/AtCoder/AtCoderIDs.txt", "rb") as f:
        AtCoderIDs = pickle.load(f)
    print("cper_bot-AtCoder-detection: Downloaded AtCoderIDs (size : ", str(len(AtCoderIDs)), ")")
    
    dirType = ""
    if type == 0 or type == 1:
        dirType += "daily"
    if type == 2:
        dirType += "weekly"
    if type == 3:
        dirType += "monthly"

    # acCount をダウンロード
    dbx.files_download_to_file("cper_bot/AtCoder/" + dirType + "_acCount.txt", "/cper_bot/AtCoder/" + dirType + "_acCount.txt")
    with open("cper_bot/AtCoder/" + dirType + "_acCount.txt", "rb") as f:
        acCount = pickle.load(f)
    print("cper_bot-AtCoder-ranking: Downloaded " + dirType + " acCount (size : ", str(len(acCount)), ")")
    
    # acPoint をダウンロード
    dbx.files_download_to_file("cper_bot/AtCoder/" + dirType + "_acPoint.txt", "/cper_bot/AtCoder/" + dirType + "_acPoint.txt")
    with open("cper_bot/AtCoder/" + dirType + "_acPoint.txt", "rb") as f:
        acPoint = pickle.load(f)
    print("cper_bot-AtCoder-ranking: Downloaded " + dirType + " acPoint (size : ", str(len(acPoint)), ")")

    # ratings をダウンロード
    dbx.files_download_to_file("cper_bot/AtCoder/ratings.txt", "/cper_bot/AtCoder/ratings.txt")
    with open("cper_bot/AtCoder/ratings.txt", "rb") as f:
        ratings = pickle.load(f)
    print("cper_bot-AtCoder-ranking: Downloaded ratings (size : ", str(len(ratings)), ")")

# Dropbox にアップロード
def uploadToDropbox(type):
    
    # グローバル変数
    global acCount
    global acPoint
    
    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    dirType = ""
    if type == 0:
        dirType = "daily"
    if type == 1:
        dirType = "mid daily"
    if type == 2:
        dirType = "weekly"
    if type == 3:
        dirType = "monthly"
    
    if type != 1:
        # acCount をアップロード
        with open("cper_bot/AtCoder/" + dirType + "_acCount.txt", "wb") as f:
            pickle.dump(acCount, f)
        with open("cper_bot/AtCoder/" + dirType + "_acCount.txt", "rb") as f:
            dbx.files_delete("/cper_bot/AtCoder/" + dirType + "_acCount.txt")
            dbx.files_upload(f.read(), "/cper_bot/AtCoder/" + dirType + "_acCount.txt")
        print("cper_bot-AtCoder-ranking: Uploaded " + dirType + " acCount (size : ", str(len(acCount)), ")")

        # acPoint をアップロード
        with open("cper_bot/AtCoder/" + dirType + "_acPoint.txt", "wb") as f:
            pickle.dump(acPoint, f)
        with open("cper_bot/AtCoder/" + dirType + "_acPoint.txt", "rb") as f:
            dbx.files_delete("/cper_bot/AtCoder/" + dirType + "_acPoint.txt")
            dbx.files_upload(f.read(), "/cper_bot/AtCoder/" + dirType + "_acPoint.txt")
        print("cper_bot-AtCoder-ranking: Uploaded " + dirType + " acPoint (size : ", str(len(acPoint)), ")")

def makeRanking(type1, type2, listData, unit):
    
    global AtCoderIDa
    global ratings
    
    colors = [[0, 0, 0], [128, 128, 128], [128, 64, 0], [0, 128, 0], [0, 192, 192], [0, 0, 255], [192, 192, 0], [255, 128, 0], [255, 0, 0]]
    rows = 30

    flag = int(listData[0][str(type2)]) > int(listData[len(listData) - 1][str(type2)])
    rankNum = 1
    countNum = 1
    countIndex = 0
    rankingFont = ImageFont.truetype("cper_bot/AtCoder/data/fontR.ttc", 32)
    rankingFontS = ImageFont.truetype("cper_bot/AtCoder/data/fontB.ttc", 32)
    rankingFirstImg = Image.open("cper_bot/AtCoder/data/" + str(type2) + "RankingImg (first).jpg")
    resImg = Image.new("RGB", (850 * int((len(listData) + rows - 1) / rows), 65 + 63 * min(len(listData), rows)))
    awardsList = []
    for idx in range(len(listData)):
        if idx % rows == 0:
            resImg.paste(rankingFirstImg, (850 * int(idx / rows), 0))
        rankingImg = Image.open("cper_bot/AtCoder/data/rankingImg (cell).jpg")
        rankingDraw = ImageDraw.Draw(rankingImg)
        if idx > 0:
            if flag and int(listData[idx - 1][str(type2)]) > int(listData[idx][str(type2)]):
                rankNum = rankNum + countNum
                countNum = 1
                countIndex += 1
            elif (not flag) and int(listData[idx - 1][str(type2)]) < int(listData[idx][str(type2)]):
                rankNum = rankNum + countNum
                countNum = 1
                countIndex += 1
            else:
                countNum = countNum + 1

        colorIndex = 0
        for border in range(7, 0, -1):
            if str(listData[idx]["atcoderID"]) in ratings:
                if ratings[str(listData[idx]["atcoderID"])] >= border * 400:
                    colorIndex = border + 1
                    break
        if rankNum <= 8:
            rankingDraw.text((10, 7), str(rankNum), fill = (0, 0, 0), font = rankingFontS)
            rankingDraw.text((120, 7), listData[idx]["atcoderID"] + " (@" + listData[idx]["twitterID"] + ")", fill = (colors[colorIndex][0], colors[colorIndex][1], colors[colorIndex][2]), font = rankingFontS)
            rankingDraw.text((672, 7), str(listData[idx][str(type2)]), fill = (0, 0, 0), font = rankingFontS)
            awardsList.append("@" + listData[idx]["twitterID"])
        else:
            rankingDraw.text((10, 7), str(rankNum), fill = (0, 0, 0), font = rankingFont)
            rankingDraw.text((120, 7), listData[idx]["atcoderID"] + " (@" + listData[idx]["twitterID"] + ")", fill = (colors[colorIndex][0], colors[colorIndex][1], colors[colorIndex][2]), font = rankingFont)
            rankingDraw.text((672, 7), str(listData[idx][str(type2)]), fill = (0, 0, 0), font = rankingFont)
        resImg.paste(rankingImg, (850 * int(idx / rows), 65 + 63 * (idx % rows)))

    resImg.save("cper_bot/AtCoder/" + str(type1) + "RankingImg_fixed.jpg")
    tweetText = " ランキング TOP " + str(rankNum) + "\n入賞の " + " , ".join(awardsList) + " さん おめでとうございます！\n"
    return tweetText

# ランキング生成 (type 0:Daily, 1:Mid Daily, 2:Weekly, 3:Monthly)
def ranking(type):
    
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

    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    # データをダウンロード
    downloadFromDropbox(type)
    
    # ランキング種別を設定
    dirType = ""
    if type == 0:
        dirType = "daily"
    if type == 1:
        dirType = "mid daily"
    if type == 2:
        dirType = "weekly"
    if type == 3:
        dirType = "monthly"

    # AC 数を取得
    session = requests.Session()
    request = session.get(url = "https://kenkoooo.com/atcoder/resources/ac.json")
    acCountData = json.loads(request.text)
    request = session.get(url = "https://kenkoooo.com/atcoder/resources/sums.json")
    acPointData = json.loads(request.text)
    nowACCount = {}
    nowACPoint = {}
    for user in acCountData:
        for atcoderID, twitterID in AtCoderIDs:
            if user["user_id"] == atcoderID:
                nowACCount[str(user["user_id"])] = int(user["problem_count"])
    for user in acPointData:
        for atcoderID, twitterID in AtCoderIDs:
            if user["user_id"] == atcoderID:
                nowACPoint[str(user["user_id"])] = int(user["point_sum"])
    newACCount = []
    newACPoint = []
    newACPer = []
    for atcoderID, twitterID in AtCoderIDs:
        if atcoderID in acCount and atcoderID in nowACCount:
            if nowACCount[atcoderID] - acCount[atcoderID] > 0:
                newACCount.append(({"atcoderID" : atcoderID, "twitterID" : twitterID, "count" : nowACCount[atcoderID] - acCount[atcoderID]}))
        if atcoderID in acPoint and atcoderID in nowACPoint:
            if nowACPoint[atcoderID] - acPoint[atcoderID] > 0 and nowACCount[atcoderID] - acCount[atcoderID] > 0:
                newACPoint.append(({"atcoderID" : atcoderID, "twitterID" : twitterID, "point" : nowACPoint[atcoderID] - acPoint[atcoderID]}))
                newACPer.append(({"atcoderID" : atcoderID, "twitterID" : twitterID, "per": float(nowACPoint[atcoderID] - acPoint[atcoderID]) / float(nowACCount[atcoderID] - acCount[atcoderID])}))
    newACCount.sort(key = lambda x: x["count"], reverse = True)
    newACPoint.sort(key = lambda x: x["point"], reverse = True)
    newACPer.sort(key = lambda x: x["per"], reverse = True)

    # ランキングをツイート
    tweetTextType = ""
    if type == 0:
        tweetTextType = "Daily"
    if type == 1:
        tweetTextType = "Mid Daily"
    if type == 2:
        tweetTextType = "Weekly"
    if type == 3:
        tweetTextType = "Monthly"

    # Unique AC 数ランキングをツイート
    countTweetText = "AtCoder Unique AC 数 " + tweetTextType
    api.update_with_media(filename = "cper_bot/AtCoder/" + dirType + "_countRankingImg_fixed.jpg", status = countTweetText + makeRanking(dirType + "_count", "count", newACCount, "Unique AC") + "\n" + timeStamp)
    print("cper_bot-AtCoder-ranking: Tweeted " + dirType + " countRanking")

    # Point Sum ランキングをツイート
    pointTweetText = "AtCoder Point Sum " + tweetTextType
    api.update_with_media(filename = "cper_bot/AtCoder/" + dirType + "_pointRankingImg_fixed.jpg", status = pointTweetText + makeRanking(dirType + "_point", "point", newACPoint, "Point") + "\n" + timeStamp)
    print("cper_bot-AtCoder-ranking: Tweeted " + dirType + " pointRanking")

    # Point Per Count ランキングをツイート
    perTweetText = "AtCoder Point / Count " + tweetTextType
    api.update_with_media(filename = "cper_bot/AtCoder/" + dirType + "_perRankingImg_fixed.jpg", status = perTweetText + makeRanking(dirType + "_per", "per", newACPer, "P./C.") + "\n" + timeStamp)
    print("cper_bot-AtCoder-ranking: Tweeted " + dirType + " perRanking")

    # データをアップロード
    oldACCount = acCount
    oldACPoint = acPoint
    acCount = nowACCount
    acPoint = nowACPoint
    uploadToDropbox(type)

    # AC 数・Rated Point Sum の通知
    if type == 0:
        for atcoderID, twitterID in AtCoderIDs:
            userURL = "https://kenkoooo.com/atcoder/#/user/" + atcoderID
            if atcoderID in oldACCount and atcoderID in nowACCount:
                if nowACCount[atcoderID] - oldACCount[atcoderID] > 0:
                    if type == 0 and int(nowACCount[atcoderID] / acCountReachNum) > int(oldACCount[atcoderID] / acCountReachNum):
                        try:
                            api.update_status(atcoderID + " ( @" + twitterID + " ) さんの AtCoder での AC 数が " + str(oldACCount[atcoderID]) + " -> " + str(nowACCount[atcoderID]) + " となり，" + str(int(nowACCount[atcoderID] / acCountReachNum) * acCountReachNum) + " を突破しました！\n" + userURL + "\n" + timeStamp)
                            print("cper_bot-AtCoder-ranking: Tweeted " + atcoderID + " ( @" + twitterID + " )'s AC Count Reach (" + str(oldACCount[atcoderID]) + " -> " + str(nowACCount[atcoderID]) + ")")
                        except:
                            print("cper_bot-AtCoder-ranking: Tweet Error")
                        time.sleep(5)
            if atcoderID in oldACPoint and atcoderID in nowACPoint:
                if nowACPoint[atcoderID] - oldACPoint[atcoderID] > 0 and nowACCount[atcoderID] - oldACCount[atcoderID] > 0:
                    if type == 0 and int(nowACPoint[atcoderID] / acPointReachNum) > int(oldACPoint[atcoderID] / acPointReachNum):
                        try:
                            api.update_status(atcoderID + " ( @" + twitterID + " ) さんの AtCoder での Rated Point Sum 数が " + str(oldACPoint[atcoderID]) + " -> " + str(nowACPoint[atcoderID]) + " となり，" + str(int(nowACPoint[atcoderID] / acPointReachNum) * acPointReachNum) + " を突破しました！\n" + userURL + "\n" + timeStamp)
                            print("cper_bot-AtCoder-ranking: Tweeted " + atcoderID + " ( @" + twitterID + " )'s Rated Point Sum Reach (" + str(oldACPoint[atcoderID]) + " -> " + str(nowACPoint[atcoderID]) + ")")
                        except:
                            print("cper_bot-AtCoder-ranking: Tweet Error")
                        time.sleep(5)

if __name__ == '__main__':
    print("cper_bot-AtCoder-ranking: Running as debug...")
    ranking(1)
    print("cper_bot-AtCoder-ranking: Debug finished")
