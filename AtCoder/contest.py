# import
import os
import tweepy
import datetime
import time
import json
import urllib
import requests
from PIL import Image, ImageDraw, ImageFont
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
import gc

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
    contestsURL = "https://atcoder.jp/contests/?lang=ja"
    contestsHTML = requests.get(contestsURL)
    try:
        contestsHTML.raise_for_status()
        contestsData = BeautifulSoup(contestsHTML.text, "html.parser")
    except:
        print("cper_bot-AtCoder-contest: contestsHTML Error")
        return
    contestsTable = contestsData.find_all("table", class_ = "table table-default table-striped table-hover table-condensed table-bordered small")
    if len(contestsTable) == 0:
        api.update_status("現在予定されている AtCoder コンテストはありません．\nhttps://atcoder.jp/contests/\n\n" + timeStamp)
        return

    # １行ずつ解析
    contestsRows = contestsTable[1].find_all("tr")    
    del contestsRows[0]
    print("cper_bot-AtCoder-contest: Downloaded contestsRows")
    contestsList = []
    for contest in contestsRows:
        contestData = [contest.get_text() for contest in contest.select("td")]
        contestData[0] = contestData[0][:-5]
        contestData[1] = contestData[1][3:]
        contestsList.append(contestData)

    # 画像生成
    listFontR = ImageFont.truetype("AtCoder/data/fontR.ttc", 32)
    listFontB = ImageFont.truetype("AtCoder/data/fontB.ttc", 32)
    contestsListFirstImg = Image.open("AtCoder/data/contestsListImg (first).jpg")
    contestsListImg = Image.new("RGB", (1852, 68 + 64 * len(contestsList)))
    contestsListImg.paste(contestsListFirstImg, (0, 0))
    idx = 0
    for contest in contestsList:
        contest[1] = contest[1].replace("◉", "")
        contest[1] = contest[1].replace("\n", "")
        contest[1] = contest[1].replace("\t", "")
        contestListImg = Image.open("AtCoder/data/contestsListImg (cell).jpg")
        contestListDraw = ImageDraw.Draw(contestListImg)
        contestListDraw.text((10, 7), str(contest[0]), fill = (0, 0, 0), font = listFontR)
        if str(contest[3]).find("~ 1999") != -1:
            contestListDraw.text((360, 7), str(contest[1]), fill = (0, 0, 255), font = listFontB)
            contestListDraw.text((1660, 7), str(contest[3]), fill = (0, 0, 255), font = listFontB)
        elif str(contest[3]).find("~ 2799") != -1:
            contestListDraw.text((360, 7), str(contest[1]), fill = (255, 150, 50), font = listFontB)
            contestListDraw.text((1660, 7), str(contest[3]), fill = (255, 150, 50), font = listFontB)
        elif str(contest[3]).find("1200 ~") != -1 or str(contest[3]).find("2000 ~") != -1:
            contestListDraw.text((360, 7), str(contest[1]), fill = (255, 0, 0), font = listFontB)
            contestListDraw.text((1660, 7), str(contest[3]), fill = (255, 0, 0), font = listFontB)
        else:
            contestListDraw.text((360, 7), str(contest[1]), fill = (0, 0, 0), font = listFontR)
            contestListDraw.text((1660, 7), str(contest[3]), fill = (0, 0, 0), font = listFontR)
        contestListDraw.text((1460, 7), str(contest[2]), fill = (0, 0, 0), font = listFontR)
        contestsListImg.paste(contestListImg, (0, 68 + 64 * idx))
        idx = idx + 1

        # メモリ解放
        del contestListImg
        del contestListDraw
        gc.collect()

    contestsListImg.save("AtCoder/contestsListImg_fixed.jpg")

    # リストをツイート
    listTweetText = "現在 " + str(len(contestsList)) + " 件の AtCoder コンテストが予定されています．\nhttps://atcoder.jp/contests/\n"
    api.update_status_with_media(filename = "AtCoder/contestsListImg_fixed.jpg", status = listTweetText + "\n" + timeStamp)
    print("cper_bot-AtCoder-contest: Tweeted contestsListImg_fixed")

    # メモリ解放
    del contestsList
    del listFontR
    del listFontB
    del contestsListFirstImg
    del contestsListImg
    gc.collect()

if __name__ == '__main__':
    print("cper_bot-AtCoder-contest: Running as debug...")
    contest()
    print("cper_bot-AtCoder-contest: Debug finished")
