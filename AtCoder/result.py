# import
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
import shutil
import json
import pickle
import urllib
import requests
import dropbox
import time
import datetime
import tweepy
import log
import os


# グローバル変数
AtCoderIDs = []
ratings = {}
canPassDL = False

# Dropbox からダウンロード


def downloadFromDropbox():

    # グローバル変数
    global AtCoderIDs
    global ratings

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # AtCoderIDs をダウンロード
    dbx.files_download_to_file(
        "AtCoder/AtCoderIDs.txt", "/AtCoder/AtCoderIDs.txt")
    with open("AtCoder/AtCoderIDs.txt", "rb") as f:
        AtCoderIDs = pickle.load(f)
    log.logger.info(
        "cper_bot-AtCoder-result: Downloaded AtCoderIDs (size : ", str(len(AtCoderIDs)), ")")

    # ratings をダウンロード
    dbx.files_download_to_file("AtCoder/ratings.txt", "/AtCoder/ratings.txt")
    with open("AtCoder/ratings.txt", "rb") as f:
        ratings = pickle.load(f)
    log.logger.info(
        "cper_bot-AtCoder-result: Downloaded ratings (size : ", str(len(ratings)), ")")

# Dropbox にアップロード


def uploadToDropbox():

    # グローバル変数
    global ratings

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # ratings をアップロード
    with open("AtCoder/ratings.txt", "wb") as f:
        pickle.dump(ratings, f)
    with open("AtCoder/ratings.txt", "rb") as f:
        dbx.files_upload(f.read(), "/AtCoder/ratings.txt",
                         mode=dropbox.files.WriteMode.overwrite)
    log.logger.info(
        "cper_bot-AtCoder-result: Uploaded ratings (size : ", str(len(ratings)), ")")


def epoch_to_datetime(epoch):
    return datetime.datetime(*time.localtime(epoch)[:6])


def downloadImage(url, dst_path):

    global canPassDL

    if canPassDL and os.path.exists(dst_path):
        return
    if url[0] != 'h':
        shutil.copy("AtCoder/data/default.png", dst_path)
        return
    try:
        with urllib.request.urlopen(url) as web_file, open(dst_path, 'wb') as local_file:
            local_file.write(web_file.read())
    except:
        log.logger.info("cper_bot-AtCoder-result: downloadImage Error (url = " +
                        url + ", dst_path = " + dst_path + ")")


