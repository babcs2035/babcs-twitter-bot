# import
import os
import tweepy
import datetime
import json
import dropbox
import urllib
from PIL import Image, ImageDraw, ImageFont
import pickle

# グローバル変数
AtCoderID = []
TwitterID = []
acCount = {}
acPoint = {}

# Dropbox からダウンロード
def downloadFromDropbox(type):
    
    # グローバル変数
    global AtCoderID
    global TwitterID
    global acCount
    global acPoint

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # AtCoderID をダウンロード
    dbx.files_download_to_file("AtCoder/AtCoderID.txt", "/AtCoder/AtCoderID.txt")
    with open("AtCoder/AtCoderID.txt", "r") as f:
        AtCoderID.clear()
        for id in f:
            AtCoderID.append(id.rstrip("\n"))
    print("AtCoder-ranking: Downloaded AtCoderID (size : ", str(len(AtCoderID)), ")")
    
    # TwitterID をダウンロード
    dbx.files_download_to_file("AtCoder/TwitterID.txt", "/AtCoder/TwitterID.txt")
    with open("AtCoder/TwitterID.txt", "r") as f:
        TwitterID.clear()
        for id in f:
            TwitterID.append(id.rstrip("\n"))
    print("AtCoder-ranking: Downloaded TwitterID (size : ", str(len(TwitterID)), ")")
    
    dirType = ""
    if type == 0 or type == 1:
        dirType += "daily"
    if type == 2:
        dirType += "weekly"
    if type == 3:
        dirType += "monthly"

    # acCount をダウンロード
    dbx.files_download_to_file("AtCoder/" + dirType + "_acCount.txt", "/AtCoder/" + dirType + "_acCount.txt")
    with open("AtCoder/" + dirType + "_acCount.txt", "rb") as f:
        acCount = pickle.load(f)
    print("AtCoder-ranking: Downloaded " + dirType + " acCount (size : ", str(len(acCount)), ")")
    
    # acPoint をダウンロード
    dbx.files_download_to_file("AtCoder/" + dirType + "_acPoint.txt", "/AtCoder/" + dirType + "_acPoint.txt")
    with open("AtCoder/" + dirType + "_acPoint.txt", "rb") as f:
        acPoint = pickle.load(f)
    print("AtCoder-ranking: Downloaded " + dirType + " acPoint (size : ", str(len(acPoint)), ")")

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
        with open("AtCoder/" + dirType + "_acCount.txt", "wb") as f:
            pickle.dump(acCount, f)
        with open("AtCoder/" + dirType + "_acCount.txt", "rb") as f:
            dbx.files_delete("/AtCoder/" + dirType + "_acCount.txt")
            dbx.files_upload(f.read(), "/AtCoder/" + dirType + "_acCount.txt")
        print("AtCoder-ranking: Uploaded " + dirType + " acCount (size : ", str(len(acCount)), ")")

        # acPoint をアップロード
        with open("AtCoder/" + dirType + "_acPoint.txt", "wb") as f:
            pickle.dump(acPoint, f)
        with open("AtCoder/" + dirType + "_acPoint.txt", "rb") as f:
            dbx.files_delete("/AtCoder/" + dirType + "_acPoint.txt")
            dbx.files_upload(f.read(), "/AtCoder/" + dirType + "_acPoint.txt")
        print("AtCoder-ranking: Uploaded " + dirType + " acPoint (size : ", str(len(acPoint)), ")")

    # countRankingImg_fixed をアップロード
    with open("AtCoder/" + dirType + "_countRankingImg_fixed.jpg", "rb") as f:
        dbx.files_upload(f.read(), "/_backup/AtCoder/countRankingImg_fixed/" + dirType + "_" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".jpg")
        print("AtCoder-ranking: Uploaded " + dirType + " countRankingImg_fixed")

    # pointRankingImg_fixed をアップロード
    with open("AtCoder/" + dirType + "_pointRankingImg_fixed.jpg", "rb") as f:
        dbx.files_upload(f.read(), "/_backup/AtCoder/pointRankingImg_fixed/" + dirType + "_" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".jpg")
        print("AtCoder-ranking: Uploaded " + dirType + " pointRankingImg_fixed")

    # perRankingImg_fixed をアップロード
    with open("AtCoder/" + dirType + "_perRankingImg_fixed.jpg", "rb") as f:
        dbx.files_upload(f.read(), "/_backup/AtCoder/perRankingImg_fixed/" + dirType + "_" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".jpg")
        print("AtCoder-ranking: Uploaded " + dirType + " perRankingImg_fixed")

# list 内の要素の添え字を返す（無い場合は -1）
def myIndex(x, l):
    if x in l:
        return l.index(x)
    else:
        return -1

