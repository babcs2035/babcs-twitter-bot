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

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global AtCoderID
    global TwitterID
    global acCount

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

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global acCount
    
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

def ranking():
    
    # グローバル変数
    global acCount

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
    acCountData = json.loads(acCountJson.read().decode("utf-8"))
    resCount = []
    for user in acCountData:
        if user["user_id"] in AtCoderID:
            resCount.append(({"user_id" : str(user["user_id"]), "count" : int(user["problem_count"])}))
    nowACCount = []   
    for id in AtCoderID:
        for user in resCount:
            if id == user["user_id"]:
                nowACCount.append(user["count"])
                break
    newACCount = []
    for idx in range(len(acCount)):
        if nowACCount[idx] - acCount[idx] > 0:
            newACCount.append(({"user_id" : AtCoderID[idx], "count" : nowACCount[idx] - acCount[idx]}))
    newACCount.sort(key = lambda x: x["count"], reverse = True)

    # ランキングを作成
    rankNum = 1
    countNum = 1
    rankingFont = ImageFont.truetype("data/YuGothM.ttc", 32)
    rankingFirstImg = Image.open("data/rankingImg (first).jpg")
    resImg = Image.new("RGB", (738, 65 + 63 * len(newACCount)))
    resImg.paste(rankingFirstImg, (0, 0))
    for idx in range(len(newACCount)):
        rankingImg = Image.open("data/rankingImg (cell).jpg")
        rankingDraw = ImageDraw.Draw(rankingImg)
        if idx > 0:
            if int(newACCount[idx - 1]["count"]) > int(newACCount[idx]["count"]):
                rankNum = rankNum + countNum
                countNum = 1
            else:
                countNum = countNum + 1
        rankingDraw.text((10, 19), str(rankNum), fill = (0, 0, 0), font = rankingFont)
        rankingDraw.text((120, 19), newACCount[idx]["user_id"], fill = (0, 0, 0), font = rankingFont)
        rankingDraw.text((560, 19), str(newACCount[idx]["count"]), fill = (0, 0, 0), font = rankingFont)
        resImg.paste(rankingImg, (0, 65 + 63 * idx))
    resImg.save("data/rankingImg_fixed.jpg")

    # データをアップロード
    acCount = nowACCount
    uploadToDropbox()

    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    # ランキングをツイート
    tweetText = "Unique AC 数ランキング TOP " + str(rankNum) + " !!\n"
    api.update_with_media(filename = "data/rankingImg_fixed.jpg", status = tweetText + "\n" + timeStamp)