def makeRanking(type, listData, unit):

    global AtCoderIDs
    global ratings

    colors = [[0, 0, 0], [128, 128, 128], [128, 64, 0], [0, 128, 0], [
        0, 192, 192], [0, 0, 255], [192, 192, 0], [255, 128, 0], [255, 0, 0]]
    rows = 30

    flag = int(listData[0][str(type)]) > int(
        listData[len(listData) - 1][str(type)])
    rankNum = 1
    countNum = 1
    rankingFont = ImageFont.truetype("AtCoder/data/fontR.ttc", 32)
    rankingFontS = ImageFont.truetype("AtCoder/data/fontB.ttc", 32)
    rankingFirstImg = Image.open(
        "AtCoder/data/result/" + str(type) + "RankingImg (first).jpg")
    resImg = Image.new("RGB", (738 * int((len(listData) +
                       rows - 1) / rows), 65 + 63 * min(len(listData), rows)))
    awardsList = []
    for idx in range(len(listData)):
        if idx % rows == 0:
            resImg.paste(rankingFirstImg, (738 * int(idx / rows), 0))
        rankingImg = Image.open("AtCoder/data/result/rankingImg (cell).jpg")
        rankingDraw = ImageDraw.Draw(rankingImg)
        if idx > 0:
            if flag and int(listData[idx - 1][str(type)]) > int(listData[idx][str(type)]):
                rankNum = rankNum + countNum
                countNum = 1
            elif (not flag) and int(listData[idx - 1][str(type)]) < int(listData[idx][str(type)]):
                rankNum = rankNum + countNum
                countNum = 1
            else:
                countNum = countNum + 1

        colorIndex = 0
        for border in range(7, 0, -1):
            if str(listData[idx]["atcoderID"]) in ratings:
                if ratings[str(listData[idx]["atcoderID"])] >= border * 400:
                    colorIndex = border + 1
                    break
        if rankNum <= 8:
            rankingDraw.text((10, 7), str(rankNum),
                             fill=(0, 0, 0), font=rankingFontS)
            rankingDraw.text((182, 7), listData[idx]["atcoderID"], fill=(
                colors[colorIndex][0], colors[colorIndex][1], colors[colorIndex][2]), font=rankingFontS)
            rankingDraw.text((560, 7), str(listData[idx][str(type)]), fill=(
                0, 0, 0), font=rankingFontS)
            awardsList.append("@" + listData[idx]["twitterID"])
        else:
            rankingDraw.text((10, 7), str(rankNum),
                             fill=(0, 0, 0), font=rankingFont)
            rankingDraw.text((182, 7), listData[idx]["atcoderID"], fill=(
                colors[colorIndex][0], colors[colorIndex][1], colors[colorIndex][2]), font=rankingFont)
            rankingDraw.text((560, 7), str(
                listData[idx][str(type)]), fill=(0, 0, 0), font=rankingFont)

        # ユーザーのアバター画像をダウンロード
        userpage = requests.get(
            url="https://atcoder.jp/users/" + listData[idx]["atcoderID"])
        try:
            userpage.raise_for_status()
            userpageData = BeautifulSoup(userpage.text, "html.parser")
            downloadImage(userpageData.find(
                "img", class_="avatar").attrs["src"], "AtCoder/data/" + listData[idx]["atcoderID"] + ".png")
            rankingImg.paste(Image.open(
                "AtCoder/data/" + listData[idx]["atcoderID"] + ".png").resize((59, 59)), (105, 2))
        except:
            log.logger.info(
                "cper_bot-AtCoder-result: userpageData Error (atcoderID = " + listData[idx]["atcoderID"] + ")")
        resImg.paste(
            rankingImg, (738 * int(idx / rows), 65 + 63 * (idx % rows)))
    resImg.save("AtCoder/data/result/" + str(type) + "RankingImg_fixed.jpg")
    return " ランキング TOP " + str(rankNum) + "\n入賞の " + " , ".join(awardsList) + " さん おめでとうございます！\n"


