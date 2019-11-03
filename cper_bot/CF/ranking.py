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
CFID = []
TwitterID = []
acCount = {}

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global CFID
    global TwitterID
    global acCount

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # CFID をダウンロード
    dbx.files_download_to_file("CF/CFID.txt", "/CF/CFID.txt")
    with open("CF/CFID.txt", "r") as f:
        CFID.clear()
        for id in f:
            CFID.append(id.rstrip("\n"))
    print("CF-ranking: Downloaded CFID (size : ", str(len(CFID)), ")")
    
    # TwitterID をダウンロード
    dbx.files_download_to_file("CF/TwitterID.txt", "/CF/TwitterID.txt")
    with open("CF/TwitterID.txt", "r") as f:
        TwitterID.clear()
        for id in f:
            TwitterID.append(id.rstrip("\n"))
    print("CF-ranking: Downloaded TwitterID (size : ", str(len(TwitterID)), ")")
    
    # acCount をダウンロード
    dbx.files_download_to_file("CF/acCount.txt", "/CF/acCount.txt")
    with open("CF/acCount.txt", "rb") as f:
        acCount = pickle.load(f)
    print("CF-ranking: Downloaded acCount (size : ", str(len(acCount)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global acCount
    
    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # acCount をアップロード
    with open("CF/acCount.txt", "wb") as f:
        pickle.dump(acCount, f)
    with open("CF/acCount.txt", "rb") as f:
        dbx.files_delete("/CF/acCount.txt")
        dbx.files_upload(f.read(), "/CF/acCount.txt")
    print("CF-ranking: Uploaded acCount (size : ", str(len(acCount)), ")")

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

    # AC 提出数を取得
    nowACCount = {}
    newACCount = []
    for user in CFID:
        acCountJson = urllib.request.urlopen("https://codeforces.com/api/user.status?handle=" + str(user))
        acCountData = json.loads(acCountJson.read().decode("utf-8"))
        cnt = 0
        for sub in acCountData["result"]:
            if sub["verdict"] == "OK":
                cnt = cnt + 1
        nowACCount[str(user)] = int(cnt)
    for user in CFID:
        if user in acCount:
            if nowACCount[user] - acCount[user] > 0:
                newACCount.append(({"user_id" : user, "count" : nowACCount[user] - acCount[user]}))
    newACCount.sort(key = lambda x: x["count"], reverse = True)
    
    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    if len(newACCount) == 0:
        api.update_status("Codeforces AC 提出数ランキング\n（該当ユーザーはいませんでした・・・）" + "\n" + timeStamp)
        acCount = nowACCount
        uploadToDropbox()
        return

    # AC 提出数ランキングを作成
    countRankNum = 1
    countNum = 1
    rankingFont = ImageFont.truetype("CF/data/fontR.ttc", 32)
    countRankingFirstImg = Image.open("CF/data/countRankingImg (first).jpg")
    countResImg = Image.new("RGB", (738, 65 + 63 * len(newACCount)))
    countResImg.paste(countRankingFirstImg, (0, 0))
    for idx in range(len(newACCount)):
        countRankingImg = Image.open("CF/data/rankingImg (cell).jpg")
        countRankingDraw = ImageDraw.Draw(countRankingImg)
        if idx > 0:
            if int(newACCount[idx - 1]["count"]) > int(newACCount[idx]["count"]):
                countRankNum = countRankNum + countNum
                countNum = 1
            else:
                countNum = countNum + 1
        countRankingDraw.text((10, 7), str(countRankNum), fill = (0, 0, 0), font = rankingFont)
        countRankingDraw.text((120, 7), newACCount[idx]["user_id"], fill = (0, 0, 0), font = rankingFont)
        countRankingDraw.text((560, 7), str(newACCount[idx]["count"]), fill = (0, 0, 0), font = rankingFont)
        countResImg.paste(countRankingImg, (0, 65 + 63 * idx))
    countResImg.save("CF/data/countRankingImg_fixed.jpg")

    # ランキングをツイート
    countTweetText = "Codeforces AC 提出数ランキング TOP " + str(countRankNum) + "\n"
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
            countTweetText += str(countRankNum) + " 位 " + newACCount[idx]["user_id"] + " ( @" + str(TwitterID[myIndex(newACCount[idx]["user_id"],CFID)]) + " ) " + str(newACCount[idx]["count"]) + " AC\n"
        else:
            break
    api.update_with_media(filename = "CF/data/countRankingImg_fixed.jpg", status = countTweetText + "\n" + timeStamp)
    
    # データをアップロード
    acCount = nowACCount
    uploadToDropbox()

if __name__ == '__main__':
    print("CF-ranking: Running as debug...")
    ranking()
    print("CF-ranking: Debug finished")
