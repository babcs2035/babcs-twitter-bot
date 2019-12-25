# import
import os
import tweepy
import datetime
import time
import json
import urllib
from PIL import Image, ImageDraw, ImageFont
from dateutil.relativedelta import relativedelta

def epoch_to_datetime(epoch):
    return datetime.datetime(*time.localtime(epoch)[:6])

def sec_to_time(sec):
    return "{0.hours:02}:{0.minutes:02}".format(relativedelta(seconds=sec))

def contest():
    
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

    # 開催予定のコンテストを取得
    contestsJsonRes = urllib.request.urlopen("https://atcoder-api.appspot.com/contests")
    contestsJsonData = json.loads(contestsJsonRes.read().decode("utf-8"))
    print("cper_bot-AtCoder-contest: Downloaded contestsJsonData")
    contestsList = []
    for contest in contestsJsonData:
        date = epoch_to_datetime(contest["startTimeSeconds"])
        if datetime.datetime.today() < date:
            contestsList.append(contest)

    if len(contestsList) == 0:
        api.update_status("現在予定されている AtCoder コンテストはありません．\nhttps://atcoder.jp/contests/\n\n" + timeStamp)
        return

    # 画像生成
    listFontR = ImageFont.truetype("AtCoder/data/fontR.ttc", 32)
    listFontB = ImageFont.truetype("AtCoder/data/fontB.ttc", 32)
    contestsListFirstImg = Image.open("AtCoder/data/contestsListImg (first).jpg")
    contestsListImg = Image.new("RGB", (1852, 68 + 64 * len(contestsList)))
    contestsListImg.paste(contestsListFirstImg, (0, 0))
    idx = 0
    for contest in contestsList:
        contest["title"] = contest["title"].replace("◉", "")
        contest["title"] = contest["title"].replace("\n", "")
        contest["title"] = contest["title"].replace("\t", "")
        contestListImg = Image.open("AtCoder/data/contestsListImg (cell).jpg")
        contestListDraw = ImageDraw.Draw(contestListImg)
        startTime = epoch_to_datetime(contest["startTimeSeconds"])
        contestListDraw.text((10, 7), str(epoch_to_datetime(contest["startTimeSeconds"])), fill = (0, 0, 0), font = listFontR)
        if str(contest["ratedRange"]) == " ~ 1999":
            contestListDraw.text((360, 7), str(contest["title"]), fill = (0, 0, 255), font = listFontB)
            contestListDraw.text((1660, 7), str(contest["ratedRange"]), fill = (0, 0, 255), font = listFontB)
        elif str(contest["ratedRange"]) == " ~ 2799":
            contestListDraw.text((360, 7), str(contest["title"]), fill = (255, 150, 50), font = listFontB)
            contestListDraw.text((1660, 7), str(contest["ratedRange"]), fill = (255, 150, 50), font = listFontB)
        elif str(contest["ratedRange"]) == "All":
            contestListDraw.text((360, 7), str(contest["title"]), fill = (255, 0, 0), font = listFontB)
            contestListDraw.text((1660, 7), str(contest["ratedRange"]), fill = (255, 0, 0), font = listFontB)
        else:
            contestListDraw.text((360, 7), str(contest["title"]), fill = (0, 0, 0), font = listFontR)
            contestListDraw.text((1660, 7), str(contest["ratedRange"]), fill = (0, 0, 0), font = listFontR)
        contestListDraw.text((1460, 7), str(sec_to_time(contest["durationSeconds"])), fill = (0, 0, 0), font = listFontR)
        contestsListImg.paste(contestListImg, (0, 68 + 64 * idx))
        idx = idx + 1
    contestsListImg.save("AtCoder/contestsListImg_fixed.jpg")

    # リストをツイート
    listTweetText = "現在 " + str(len(contestsList)) + " の AtCoder コンテストが予定されています．\nhttps://atcoder.jp/contests/\n"
    api.update_with_media(filename = "AtCoder/contestsListImg_fixed.jpg", status = listTweetText + "\n" + timeStamp)
    print("cper_bot-AtCoder-contest: Tweeted contestsListImg_fixed")

if __name__ == '__main__':
    print("cper_bot-AtCoder-contest: Running as debug...")
    contest()
    print("cper_bot-AtCoder-contest: Debug finished")
