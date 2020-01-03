# import
import os
import tweepy
import dropbox
import pickle
import datetime
import requests
import urllib
from bs4 import BeautifulSoup
import json
from PIL import Image, ImageDraw, ImageFont

rankings = {}
AtCoderIDs = []

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global rankings
    global AtCoderIDs

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # rankings をダウンロード
    dbx.files_download_to_file("cpcontest_bot/rankings.txt", "/cpcontest_bot/rankings.txt")
    dbx.files_delete("/cpcontest_bot/rankings.txt")
    with open("cpcontest_bot/rankings.txt", "rb") as f:
        rankings = pickle.load(f)
    print("cpcontest_bot-ranking: Downloaded rankings (size : ", str(len(rankings)), ")")

    # AtCoderIDs をダウンロード
    dbx.files_download_to_file("cpcontest_bot/AtCoderIDs.txt", "/cpcontest_bot/AtCoderIDs.txt")
    with open("cpcontest_bot/AtCoderIDs.txt", "rb") as f:
        AtCoderIDs = pickle.load(f)
    print("cpcontest_bot-ranking: Downloaded AtCoderIDs (size : ", str(len(AtCoderIDs)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global rankings

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # rankings をアップロード
    with open("cpcontest_bot/rankings.txt", "wb") as f:
        pickle.dump(rankings, f)
    with open("cpcontest_bot/rankings.txt", "rb") as f:
        dbx.files_upload(f.read(), "/cpcontest_bot/rankings.txt")
    print("cpcontest_bot-ranking: Uploaded rankings (size : ", str(len(rankings)), ")")

def downloadImage(url, dst_path):
    if url[0] != 'h':
        url = "https:" + url
    try:
        with urllib.request.urlopen(url) as web_file, open(dst_path, 'wb') as local_file:
            local_file.write(web_file.read())
    except:
        print("cpcontest_bot-results: downloadImage Error (url = " + url + ", dst_path = " + dst_path + ")")

def ranking(contests):

    global rankings
    global AtCoderIDs

    # 各種キー設定
    CK = os.environ["CONSUMER_KEY2"]
    CS = os.environ["CONSUMER_SECRET2"]
    AT = os.environ["ACCESS_TOKEN_KEY2"]
    AS = os.environ["ACCESS_TOKEN_SECRET2"]
    
    # Twitter オブジェクトの生成
    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    api = tweepy.API(auth)

    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))

    downloadFromDropbox()

    # 順位表から順位の浮上を見つける
    newRankings = {}
    for contest in contests:

        # コンテスト名を取得
        topHTML = requests.get("https://atcoder.jp/contests/" + str(contest))
        try:
            topHTML.raise_for_status()
            topData = BeautifulSoup(topHTML.text, "html.parser")
        except:
            print("cpcontest_bot-ranking: topHTML Error (contest = " + contest + ")")
            break
        contestName = str(topData.contents[3].contents[1].contents[1].contents[0])[0:-10]

        # 順位表 json データを取得
        session = requests.Session()
        request = session.get(url = "https://atcoder.jp/contests/" + str(contest) + "/standings/json")
        try:
            standingsJsonData = json.loads(request.text)
            print("cpcontest_bot-ranking: Downloaded standingsJsonData")
        except:
            print("cpcontest_bot-ranking: standingsJsonData Error (contest = " + contest + ")")
            break

        newData = {}
        for rows in standingsJsonData["StandingsData"]:
            if contest in rankings:
                if rows["UserScreenName"] in rankings[contest]:
                    flag = False
                    userTwitterID = ""
                    for atcoderID, twitterID in AtCoderIDs:
                        if atcoderID == rows["UserScreenName"]:
                            flag = True
                            userTwitterID = twitterID
                            break
                    if rankings[contest][rows["UserScreenName"]] > rows["Rank"]:

                        # ユーザーのアバター画像をダウンロード
                        userpage = requests.get(url = "https://atcoder.jp/users/" + rows["UserScreenName"])
                        try:
                            userpage.raise_for_status()
                            userpageData = BeautifulSoup(userpage.text, "html.parser")
                        except:
                            print("cpcontest_bot-ranking: userpageData Error (UserScreenName = " + rows["UserScreenName"] + ")")
                            continue
                        downloadImage(userpageData.find("img", class_ = "avatar").attrs["src"], "cpcontest_bot/imgs/" + rows["UserScreenName"] + ".png")

                        # 投稿する画像を作成
                        succeedFlag = True
                        try:
                            font = ImageFont.truetype("AtCoder/data/fontR.ttc", 96)
                            fontB = ImageFont.truetype("AtCoder/data/fontB.ttc", 96)
                            resImg = Image.new("RGB", (1405, 562), (255, 255, 255))
                            resDraw = ImageDraw.Draw(resImg)
                            resImg.paste(Image.open("cpcontest_bot/imgs/" + rows["UserScreenName"] + ".png").resize((512, 512)), (25, 25))
                            resDraw.text((567, 165), str(rankings[contest][rows["UserScreenName"]]) + " 位 ⇒", fill = (64, 64, 64), font = font)
                            resDraw.text((617, 281), str(rows["Rank"]) + " 位 (" + str(int(rankings[contest][rows["UserScreenName"]]) - int(rows["Rank"])) + " 位 UP)", fill = (255, 64, 64), font = fontB)
                            resImg.save("cpcontest_bot/imgs/resImg.jpg")
                        except:
                            succeedFlag = False

                        # ツイート
                        if flag:
                            if succeedFlag:
                                api.update_with_media(filename = "cpcontest_bot/imgs/resImg.jpg", status = "〔" + contestName + " 実況〕\n" + rows["UserScreenName"] + " ( @" + userTwitterID + " ) さんが " + str(rankings[contest][rows["UserScreenName"]]) + " 位から " + str(rows["Rank"]) + " 位に浮上しました！\nhttps://atcoder.jp/contests/" + contest + "/standings\n" + timeStamp)
                            else:
                                api.update_status("〔" + contestName + " 実況〕\n" + rows["UserScreenName"] + " ( @" + userTwitterID + " ) さんが " + str(rankings[contest][rows["UserScreenName"]]) + " 位から " + str(rows["Rank"]) + " 位に浮上しました！\nhttps://atcoder.jp/contests/" + contest + "/standings\n" + timeStamp)
                        elif rows["Rank"] <= 10:
                            if succeedFlag:
                                api.update_with_media(filename = "cpcontest_bot/imgs/resImg.jpg", status = "〔" + contestName + " 実況〕\n" + rows["UserScreenName"] + " さんが " + str(rankings[contest][rows["UserScreenName"]]) + " 位から " + str(rows["Rank"]) + " 位に浮上しました！\nhttps://atcoder.jp/contests/" + contest + "/standings\n" + timeStamp)
                            else:
                                api.update_status("〔" + contestName + " 実況〕\n" + rows["UserScreenName"] + " さんが " + str(rankings[contest][rows["UserScreenName"]]) + " 位から " + str(rows["Rank"]) + " 位に浮上しました！\nhttps://atcoder.jp/contests/" + contest + "/standings\n" + timeStamp)
                        print("cpcontest_bot-ranking: detected ranking updated (" + rows["UserScreenName"] + ")")
            newData[rows["UserScreenName"]] = rows["Rank"]
        newRankings[contest] = newData
    
    rankings = newRankings
    uploadToDropbox()

if __name__ == '__main__':
    print("cpcontest_bot-ranking: Running as debug...")
    ranking(["abc001"])
    print("cpcontest_bot-ranking: Debug finished")
