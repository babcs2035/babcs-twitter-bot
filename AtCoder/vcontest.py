# import
import os
import tweepy
import datetime
import time
import dropbox
import urllib
from bs4 import BeautifulSoup
import requests
from PIL import Image, ImageDraw, ImageFont

# Dropbox にアップロード
def uploadToDropbox():

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # vcontestsListImg_fixed をアップロード
    with open("AtCoder/data/vcontest/vcontestsListImg_fixed.jpg", "rb") as f:
        dbx.files_upload(f.read(), "/_backup/AtCoder/vcontestsListImg_fixed/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".jpg")
        print("AtCoder-vcontest: Uploaded vcontestsListImg_fixed")

def vcontest():
    
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
    listURL = "https://not-522.appspot.com/"
    listHTML = requests.get(listURL)
    listHTML.raise_for_status()
    listData = BeautifulSoup(listHTML.text, "html.parser")
    listTable = listData.find_all("tbody")
    listRows = listTable[0].find_all("tr")
    listRows += listTable[1].find_all("tr")
    vcontestsList = []
    for detail in listRows[0].find_all("a"):
        name = str(detail.contents[0])
        beginTime = str(detail.parent.contents[2].contents[0])
        endTime = str(detail.parent.contents[2].contents[1].contents[0])
        endTime_formatted = datetime.datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S\n        ")
        if endTime_formatted < datetime.datetime.today():
           continue
        vcontestsList.append(({"name" : name, "beginTime" : beginTime, "endTime" : endTime}))
    for detail in listRows[len(vcontestsList)].find_all("a"):
        name = str(detail.contents[0])
        beginTime = str(detail.parent.contents[2].contents[0])
        endTime = str(detail.parent.contents[2].contents[1].contents[0])
        endTime_formatted = datetime.datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S\n        ")
        if endTime_formatted < datetime.datetime.today():
           continue
        vcontestsList.append(({"name" : name, "beginTime" : beginTime, "endTime" : endTime}))

    # 画像生成
    listFont = ImageFont.truetype("AtCoder/data/YuGothM.ttc", 32)
    vcontestsListFirstImg = Image.open("AtCoder/data/vcontest/vcontestsListImg (first).jpg")
    vcontestsListImg = Image.new("RGB", (1772, 68 + 64 * len(vcontestsList)))
    vcontestsListImg.paste(vcontestsListFirstImg, (0, 0))
    idx = 0
    for vcontest in vcontestsList:
        vcontestListImg = Image.open("AtCoder/data/vcontest/vcontestsListImg (cell).jpg")
        vcontestListDraw = ImageDraw.Draw(vcontestListImg)
        vcontestListDraw.text((10, 15), str(vcontest["beginTime"]), fill = (0, 0, 0), font = listFont)
        vcontestListDraw.text((360, 15), str(vcontest["endTime"]), fill = (0, 0, 0), font = listFont)
        vcontestListDraw.text((710, 15), str(vcontest["name"]), fill = (0, 0, 0), font = listFont)
        vcontestsListImg.paste(vcontestListImg, (0, 68 + 64 * idx))
        idx = idx + 1
    vcontestsListImg.save("AtCoder/data/vcontest/vcontestsListImg_fixed.jpg")

    # リストをツイート
    listTweetText = "現在，" + str(idx) + " の AtCoder バーチャルコンテストが行われて or 予定されています．\nhttps://not-522.appspot.com/\n"
    api.update_with_media(filename = "AtCoder/data/vcontest/vcontestsListImg_fixed.jpg", status = listTweetText + "\n" + timeStamp)

    # 画像をアップロード
    uploadToDropbox()

if __name__ == '__main__':
    print("AtCoder-vcontest: Running as debug...")
    vcontest()
    print("AtCoder-vcontest: Debug finished")
