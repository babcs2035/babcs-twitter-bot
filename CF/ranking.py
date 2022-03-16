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
CFIDs = set()
acCount = {}

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global CFIDs
    global acCount

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # CFIDs をダウンロード
    dbx.files_download_to_file("CF/CFIDs.txt", "/CF/CFIDs.txt")
    with open("CF/CFIDs.txt", "rb") as f:
        CFIDs = pickle.load(f)
    print("cper_bot-CF-ranking: Downloaded CFIDs (size : ", str(len(CFIDs)), ")")

    # acCount をダウンロード
    dbx.files_download_to_file("CF/acCount.txt", "/CF/acCount.txt")
    with open("CF/acCount.txt", "rb") as f:
        acCount = pickle.load(f)
    print("cper_bot-CF-ranking: Downloaded acCount (size : ", str(len(acCount)), ")")

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
        dbx.files_upload(f.read(), "/CF/acCount.txt", mode = dropbox.files.WriteMode.overwrite)
    print("cper_bot-CF-ranking: Uploaded acCount (size : ", str(len(acCount)), ")")

def ranking():
    
    # グローバル変数
    global CFIDs
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
    for (cfID, twitterID) in CFIDs:
        try:
            acCountJson = urllib.request.urlopen("https://codeforces.com/api/user.status?handle=" + str(cfID))
        except:
            print("cper_bot-CF-ranking: acCountJson Error")
            continue
        acCountData = json.loads(acCountJson.read().decode("utf-8"))
        cnt = 0
        for sub in acCountData["result"]:
            if sub["verdict"] == "OK":
                cnt = cnt + 1
        nowACCount[str(cfID)] = int(cnt)
    for (cfID, twitterID) in CFIDs:
        if cfID in acCount and cfID in nowACCount:
            if nowACCount[cfID] - acCount[cfID] > 0:
                newACCount.append(({"cfID" : cfID, "twitterID" : twitterID, "count" : nowACCount[cfID] - acCount[cfID]}))
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
    rankingFontS = ImageFont.truetype("CF/data/fontB.ttc", 32)
    countRankingFirstImg = Image.open("CF/data/countRankingImg (first).jpg")
    countResImg = Image.new("RGB", (738, 65 + 63 * len(newACCount)))
    countResImg.paste(countRankingFirstImg, (0, 0))
    awardsList = []
    for idx in range(len(newACCount)):
        countRankingImg = Image.open("CF/data/rankingImg (cell).jpg")
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
            countRankingDraw.text((120, 7), newACCount[idx]["cfID"], fill = (0, 0, 0), font = rankingFontS)
            countRankingDraw.text((560, 7), str(newACCount[idx]["count"]), fill = (0, 0, 0), font = rankingFontS)
        else:
            countRankingDraw.text((10, 7), str(countRankNum), fill = (0, 0, 0), font = rankingFont)
            countRankingDraw.text((120, 7), newACCount[idx]["cfID"], fill = (0, 0, 0), font = rankingFont)
            countRankingDraw.text((560, 7), str(newACCount[idx]["count"]), fill = (0, 0, 0), font = rankingFont)
        countResImg.paste(countRankingImg, (0, 65 + 63 * idx))
    countResImg.save("CF/data/countRankingImg_fixed.jpg")

    # ランキングをツイート
    countTweetText = "Codeforces AC 提出数ランキング TOP " + str(countRankNum) + "\n入賞の " + " , ".join(awardsList) + " さん おめでとうございます！\n"
    api.update_status_with_media(filename = "CF/data/countRankingImg_fixed.jpg", status = countTweetText + "\n" + timeStamp)
    
    # データをアップロード
    acCount = nowACCount
    uploadToDropbox()

if __name__ == '__main__':
    print("cper_bot-CF-ranking: Running as debug...")
    ranking()
    print("cper_bot-CF-ranking: Debug finished")