def makeRanking(type1, type2, listData, unit):
    
    global AtCoderID
    global TwitterID

    flag = int(listData[0][str(type2)]) > int(listData[len(listData) - 1][str(type2)])
    rankNum = 1
    countNum = 1
    countIndex = 0
    rankingFont = ImageFont.truetype("AtCoder/data/YuGothM.ttc", 32)
    rankingFirstImg = Image.open("AtCoder/data/" + str(type2) + "RankingImg (first).jpg")
    resImg = Image.new("RGB", (850 * int((len(listData) + 19) / 20), 65 + 63 * min(len(listData), 20)))
    tweetText = ""
    for idx in range(len(listData)):
        if idx % 20 == 0:
            resImg.paste(rankingFirstImg, (850 * int(idx / 20), 0))
        rankingImg = Image.open("AtCoder/data/rankingImg (cell).jpg")
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
        
        if rankNum + countNum - 1 <= 3:
            tweetText += str(rankNum) + " 位 " + listData[idx]["user"] + " ( @" + str(TwitterID[myIndex(listData[idx]["user"], AtCoderID)]) + " ) " + str(listData[idx][str(type2)]) + " " + str(unit) + "\n"
        rankingDraw.text((10, 19), str(rankNum), fill = (0, 0, 0), font = rankingFont)
        rankingDraw.text((120, 19), listData[idx]["user"] + " (@" + str(TwitterID[myIndex(str(listData[idx]["user"]), AtCoderID)]) + ")", fill = (0, 0, 0), font = rankingFont)
        rankingDraw.text((672, 19), str(listData[idx][str(type2)]), fill = (0, 0, 0), font = rankingFont)
        resImg.paste(rankingImg, (850 * int(idx / 20), 65 + 63 * (idx % 20)))

        # ランキングポイント処理
        point = 1
        if countIndex == 0:
            point = 5
        elif countIndex == 1:
            point = 4
        elif countIndex == 2:
            point = 3

    resImg.save("AtCoder/" + str(type1) + "RankingImg_fixed.jpg")
    tweetText = " ランキング TOP " + str(rankNum) + "\n" + tweetText
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
    acCountJson = urllib.request.urlopen("https://kenkoooo.com/atcoder/resources/ac.json")
    acPointJson = urllib.request.urlopen("https://kenkoooo.com/atcoder/resources/sums.json")
    acCountData = json.loads(acCountJson.read().decode("utf-8"))
    acPointData = json.loads(acPointJson.read().decode("utf-8"))
    nowACCount = {}
    nowACPoint = {}
    for user in acCountData:
        if user["user_id"] in AtCoderID:
            nowACCount[str(user["user_id"])] = int(user["problem_count"])
    for user in acPointData:
        if user["user_id"] in AtCoderID:
            nowACPoint[str(user["user_id"])] = int(user["point_sum"])
    newACCount = []
    newACPoint = []
    newACPer = []
    for user in AtCoderID:
        if user in acCount and user in nowACCount:
            if nowACCount[user] - acCount[user] > 0:
                newACCount.append(({"user" : user, "count" : nowACCount[user] - acCount[user]}))
        if user in acPoint and user in nowACPoint:
            if nowACPoint[user] - acPoint[user] > 0 and nowACCount[user] - acCount[user] > 0:
                newACPoint.append(({"user" : user, "point" : nowACPoint[user] - acPoint[user]}))
                newACPer.append(({"user" : user, "per": float(nowACPoint[user] - acPoint[user]) / float(nowACCount[user] - acCount[user])}))
    newACCount.sort(key = lambda x: x["count"], reverse = True)
    newACPoint.sort(key = lambda x: x["point"], reverse = True)
    newACPer.sort(key = lambda x: x["per"], reverse = True)

    ## ランキングをツイート
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
    api.update_with_media(filename = "AtCoder/" + dirType + "_countRankingImg_fixed.jpg", status = countTweetText + makeRanking(dirType + "_count", "count", newACCount, "Unique AC") + "\n" + timeStamp)
    print("AtCoder-ranking: Tweeted " + dirType + " countRanking")

    # Point Sum ランキングをツイート
    pointTweetText = "AtCoder Point Sum " + tweetTextType
    api.update_with_media(filename = "AtCoder/" + dirType + "_pointRankingImg_fixed.jpg", status = pointTweetText + makeRanking(dirType + "_point", "point", newACPoint, "Point") + "\n" + timeStamp)
    print("AtCoder-ranking: Tweeted " + dirType + " pointRanking")

    # Point Per Count ランキングをツイート
    perTweetText = "AtCoder Point / Count " + tweetTextType
    api.update_with_media(filename = "AtCoder/" + dirType + "_perRankingImg_fixed.jpg", status = perTweetText + makeRanking(dirType + "_per", "per", newACPer, "P./C.") + "\n" + timeStamp)
    print("AtCoder-ranking: Tweeted " + dirType + " perRanking")

    # データをアップロード
    acCount = nowACCount
    acPoint = nowACPoint
    uploadToDropbox(type)

if __name__ == '__main__':
    print("AtCoder-ranking: Running as debug...")
    ranking(1)
    print("AtCoder-ranking: Debug finished")
