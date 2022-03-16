# import
import os
import tweepy
import datetime
import time
import urllib
import requests
import json
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
    contestsJsonRes = urllib.request.urlopen("https://codeforces.com/api/contest.list?lang=us")
    contestsJsonData = json.loads(contestsJsonRes.read().decode("utf-8"))
    contestsList = []
    for contest in contestsJsonData["result"]:
        if str(contest["phase"]) == "BEFORE":
            contestsList.append(contest)
    contestsList.sort(key = lambda x: x["startTimeSeconds"])
    if len(contestsList) == 0:
        api.update_status("現在予定されている Codeforces コンテストはありません．\nhttps://codeforces.com/contests\n\n" + timeStamp)
        return

    # 画像生成
    listFont = ImageFont.truetype("CF/data/fontR.ttc", 32)
    contestsListFirstImg = Image.open("CF/data/contest/contestsListImg (first).jpg")
    contestsListImg = Image.new("RGB", (1852, 68 + 64 * len(contestsList)))
    contestsListImg.paste(contestsListFirstImg, (0, 0))
    idx = 0
    for contest in contestsList:
        contestListImg = Image.open("CF/data/contest/contestsListImg (cell).jpg")
        contestListDraw = ImageDraw.Draw(contestListImg)
        contestListDraw.text((10, 7), str(epoch_to_datetime(contest["startTimeSeconds"])), fill = (0, 0, 0), font = listFont)
        contestListDraw.text((360, 7), str(contest["name"]), fill = (0, 0, 0), font = listFont)
        contestListDraw.text((1460, 7), str(sec_to_time(contest["durationSeconds"])), fill = (0, 0, 0), font = listFont)
        contestListDraw.text((1660, 7), str(contest["type"]), fill = (0, 0, 0), font = listFont)
        contestsListImg.paste(contestListImg, (0, 68 + 64 * idx))
        idx = idx + 1
    contestsListImg.save("CF/data/contest/contestsListImg_fixed.jpg")

    # リストをツイート
    listTweetText = "現在 " + str(idx) + " の Codeforces コンテストが予定されています．\nhttps://codeforces.com/contests\n"
    api.update_status_with_media(filename = "CF/data/contest/contestsListImg_fixed.jpg", status = listTweetText + "\n" + timeStamp)

if __name__ == '__main__':
    print("cper_bot-CF-contest: Running as debug...")
    contest()
    print("cper_bot-CF-contest: Debug finished")
