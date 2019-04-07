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
    contestsJsonRes = urllib.request.urlopen("https://yukicoder.me/api/v1/contest/future")
    contestsJsonData = json.loads(contestsJsonRes.read().decode("utf-8"))
    contestsList = []
    for contest in contestsJsonData:
        contest["Date"] = contest["Date"][:10] + " " + contest["Date"][11:19]
        contest["EndDate"] = contest["EndDate"][:10] + " " + contest["EndDate"][11:19]
        contestsList.append(contest)
    if len(contestsList) == 0:
        api.update_status("現在予定されている yukicoder コンテストはありません．\nhttps://yukicoder.me/contests\n\n" + timeStamp)
        return

    # 画像生成
    listFont = ImageFont.truetype("YK/data/YuGothM.ttc", 32)
    contestsListFirstImg = Image.open("YK/data/contestsListImg (first).jpg")
    contestsListImg = Image.new("RGB", (1772, 68 + 64 * len(contestsList)))
    contestsListImg.paste(contestsListFirstImg, (0, 0))
    idx = 0
    for contest in contestsList:
        contestListImg = Image.open("YK/data/contestsListImg (cell).jpg")
        contestListDraw = ImageDraw.Draw(contestListImg)
        contestListDraw.text((10, 15), str(contest["Date"]), fill = (0, 0, 0), font = listFont)
        contestListDraw.text((360, 15), str(contest["EndDate"]), fill = (0, 0, 0), font = listFont)
        contestListDraw.text((710, 15), str(contest["Name"]), fill = (0, 0, 0), font = listFont)
        contestsListImg.paste(contestListImg, (0, 68 + 64 * idx))
        idx = idx + 1
    contestsListImg.save("YK/contestsListImg_fixed.jpg")

    # リストをツイート
    listTweetText = "現在 " + str(len(contestsList)) + " の yukicoder コンテストが予定されています．\nhttps://yukicoder.me/contests\n"
    api.update_with_media(filename = "YK/contestsListImg_fixed.jpg", status = listTweetText + "\n" + timeStamp)

if __name__ == '__main__':
    print("YK-contest: Running as debug...")
    contest()
    print("YK-contest: Debug finished")
