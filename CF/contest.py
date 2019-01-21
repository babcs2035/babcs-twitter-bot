# import
import os
import tweepy
import datetime
import time
import dropbox
import urllib
import requests
import json
from PIL import Image, ImageDraw, ImageFont
from dateutil.relativedelta import relativedelta

def epoch_to_datetime(epoch):
    return datetime.datetime(*time.localtime(epoch)[:6])

def sec_to_time(sec):
    return "{0.hours:02}:{0.minutes:02}".format(relativedelta(seconds=sec))

# Dropbox にアップロード
def uploadToDropbox():

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # contestsListImg_fixed をアップロード
    with open("CF/data/contest/contestsListImg_fixed.jpg", "rb") as f:
        dbx.files_upload(f.read(), "/_backup/CF/contestsListImg_fixed/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".jpg")
        print("CF-contest: Uploaded contestsListImg_fixed")

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

    # 画像生成
    listFont = ImageFont.truetype("CF/data/YuGothM.ttc", 32)
    contestsListFirstImg = Image.open("CF/data/contest/contestsListImg (first).jpg")
    contestsListImg = Image.new("RGB", (1852, 68 + 64 * len(contestsList)))
    contestsListImg.paste(contestsListFirstImg, (0, 0))
    idx = 0
    for contest in contestsList:
        contestListImg = Image.open("CF/data/contest/contestsListImg (cell).jpg")
        contestListDraw = ImageDraw.Draw(contestListImg)
        contestListDraw.text((10, 15), str(epoch_to_datetime(contest["startTimeSeconds"])), fill = (0, 0, 0), font = listFont)
        contestListDraw.text((360, 15), str(contest["name"]), fill = (0, 0, 0), font = listFont)
        contestListDraw.text((1460, 15), str(sec_to_time(contest["durationSeconds"])), fill = (0, 0, 0), font = listFont)
        contestListDraw.text((1660, 15), str(contest["type"]), fill = (0, 0, 0), font = listFont)
        contestsListImg.paste(contestListImg, (0, 68 + 64 * idx))
        idx = idx + 1
    contestsListImg.save("CF/data/contest/contestsListImg_fixed.jpg")

    # リストをツイート
    listTweetText = "現在，" + str(idx) + " の Codeforces コンテストが予定されています．\nhttps://codeforces.com/contests\n"
    api.update_with_media(filename = "CF/data/contest/contestsListImg_fixed.jpg", status = listTweetText + "\n" + timeStamp)

    # 画像をアップロード
    uploadToDropbox()

if __name__ == '__main__':
    print("CF-contest: Running as debug...")
    contest()
    print("CF-contest: Debug finished")
