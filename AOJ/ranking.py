# import
import pickle
from PIL import Image, ImageDraw, ImageFont
import urllib
import dropbox
import json
import datetime
import tweepy
import log
import os
import sys
sys.path.append("../")

# グローバル変数
AOJIDs = set()
acCount = {}


# Dropbox からダウンロード
def downloadFromDropbox():

    # グローバル変数
    global AOJIDs
    global acCount

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # AOJIDs をダウンロード
    dbx.files_download_to_file("AOJ/AOJIDs.txt", "/AOJ/AOJIDs.txt")
    with open("AOJ/AOJIDs.txt", "rb") as f:
        AOJIDs = pickle.load(f)
    log.logger.info(
        "cper_bot-AOJ-ranking: Downloaded AOJIDs (size : ", str(len(AOJIDs)), ")")

    # acCount をダウンロード
    dbx.files_download_to_file("AOJ/acCount.txt", "/AOJ/acCount.txt")
    with open("AOJ/acCount.txt", "rb") as f:
        acCount = pickle.load(f)
    log.logger.info(
        "cper_bot-AOJ-ranking: Downloaded acCount (size : ", str(len(acCount)), ")")


# Dropbox にアップロード
def uploadToDropbox():

    # グローバル変数
    global acCount

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # acCount をアップロード
    with open("AOJ/acCount.txt", "wb") as f:
        pickle.dump(acCount, f)
    with open("AOJ/acCount.txt", "rb") as f:
        dbx.files_upload(f.read(), "/AOJ/acCount.txt",
                         mode=dropbox.files.WriteMode.overwrite)
    log.logger.info(
        "cper_bot-AOJ-ranking: Uploaded acCount (size : ", str(len(acCount)), ")")


def ranking():

    # グローバル変数
    global AOJIDs
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
    for (AOJID, twitterID) in AOJIDs:
        acCountJson = urllib.request.urlopen(
            "https://judgeapi.u-aizu.ac.jp/users/" + str(AOJID))
        acCountData = json.loads(acCountJson.read().decode("utf-8"))
        nowACCount[str(AOJID)] = int(acCountData["status"]["solved"])
    newACCount = []
    for (AOJID, twitterID) in AOJIDs:
        if AOJID in acCount:
            if nowACCount[AOJID] - acCount[AOJID] > 0:
                newACCount.append(
                    ({"AOJID": AOJID, "twitterID": twitterID, "count": nowACCount[AOJID] - acCount[AOJID]}))
    newACCount.sort(key=lambda x: x["count"], reverse=True)

    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    if len(newACCount) == 0:
        api.update_status(
            "AOJ Unique AC 数ランキング\n（該当ユーザーはいませんでした・・・）" + "\n" + timeStamp)
        acCount = nowACCount
        uploadToDropbox()
        return

    # Unique AC 数ランキングを作成
    countRankNum = 1
    countNum = 1
    rankingFont = ImageFont.truetype("AOJ/data/fontR.ttc", 32)
    rankingFontS = ImageFont.truetype("AtCoder/data/fontB.ttc", 32)
    countRankingFirstImg = Image.open("AOJ/data/countRankingImg (first).jpg")
    countResImg = Image.new("RGB", (738, 65 + 63 * len(newACCount)))
    countResImg.paste(countRankingFirstImg, (0, 0))
    awardsList = []
    for idx in range(len(newACCount)):
        countRankingImg = Image.open("AOJ/data/rankingImg (cell).jpg")
        countRankingDraw = ImageDraw.Draw(countRankingImg)
        if idx > 0:
            if int(newACCount[idx - 1]["count"]) > int(newACCount[idx]["count"]):
                countRankNum = countRankNum + countNum
                countNum = 1
            else:
                countNum = countNum + 1
        if countRankNum <= 5:
            awardsList.append("@" + newACCount[idx]["twitterID"])
            countRankingDraw.text((10, 7), str(
                countRankNum), fill=(0, 0, 0), font=rankingFontS)
            countRankingDraw.text(
                (120, 7), newACCount[idx]["AOJID"], fill=(0, 0, 0), font=rankingFontS)
            countRankingDraw.text((560, 7), str(
                newACCount[idx]["count"]), fill=(0, 0, 0), font=rankingFontS)
        else:
            countRankingDraw.text((10, 7), str(
                countRankNum), fill=(0, 0, 0), font=rankingFont)
            countRankingDraw.text(
                (120, 7), newACCount[idx]["AOJID"], fill=(0, 0, 0), font=rankingFont)
            countRankingDraw.text((560, 7), str(
                newACCount[idx]["count"]), fill=(0, 0, 0), font=rankingFont)
        countResImg.paste(countRankingImg, (0, 65 + 63 * idx))
    countResImg.save("AOJ/data/countRankingImg_fixed.jpg")

    # ランキングをツイート
    countTweetText = "AOJ Unique AC 数ランキング TOP " + \
        str(countRankNum) + "\n入賞の " + \
        " , ".join(awardsList) + " さん おめでとうございます！\n"
    api.update_staus_with_media(
        filename="AOJ/data/countRankingImg_fixed.jpg", status=countTweetText + "\n" + timeStamp)

    # データをアップロード
    acCount = nowACCount
    uploadToDropbox()


if __name__ == '__main__':
    log.logger.info("cper_bot-AOJ-ranking: Running as debug...")
    ranking()
    log.logger.info("cper_bot-AOJ-ranking: Debug finished")
