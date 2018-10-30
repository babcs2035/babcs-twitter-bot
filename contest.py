# import
import os
import tweepy
import datetime
import time
import json
import urllib
from PIL import Image, ImageDraw, ImageFont

def epoch_to_datetime(epoch):
    return datetime.datetime(*time.localtime(epoch)[:6])

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
    contestsList = []
    for contest in contestsJsonData:
        date = epoch_to_datetime(contest["startTimeSeconds"])
        if datetime.datetime.today() < date:
            contestsList.append(contest)

    # 画像生成
    listFont = ImageFont.truetype("data/YuGothM.ttc", 32)
    contestsListFirstImg = Image.open("data/contestsListImg (first).jpg")
    contestsListImg = Image.new("RGB", (850, 65 + 63 * len(contestsList)))
    contestsListImg.paste(contestsListFirstImg, (0, 0))
    idx = 0
    for contest in contestsList:
        contestListImg = Image.open("data/contestsListImg (cell).jpg")
        contestListDraw = ImageDraw.Draw(contestListImg)
        contestListDraw.text((10, 19), str(epoch_to_datetime(contest["startTimeSeconds"])), fill = (0, 0, 0), font = listFont)
        contestListDraw.text((220, 19), str(contest["title"]), fill = (0, 0, 0), font = listFont)
        contestListDraw.text((640, 19), str(contest["ratedRange"]), fill = (0, 0, 0), font = listFont)
        contestsListImg.paste(contestListImg, (0, 65 + 63 * idx))
        idx = idx + 1
    contestsListImg.save("data/contestsListImg_fixed.jpg")
