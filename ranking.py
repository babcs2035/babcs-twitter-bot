# import
import os
import tweepy
import datetime
import json
import dropbox
import urllib
from PIL import Image, ImageDraw, ImageFont

# グローバル変数
AtCoderID = []
TwitterID = []
acCount = []
acPoint = []

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global AtCoderID
    global TwitterID
    global acCount
    global acPoint

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # AtCoderID をダウンロード
    dbx.files_download_to_file("AtCoderID.txt", "/AtCoderID.txt")
    with open("AtCoderID.txt", "r") as f:
        AtCoderID.clear()
        for id in f:
            AtCoderID.append(id.rstrip("\n"))
    print("ranking: Downloaded AtCoderID (size : ", str(len(AtCoderID)), ")")
    
    # TwitterID をダウンロード
    dbx.files_download_to_file("TwitterID.txt", "/TwitterID.txt")
    with open("TwitterID.txt", "r") as f:
        TwitterID.clear()
        for id in f:
            TwitterID.append(id.rstrip("\n"))
    print("ranking: Downloaded TwitterID (size : ", str(len(TwitterID)), ")")
    
    # acCount をダウンロード
    dbx.files_download_to_file("acCount.txt", "/acCount.txt")
    with open("acCount.txt", "r") as f:
        acCount.clear()
        for acs in f:
            acCount.append(int(acs.rstrip("\n")))
    print("ranking: Downloaded acCount (size : ", str(len(acCount)), ")")

    # acPoint をダウンロード
    dbx.files_download_to_file("acPoint.txt", "/acPoint.txt")
    with open("acPoint.txt", "r") as f:
        acPoint.clear()
        for acs in f:
            acPoint.append(int(acs.rstrip("\n")))
    print("ranking: Downloaded acPoint (size : ", str(len(acPoint)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global acCount
    global acPoint
    
    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # acCount をアップロード
    with open("acCount.txt", "w") as f:
        for acs in acCount:
            f.write(str(acs) + "\n")
    with open("acCount.txt", "rb") as f:
        dbx.files_delete("/acCount.txt")
        dbx.files_upload(f.read(), "/acCount.txt")
    print("ranking: Uploaded acCount (size : ", str(len(acCount)), ")")

    # acPoint をアップロード
    with open("acPoint.txt", "w") as f:
        for acs in acPoint:
            f.write(str(acs) + "\n")
    with open("acPoint.txt", "rb") as f:
        dbx.files_delete("/acPoint.txt")
        dbx.files_upload(f.read(), "/acPoint.txt")
    print("ranking: Uploaded acPoint (size : ", str(len(acPoint)), ")")
    
    # countRankingImg_fixed をアップロード
    with open("data/countRankingImg_fixed.jpg", "rb") as f:
        dbx.files_upload(f.read(), "/_backup/countRankingImg_fixed/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".jpg")
        print("ranking: Uploaded countRankingImg_fixed")

    # pointRankingImg_fixed をアップロード
    with open("data/pointRankingImg_fixed.jpg", "rb") as f:
        dbx.files_upload(f.read(), "/_backup/pointRankingImg_fixed/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".jpg")
        print("ranking: Uploaded pointRankingImg_fixed")

# list 内の要素の添え字を返す（無い場合は -1）
def myIndex(x, l):
    if x in l:
        return l.index(x)
    else:
        return -1

def ranking():
    
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
    
    # データをダウンロード
    downloadFromDropbox()

    # AC 数を取得
    acCountJson = urllib.request.urlopen("https://kenkoooo.com/atcoder/atcoder-api/info/ac")
    acPointJson = urllib.request.urlopen("https://kenkoooo.com/atcoder/atcoder-api/info/sums")
    acCountData = json.loads(acCountJson.read().decode("utf-8"))
    acPointData = json.loads(acPointJson.read().decode("utf-8"))
    resCount = []
    resPoint = []
    for user in acCountData:
        if user["user_id"] in AtCoderID:
            resCount.append(({"user_id" : str(user["user_id"]), "count" : int(user["problem_count"])}))
    for user in acPointData:
        if user["user_id"] in AtCoderID:
            resPoint.append(({"user_id" : str(user["user_id"]), "point" : int(user["point_sum"])}))
    nowACCount = []
    nowACPoint = []
    for id in AtCoderID:
        for user in resCount:
            if id == user["user_id"]:
                nowACCount.append(user["count"])
                break
    for id in AtCoderID:
        for user in resPoint:
            if id == user["user_id"]:
                nowACPoint.append(user["point"])
                break
    newACCount = []
    newACPoint = []
    for idx in range(len(acCount)):
        if nowACCount[idx] - acCount[idx] > 0:
            newACCount.append(({"user_id" : AtCoderID[idx], "count" : nowACCount[idx] - acCount[idx]}))
    for idx in range(len(acPoint)):
        if nowACPoint[idx] - acPoint[idx] > 0:
            newACPoint.append(({"user_id" : AtCoderID[idx], "point" : nowACPoint[idx] - acPoint[idx]}))
    newACCount.sort(key = lambda x: x["count"], reverse = True)
    newACPoint.sort(key = lambda x: x["point"], reverse = True)

    # Unique AC 数ランキングを作成
    countRankNum = 1
    countNum = 1
    rankingFont = ImageFont.truetype("data/YuGothM.ttc", 32)
    countRankingFirstImg = Image.open("data/countRankingImg (first).jpg")
    countResImg = Image.new("RGB", (738, 65 + 63 * len(newACCount)))
    countResImg.paste(countRankingFirstImg, (0, 0))
    for idx in range(len(newACCount)):
        countRankingImg = Image.open("data/rankingImg (cell).jpg")
        countRankingDraw = ImageDraw.Draw(countRankingImg)
        if idx > 0:
            if int(newACCount[idx - 1]["count"]) > int(newACCount[idx]["count"]):
                countRankNum = countRankNum + countNum
                countNum = 1
            else:
                countNum = countNum + 1
        countRankingDraw.text((10, 19), str(countRankNum), fill = (0, 0, 0), font = rankingFont)
        countRankingDraw.text((120, 19), newACCount[idx]["user_id"], fill = (0, 0, 0), font = rankingFont)
        countRankingDraw.text((560, 19), str(newACCount[idx]["count"]), fill = (0, 0, 0), font = rankingFont)
        countResImg.paste(countRankingImg, (0, 65 + 63 * idx))
    countResImg.save("data/countRankingImg_fixed.jpg")

    # Point Sum ランキングを作成
    pointRankNum = 1
    pointNum = 1
    pointRankingFirstImg = Image.open("data/pointRankingImg (first).jpg")
    pointResImg = Image.new("RGB", (738, 65 + 63 * len(newACPoint)))
    pointResImg.paste(pointRankingFirstImg, (0, 0))
    for idx in range(len(newACPoint)):
        pointRankingImg = Image.open("data/rankingImg (cell).jpg")
        pointRankingDraw = ImageDraw.Draw(pointRankingImg)
        if idx > 0:
            if int(newACPoint[idx - 1]["point"]) > int(newACPoint[idx]["point"]):
                pointRankNum = pointRankNum + pointNum
                pointNum = 1
            else:
                pointNum = pointNum + 1
        pointRankingDraw.text((10, 19), str(pointRankNum), fill = (0, 0, 0), font = rankingFont)
        pointRankingDraw.text((120, 19), newACPoint[idx]["user_id"], fill = (0, 0, 0), font = rankingFont)
        pointRankingDraw.text((560, 19), str(newACPoint[idx]["point"]), fill = (0, 0, 0), font = rankingFont)
        pointResImg.paste(pointRankingImg, (0, 65 + 63 * idx))
    pointResImg.save("data/pointRankingImg_fixed.jpg")

    # データをアップロード
    acCount = nowACCount
    acPoint = nowACPoint
    uploadToDropbox()

    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    # ランキングをツイート
    countTweetText = "Unique AC 数ランキング TOP " + str(countRankNum) + " !!\n"
    countRankNum = 1
    countNum = 1
    for idx in range(len(newACCount)):
        if idx > 0:
            if int(newACCount[idx - 1]["count"]) > int(newACCount[idx]["count"]):
                countRankNum = countRankNum + countNum
                countNum = 1
            else:
                countNum = countNum + 1
        if len(countTweetText) + len(timeStamp) + len(str(countRankNum) + " 位 " + newACCount[idx]["user_id"] + " ( @" + str(TwitterID[myIndex(newACCount[idx]["user_id"],AtCoderID)]) + " ) " + str(newACCount[idx]["count"]) + " Unique AC\n") <= 140:
            countTweetText += str(countRankNum) + " 位 " + newACCount[idx]["user_id"] + " ( @" + str(TwitterID[myIndex(newACCount[idx]["user_id"],AtCoderID)]) + " ) " + str(newACCount[idx]["count"]) + " Unique AC\n"
        else:
            break
    api.update_with_media(filename = "data/countRankingImg_fixed.jpg", status = countTweetText + "\n" + timeStamp)
    pointTweetText = "Point Sum ランキング TOP " + str(pointRankNum) + " !!\n"
    pointRankNum = 1
    pointNum = 1
    for idx in range(len(newACPoint)):
        if idx > 0:
            if int(newACPoint[idx - 1]["point"]) > int(newACPoint[idx]["point"]):
                pointRankNum = pointRankNum + pointNum
                pointNum = 1
            else:
                pointNum = pointNum + 1
        if len(pointTweetText) + len(timeStamp) + len(str(pointRankNum) + " 位 " + newACPoint[idx]["user_id"] + " ( @" + str(TwitterID[myIndex(newACPoint[idx]["user_id"],AtCoderID)]) + " ) " + str(newACPoint[idx]["point"]) + " Point\n") <= 140:
            pointTweetText += str(pointRankNum) + " 位 " + newACPoint[idx]["user_id"] + " ( @" + str(TwitterID[myIndex(newACPoint[idx]["user_id"],AtCoderID)]) + " ) " + str(newACPoint[idx]["point"]) + " Point\n"
        else:
            break
    api.update_with_media(filename = "data/pointRankingImg_fixed.jpg", status = pointTweetText + "\n" + timeStamp)
