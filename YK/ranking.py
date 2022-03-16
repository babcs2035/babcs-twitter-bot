# import
import os
import tweepy
import datetime
import json
import dropbox
import urllib
from PIL import Image, ImageDraw, ImageFont
import pickle
import codecs

# グローバル変数
YKIDs = set()
acCount = {}

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global YKIDs
    global acCount

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # YKID をダウンロード
    dbx.files_download_to_file("YK/YKIDs.txt", "/YK/YKIDs.txt")
    with open("YK/YKIDs.txt", "rb") as f:
        YKIDs = pickle.load(f)
    print("cper_bot-YK-ranking: Downloaded YKIDs (size : ", str(len(YKIDs)), ")")
    
    # acCount をダウンロード
    dbx.files_download_to_file("acCount.txt", "/YK/acCount.txt")
    with open("acCount.txt", "rb") as f:
        acCount = pickle.load(f)
    print("cper_bot-YK-ranking: Downloaded acCount (size : ", str(len(acCount)), ")")

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
        dbx.files_upload(f.read(), "/YK/acCount.txt", mode = dropbox.files.WriteMode.overwrite)
    print("cper_bot-YK-ranking: Uploaded acCount (size : ", str(len(acCount)), ")")

def ranking():
    
    # グローバル変数
    global YKIDs
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
    for (ykID, twitterID) in YKIDs:
        url = "https://yukicoder.me/api/v1/user/name/" + urllib.parse.quote_plus(ykID, encoding = "utf-8")
        try:
            acCountJson = urllib.request.urlopen(url)
            acCountData = json.loads(acCountJson.read().decode("utf-8"))
            nowACCount[str(ykID)] = int(acCountData["Solved"])
        except:
            print("cper_bot-YK-ranking: acCountJson Error (ykID = " + ykID + ")")

    newACCount = []
    for (ykID, twitterID) in YKIDs:
        if ykID in acCount and ykID in nowACCount:
            if nowACCount[ykID] - acCount[ykID] > 0:
                newACCount.append(({"ykID" : ykID, "twitterID" : twitterID, "count" : nowACCount[ykID] - acCount[ykID]}))
    newACCount.sort(key = lambda x: x["count"], reverse = True)
    
    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    if len(newACCount) == 0:
        api.update_status("yukicoder Unique AC 数ランキング\n（該当ユーザーはいませんでした・・・）" + "\n" + timeStamp)
        acCount = nowACCount
        uploadToDropbox()
        return

    # Unique AC 数ランキングを作成
    countRankNum = 1
    countNum = 1
    rankingFont = ImageFont.truetype("YK/data/fontR.ttc", 32)
    rankingFontS = ImageFont.truetype("YK/data/fontB.ttc", 32)
    countRankingFirstImg = Image.open("YK/data/countRankingImg (first).jpg")
    countResImg = Image.new("RGB", (738, 65 + 63 * len(newACCount)))
    countResImg.paste(countRankingFirstImg, (0, 0))
    awardsList = []
    for idx in range(len(newACCount)):
        countRankingImg = Image.open("YK/data/rankingImg (cell).jpg")
        countRankingDraw = ImageDraw.Draw(countRankingImg)
        if idx > 0:
            if int(newACCount[idx - 1]["count"]) > int(newACCount[idx]["count"]):
                countRankNum = countRankNum + countNum
                countNum = 1
            else:
                countNum = countNum + 1
        if countRankNum <= 5:
            awardsList.append("@" + newACCount[idx]["twitterID"])
            countRankingDraw.text((10, 7), str(countRankNum), fill = (0, 0, 0), font = rankingFontS)
            countRankingDraw.text((120, 7), newACCount[idx]["ykID"], fill = (0, 0, 0), font = rankingFontS)
            countRankingDraw.text((560, 7), str(newACCount[idx]["count"]), fill = (0, 0, 0), font = rankingFontS)
        else:
            countRankingDraw.text((10, 7), str(countRankNum), fill = (0, 0, 0), font = rankingFont)
            countRankingDraw.text((120, 7), newACCount[idx]["ykID"], fill = (0, 0, 0), font = rankingFont)
            countRankingDraw.text((560, 7), str(newACCount[idx]["count"]), fill = (0, 0, 0), font = rankingFont)
        countResImg.paste(countRankingImg, (0, 65 + 63 * idx))
    countResImg.save("YK/data/countRankingImg_fixed.jpg")

    # ランキングをツイート
    countTweetText = "yukicoder Unique AC 数ランキング TOP " + str(countRankNum) + "\n入賞の " + " , ".join(awardsList) + " さん おめでとうございます！\n"
    api.update_status_with_media(filename = "YK/data/countRankingImg_fixed.jpg", status = countTweetText + "\n" + timeStamp)
    
    # データをアップロード
    acCount = nowACCount
    uploadToDropbox()

if __name__ == '__main__':
    print("cper_bot-YK-ranking: Running as debug...")
    ranking()
    print("cper_bot-YK-ranking: Debug finished")
