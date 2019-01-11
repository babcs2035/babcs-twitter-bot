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
AOJID = []
TwitterID = []
acCount = {}

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global AOJID
    global TwitterID
    global acCount

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # AOJID をダウンロード
    dbx.files_download_to_file("AOJID.txt", "/AOJ/AOJID.txt")
    with open("AOJID.txt", "r") as f:
        AOJID.clear()
        for id in f:
            AOJID.append(id.rstrip("\n"))
    print("AOJ-ranking: Downloaded AOJID (size : ", str(len(AOJID)), ")")
    
    # TwitterID をダウンロード
    dbx.files_download_to_file("TwitterID.txt", "/AOJ/TwitterID.txt")
    with open("TwitterID.txt", "r") as f:
        TwitterID.clear()
        for id in f:
            TwitterID.append(id.rstrip("\n"))
    print("AOJ-ranking: Downloaded TwitterID (size : ", str(len(TwitterID)), ")")
    
    # acCount をダウンロード
    dbx.files_download_to_file("acCount.txt", "/AOJ/acCount.txt")
    with open("acCount.txt", "rb") as f:
        acCount = pickle.load(f)
    print("AOJ-ranking: Downloaded acCount (size : ", str(len(acCount)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global acCount
    
    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # acCount をアップロード
    with open("acCount.txt", "wb") as f:
        pickle.dump(acCount, f)
    with open("acCount.txt", "rb") as f:
        dbx.files_delete("/AOJ/acCount.txt")
        dbx.files_upload(f.read(), "/AOJ/acCount.txt")
    print("AOJ-ranking: Uploaded acCount (size : ", str(len(acCount)), ")")
    
    # countRankingImg_fixed をアップロード
    with open("AOJ/data/countRankingImg_fixed.jpg", "rb") as f:
        dbx.files_upload(f.read(), "/_backup/AOJ/countRankingImg_fixed/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".jpg")
        print("AOJ-ranking: Uploaded countRankingImg_fixed")

# list 内の要素の添え字を返す（無い場合は -1）
def myIndex(x, l):
    if x in l:
        return l.index(x)
    else:
        return -1

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
    nowACCount = {}
    for user in AOJID:
        acCountJson = urllib.request.urlopen("https://judgeapi.u-aizu.ac.jp/users/" + str(user))
        acCountData = json.loads(acCountJson.read().decode("utf-8"))
        nowACCount[str(user)] = int(acCountData["status"]["solved"])

    newACCount = []
    for user in AOJID:
        if user in acCount:
            if nowACCount[user] - acCount[user] > 0:
                newACCount.append(({"user_id" : user, "count" : nowACCount[user] - acCount[user]}))
    newACCount.sort(key = lambda x: x["count"], reverse = True)

    # Unique AC 数ランキングを作成
    countRankNum = 1
    countNum = 1
    rankingFont = ImageFont.truetype("AOJ/data/YuGothM.ttc", 32)
    countRankingFirstImg = Image.open("AOJ/data/countRankingImg (first).jpg")
    countResImg = Image.new("RGB", (738, 65 + 63 * len(newACCount)))
    countResImg.paste(countRankingFirstImg, (0, 0))
    for idx in range(len(newACCount)):
        countRankingImg = Image.open("AOJ/data/rankingImg (cell).jpg")
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
    countResImg.save("AOJ/data/countRankingImg_fixed.jpg")

    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    # ランキングをツイート
    countTweetText = "AOJ Unique AC 数ランキング TOP " + str(countRankNum) + "\n"
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
            countTweetText += str(countRankNum) + " 位 " + newACCount[idx]["user_id"] + " ( @" + str(TwitterID[myIndex(newACCount[idx]["user_id"],AOJID)]) + " ) " + str(newACCount[idx]["count"]) + " Unique AC\n"
        else:
            break
    api.update_with_media(filename = "AOJ/data/countRankingImg_fixed.jpg", status = countTweetText + "\n" + timeStamp)
    
    # データをアップロード
    acCount = nowACCount
    uploadToDropbox()

if __name__ == '__main__':
    print("AOJ-ranking: Running as debug...")
    ranking()
    print("AOJ-ranking: Debug finished")