def result():

    # グローバル変数
    global AtCoderIDs
    global contestFlag
    global ratings
    global canPassDL

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

    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    # 色が変化したユーザーに通知
    for atcoderID, twitterID in AtCoderIDs:

        # 現在の色を取得
        profileURL = "https://atcoder.jp/users/" + atcoderID
        profileHTML = requests.get(profileURL)
        try:
            profileHTML.raise_for_status()
            profileData = BeautifulSoup(profileHTML.text, "html.parser")
        except:
            log.logger.info("cper_bot-AtCoder-result: profileHTML Error")
            continue
        log.logger.info("cper_bot-AtCoder-result: Downloaded " +
                        atcoderID + "'s profileData")
        profileTable = profileData.find_all("table", class_="dl-table")
        try:
            nowRating = int(
                profileTable[1].contents[3].contents[1].contents[0].contents[0])
        except:
            nowRating = -1

        # 色が変わったか調べる
        strs = ["灰色", "茶色", "緑", "水色", "青", "黄色", "オレンジ", "レッド"]
        if atcoderID in ratings:
            for border in range(7, 0, -1):
                if ratings[str(atcoderID)] < border * 400 and border * 400 <= nowRating:
                    api.update_status(atcoderID + " ( @" + twitterID + " ) さんの AtCoder レートが " + str(ratings[atcoderID]) + " -> " + str(
                        nowRating) + " となり，" + strs[border] + "コーダーになりました！おめでとうございます！！！\n" + profileURL + "\n" + timeStamp)
                    log.logger.info("cper_bot-AtCoder-result: Tweeted " +
                                    atcoderID + " ( @" + twitterID + " )'s rating change")
                    break
        ratings[atcoderID] = nowRating

    # コンテスト結果のランキング処理
    # 取得すべきコンテストを取得
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    session = requests.Session()
    request = session.get(
        url="https://kenkoooo.com/atcoder/resources/contests.json", headers=headers)
    contestsJsonData = json.loads(request.text)
    log.logger.info("cper_bot-AtCoder-result: Downloaded contestsJsonData")
    newcontests = []
    yesterday = datetime.datetime.today() - datetime.timedelta(1)
    for contest in contestsJsonData:
        date = epoch_to_datetime(
            contest["start_epoch_second"] + contest["duration_second"])
        if yesterday <= date and date < datetime.datetime.today():
            contest["title"] = contest["title"].replace("◉", "")
            contest["title"] = contest["title"].replace("\n", "")
            contest["title"] = contest["title"].replace("\t", "")
            newcontests.append(str(contest["title"]))

    # コンテストごとに処理
    for contest in newcontests:
        rankList = []
        perfList = []
        diffList = []

        # ユーザーの成績を取得
        for atcoderID, twitterID in AtCoderIDs:
            reslistURL = "https://atcoder.jp/users/" + \
                str(atcoderID) + "/history"
            reslistHTML = requests.get(reslistURL)
            try:
                reslistHTML.raise_for_status()
                reslistData = BeautifulSoup(reslistHTML.text, "html.parser")
            except:
                log.logger.info("cper_bot-AtCoder-result: reslistHTML Error")
                continue
            log.logger.info(
                "cper_bot-AtCoder-result: Downloaded " + atcoderID + "'s reslistData")
            reslistTable = reslistData.find_all("table")
            if len(reslistTable) == 0:
                continue
            reslistRows = reslistTable[0].find_all("tr")
            del reslistRows[0]
            for row in reslistRows:
                if str(contest) == str(row.contents[3].contents[0].contents[0]):
                    if str(row.contents[5].contents[0].contents[0]) != "-":
                        rankList.append({"atcoderID": atcoderID, "twitterID": twitterID, "rank": int(
                            row.contents[5].contents[0].contents[0])})
                    if str(row.contents[7].contents[0]) != "-":
                        perfList.append({"atcoderID": atcoderID, "twitterID": twitterID, "perf": int(
                            row.contents[7].contents[0])})
                    if str(row.contents[11].contents[0]) != "-":
                        if str(row.contents[11].contents[0]) == "±0":
                            diffList.append(
                                {"atcoderID": atcoderID, "twitterID": twitterID, "diff": int(0)})
                        else:
                            diffList.append({"atcoderID": atcoderID, "twitterID": twitterID, "diff": int(
                                row.contents[11].contents[0])})
                    break
        log.logger.info("cper_bot-AtCoder-result: Checked " +
                        str(contest) + " result")

        # ランキングを作成
        canPassDL = False
        if len(rankList) > 0:
            rankList.sort(key=lambda x: x["rank"])
            tweetText = str(contest) + " 順位表" + \
                makeRanking("rank", rankList, "位")
            api.update_status_with_media(
                filename="AtCoder/data/result/rankRankingImg_fixed.jpg", status=tweetText + "\n" + timeStamp)
            log.logger.info("cper_bot-AtCoder-result: Tweeted " +
                            str(contest) + " rankRanking")
            canPassDL = True
        if len(perfList) > 0:
            perfList.sort(key=lambda x: x["perf"], reverse=True)
            tweetText = str(contest) + " パフォーマンス値" + \
                makeRanking("perf", perfList, "perf.")
            api.update_status_with_media(
                filename="AtCoder/data/result/perfRankingImg_fixed.jpg", status=tweetText + "\n" + timeStamp)
            log.logger.info("cper_bot-AtCoder-result: Tweeted " +
                            str(contest) + " perfRanking")
            canPassDL = True
        if len(diffList) > 0:
            diffList.sort(key=lambda x: x["diff"], reverse=True)
            tweetText = str(contest) + " レート変動値" + \
                makeRanking("diff", diffList, "")
            api.update_status_with_media(
                filename="AtCoder/data/result/diffRankingImg_fixed.jpg", status=tweetText + "\n" + timeStamp)
            log.logger.info("cper_bot-AtCoder-result: Tweeted " +
                            str(contest) + " diffRanking")
            canPassDL = True

    # データをアップロード
    uploadToDropbox()


if __name__ == '__main__':
    log.logger.info("cper_bot-AtCoder-result: Running as debug...")
    result()
    log.logger.info("cper_bot-AtCoder-result: Debug finished")
