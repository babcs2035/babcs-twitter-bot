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
    dbx.files_download_to_file("AtCoder/AtCoderID.txt", "/AtCoder/AtCoderID.txt")
    with open("AtCoder/AtCoderID.txt", "r") as f:
        AtCoderID.clear()
        for id in f:
            AtCoderID.append(id.rstrip("\n"))
    print("ranking: Downloaded AtCoderID (size : ", str(len(AtCoderID)), ")")
    
    # TwitterID をダウンロード
    dbx.files_download_to_file("AtCoder/TwitterID.txt", "/AtCoder/TwitterID.txt")
    with open("AtCoder/TwitterID.txt", "r") as f:
        TwitterID.clear()
        for id in f:
            TwitterID.append(id.rstrip("\n"))
    print("ranking: Downloaded TwitterID (size : ", str(len(TwitterID)), ")")
    
    # acCount をダウンロード
    dbx.files_download_to_file("AtCoder/acCount.txt", "/AtCoder/acCount.txt")
    with open("AtCoder/acCount.txt", "rb") as f:
        acCount = pickle.load(f)
    print("ranking: Downloaded acCount (size : ", str(len(acCount)), ")")

    # acPoint をダウンロード
    dbx.files_download_to_file("AtCoder/acPoint.txt", "/AtCoder/acPoint.txt")
    with open("AtCoder/acPoint.txt", "rb") as f:
        acPoint = pickle.load(f)
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
    with open("AtCoder/acCount.txt", "wb") as f:
        pickle.dump(acCount, f)
    with open("AtCoder/acCount.txt", "rb") as f:
        dbx.files_delete("/AtCoder/acCount.txt")
        dbx.files_upload(f.read(), "/AtCoder/acCount.txt")
    print("ranking: Uploaded acCount (size : ", str(len(acCount)), ")")

    # acPoint をアップロード
    with open("AtCoder/acPoint.txt", "wb") as f:
        pickle.dump(acPoint, f)
    with open("AtCoder/acPoint.txt", "rb") as f:
        dbx.files_delete("/AtCoder/acPoint.txt")
        dbx.files_upload(f.read(), "/AtCoder/acPoint.txt")
    print("ranking: Uploaded acPoint (size : ", str(len(acPoint)), ")")
    
    # countRankingImg_fixed をアップロード
    with open("AtCoder/countRankingImg_fixed.jpg", "rb") as f:
        dbx.files_upload(f.read(), "/_backup/AtCoder/countRankingImg_fixed/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".jpg")
        print("ranking: Uploaded countRankingImg_fixed")

    # pointRankingImg_fixed をアップロード
    with open("AtCoder/pointRankingImg_fixed.jpg", "rb") as f:
        dbx.files_upload(f.read(), "/_backup/AtCoder/pointRankingImg_fixed/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".jpg")
        print("ranking: Uploaded pointRankingImg_fixed")

    # perRankingImg_fixed をアップロード
    with open("AtCoder/perRankingImg_fixed.jpg", "rb") as f:
        dbx.files_upload(f.read(), "/_backup/AtCoder/perRankingImg_fixed/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".jpg")
        print("ranking: Uploaded perRankingImg_fixed")

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
        if user in acCount:
            if nowACCount[user] - acCount[user] > 0:
                newACCount.append(({"user_id" : user, "count" : nowACCount[user] - acCount[user]}))
        if user in acPoint:
            if nowACPoint[user] - acPoint[user] > 0:
                newACPoint.append(({"user_id" : user, "point" : nowACPoint[user] - acPoint[user]}))
                newACPer.append(({"user_id" : user, "per": float(nowACPoint[user] - acPoint[user]) / float(nowACCount[user] - acCount[user])}))
    newACCount.sort(key = lambda x: x["count"], reverse = True)
    newACPoint.sort(key = lambda x: x["point"], reverse = True)
    newACPer.sort(key = lambda x: x["per"], reverse = True)

    # Unique AC 数ランキングを作成
    countRankNum = 1
    countNum = 1
    rankingFont = ImageFont.truetype("AtCoder/data/YuGothM.ttc", 32)
    countRankingFirstImg = Image.open("AtCoder/data/countRankingImg (first).jpg")
    countResImg = Image.new("RGB", (738, 65 + 63 * len(newACCount)))
    countResImg.paste(countRankingFirstImg, (0, 0))
    for idx in range(len(newACCount)):
        countRankingImg = Image.open("AtCoder/data/rankingImg (cell).jpg")
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
    countResImg.save("AtCoder/countRankingImg_fixed.jpg")

    # Point Sum ランキングを作成
    pointRankNum = 1
    pointNum = 1
    pointRankingFirstImg = Image.open("AtCoder/data/pointRankingImg (first).jpg")
    pointResImg = Image.new("RGB", (738, 65 + 63 * len(newACPoint)))
    pointResImg.paste(pointRankingFirstImg, (0, 0))
    for idx in range(len(newACPoint)):
        pointRankingImg = Image.open("AtCoder/data/rankingImg (cell).jpg")
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
    pointResImg.save("AtCoder/pointRankingImg_fixed.jpg")

    # Point Per Count ランキングを作成
    perRankNum = 1
    perNum = 1
    perRankingFirstImg = Image.open("AtCoder/data/perRankingImg (first).jpg")
    perResImg = Image.new("RGB", (738, 65 + 63 * len(newACPer)))
    perResImg.paste(perRankingFirstImg, (0, 0))
    for idx in range(len(newACPer)):
        perRankingImg = Image.open("AtCoder/data/rankingImg (cell).jpg")
        perRankingDraw = ImageDraw.Draw(perRankingImg)
        if idx > 0:
            if int(newACPer[idx - 1]["per"]) > int(newACPer[idx]["per"]):
                perRankNum = perRankNum + perNum
                perNum = 1
            else:
                perNum = perNum + 1
        perRankingDraw.text((10, 19), str(perRankNum), fill = (0, 0, 0), font = rankingFont)
        perRankingDraw.text((120, 19), newACPer[idx]["user_id"], fill = (0, 0, 0), font = rankingFont)
        perRankingDraw.text((560, 19), str(newACPer[idx]["per"]), fill = (0, 0, 0), font = rankingFont)
        perResImg.paste(perRankingImg, (0, 65 + 63 * idx))
    perResImg.save("AtCoder/perRankingImg_fixed.jpg")

    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    # ランキングをツイート
    countTweetText = "AtCoder Unique AC 数ランキング TOP " + str(countRankNum) + "\n"
    countRankNum = 1
    countNum = 1
    for idx in range(len(newACCount)):
        if idx > 0:
            if int(newACCount[idx - 1]["count"]) > int(newACCount[idx]["count"]):
                countRankNum = countRankNum + countNum
                countNum = 1
            else:
                countNum = countNum + 1
        if countRankNum + countNum - 1 <= 3:
            countTweetText += str(countRankNum) + " 位 " + newACCount[idx]["user_id"] + " ( @" + str(TwitterID[myIndex(newACCount[idx]["user_id"],AtCoderID)]) + " ) " + str(newACCount[idx]["count"]) + " Unique AC\n"
        else:
            break
    api.update_with_media(filename = "AtCoder/countRankingImg_fixed.jpg", status = countTweetText + "\n" + timeStamp)
    pointTweetText = "AtCoder Point Sum ランキング TOP " + str(pointRankNum) + "\n"
    pointRankNum = 1
    pointNum = 1
    for idx in range(len(newACPoint)):
        if idx > 0:
            if int(newACPoint[idx - 1]["point"]) > int(newACPoint[idx]["point"]):
                pointRankNum = pointRankNum + pointNum
                pointNum = 1
            else:
                pointNum = pointNum + 1
        if pointRankNum + pointNum - 1 <= 3:
            pointTweetText += str(pointRankNum) + " 位 " + newACPoint[idx]["user_id"] + " ( @" + str(TwitterID[myIndex(newACPoint[idx]["user_id"],AtCoderID)]) + " ) " + str(newACPoint[idx]["point"]) + " Point\n"
        else:
            break
    api.update_with_media(filename = "AtCoder/pointRankingImg_fixed.jpg", status = pointTweetText + "\n" + timeStamp)
    perTweetText = "AtCoder Point / Count ランキング TOP " + str(perRankNum) + "\n"
    perRankNum = 1
    perNum = 1
    for idx in range(len(newACPer)):
        if idx > 0:
            if int(newACPer[idx - 1]["per"]) > int(newACPer[idx]["per"]):
                perRankNum = perRankNum + perNum
                perNum = 1
            else:
                perNum = perNum + 1
        if perRankNum + perNum - 1 <= 3:
            perTweetText += str(perRankNum) + " 位 " + newACPer[idx]["user_id"] + " ( @" + str(TwitterID[myIndex(newACPer[idx]["user_id"],AtCoderID)]) + " ) " + str(newACPer[idx]["per"]) + " Point\n"
        else:
            break
    api.update_with_media(filename = "AtCoder/perRankingImg_fixed.jpg", status = perTweetText + "\n" + timeStamp)
    
    # データをアップロード
    acCount = nowACCount
    acPoint = nowACPoint
    uploadToDropbox()

if __name__ == '__main__':
    print("AtCoder-ranking: Running as debug...")
    ranking()
    print("AtCoder-ranking: Debug finished")
