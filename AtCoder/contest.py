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

def isSponseredContest(str):
    return (str.find("（") != -1 or str.find("(") != -1)

def contest():
    
    # Create Twitter Object
    auth = tweepy.OAuthHandler(os.environ["CONSUMER_KEY"], os.environ["CONSUMER_SECRET"])
    auth.set_access_token(os.environ["ACCESS_TOKEN_KEY"], os.environ["ACCESS_TOKEN_SECRET"])
    api = tweepy.API(auth)

    # Create time stamp
    timeStamp = str(datetime.datetime.today().strftime("%Y/%m/%d %H:%M"))

    # Get Upcoming contests list
    contestsHTML = requests.get("https://atcoder.jp/contests/?lang=ja")
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

    # Analyze list
    contestsRows = contestsTable[1].find_all("tr")    
    del contestsRows[0]
    contestsList = []
    sponseredContestsCnt = 0
    for contest in contestsRows:
        contestData = [contest.get_text() for contest in contest.select("td")]
        contestData[0] = contestData[0][:-5]
        contestData[1] = contestData[1].replace("◉", "")
        contestData[1] = contestData[1].replace("\n", "")
        contestData[1] = contestData[1].replace("\t", "")
        contestData[1] = contestData[1][0:1] + " " + contestData[1][1:]
        contestData[1] = contestData[1].replace("（", "\n   （")
        contestData[1] = contestData[1].replace("(", "\n      (")
        contestData.append(isSponseredContest(contestData[1]))
        contestsList.append(contestData)
        sponseredContestsCnt += contestData[4]

    # Generate image
    listFontR = ImageFont.truetype("fontR.ttc", 32)
    listFontB = ImageFont.truetype("fontB.ttc", 32)
    contestsListTitleImg = Image.open("AtCoder/data/contestsListImg (title).jpg")
    contestsListImg = Image.new("RGB", (1852, 68 + 64 * (len(contestsList) + sponseredContestsCnt)))
    contestsListImg.paste(contestsListTitleImg, (0, 0))
    idx = 0
    for contest in contestsList:
        imgPath = "AtCoder/data/contestsListImg (normal).jpg"
        if contest[4]:
            imgPath = "AtCoder/data/contestsListImg (sponsered).jpg"
        contestListImg = Image.open(imgPath)
        contestListDraw = ImageDraw.Draw(contestListImg)
        contestListDraw.text((10, 7 + 32 * contest[4]), str(contest[0]), fill = (0, 0, 0), font = listFontR)
        specialFontColor = (0, 0, 0)
        if str(contest[3]).find("~ 1999") != -1:
            specialFontColor = (0, 0, 255)
        elif str(contest[3]).find("~ 2799") != -1:
            specialFontColor = (255, 150, 50)
        elif str(contest[3]).find("1200 ~") != -1 or str(contest[3]).find("2000 ~") != -1:
            specialFontColor = (255, 0, 0)
        contestListDraw.text((360, 7 + 7 * contest[4]), str(contest[1]), fill = specialFontColor, font = listFontB)
        contestListDraw.text((1460, 7 + 32 * contest[4]), str(contest[2]), fill = (0, 0, 0), font = listFontR)
        contestListDraw.text((1660, 7 + 32 * contest[4]), str(contest[3]), fill = specialFontColor, font = listFontB)
        contestsListImg.paste(contestListImg, (0, 68 + 64 * idx))
        idx += (1 + contest[4])

        # Release memory
        del contestListImg
        del contestListDraw
        gc.collect()

    contestsListImg.save("AtCoder/contestsListImg_fixed.jpg")

    # Tweet
    listTweetText = "現在 " + str(len(contestsList)) + " 件の AtCoder コンテストが予定されています．\nhttps://atcoder.jp/contests/\n"
    api.update_status_with_media(filename = "AtCoder/contestsListImg_fixed.jpg", status = listTweetText + "\n" + timeStamp)
    print("cper_bot-AtCoder-contest: Tweeted contestsListImg_fixed")

    # Release memory
    del contestsList
    del listFontR
    del listFontB
    del contestsListTitleImg
    del contestsListImg
    gc.collect()

if __name__ == '__main__':
    print("cper_bot-AtCoder-contest: Running as debug...")
    contest()
    print("cper_bot-AtCoder-contest: Debug finished")
