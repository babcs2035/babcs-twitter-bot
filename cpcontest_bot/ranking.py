# import
import os
import tweepy
import dropbox
import pickle
import datetime
import requests
import urllib
import shutil
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
        shutil.copy("AtCoder/data/default.png", dst_path)
        return
    try:
        with urllib.request.urlopen(url) as web_file, open(dst_path, 'wb') as local_file:
            local_file.write(web_file.read())
    except:
        print("cpcontest_bot-ranking: downloadImage Error (url = " + url + ", dst_path = " + dst_path + ")")

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
    login_info = {
        "name": os.environ["ATCODER_ID"],
        "password" : os.environ["ATCODER_PASSWORD"]
    }
    for contest in contests:

        # コンテスト名を取得
        session = requests.session()
        topHTML = session.post("https://" + str(contest) + ".contest.atcoder.jp/login", data = login_info)
        try:
            topHTML.raise_for_status()
            topData = BeautifulSoup(topHTML.text, "html.parser")
        except:
            print("cpcontest_bot-ranking: topHTML Error (contest = " + contest + ")")
            break
        contestName = str(topData.find("h1", class_ = "site-title").contents[0])[11:-7]

        # 順位表 json データを取得
        session = requests.Session()
        request = session.post("https://" + str(contest) + ".contest.atcoder.jp/standings/json", data = login_info)
        try:
            standingsJsonData = json.loads(request.text)
            print("cpcontest_bot-ranking: Downloaded standingsJsonData")
        except:
            print("cpcontest_bot-ranking: standingsJsonData Error (contest = " + contest + ")")
            break

        newData = {}
        rankNum = 1
        index = 0
        rankTemp = 0
        for rows in standingsJsonData["response"]:
            if "user_screen_name" not in rows:
                index += 1
                continue
            if rankNum > 1:
                if standingsJsonData["response"][index - 1]["penalty"] == standingsJsonData["response"][index]["penalty"] and standingsJsonData["response"][index - 1]["score"] == standingsJsonData["response"][index]["score"]:
                    rankNum -= 1
                    rankTemp += 1
                else:
                    rankNum += rankTemp
                    rankTemp = 0

            if contest in rankings:
                if rows["user_screen_name"] in rankings[contest]:
                    flag = False
                    userTwitterID = ""
                    for atcoderID, twitterID in AtCoderIDs:
                        if atcoderID == rows["user_screen_name"]:
                            flag = True
                            userTwitterID = twitterID
                            break
                    if rankings[contest][rows["user_screen_name"]] > rankNum and (rankNum <= 10 or flag):

                        # ユーザーのアバター画像をダウンロード
                        userpage = requests.get(url = "https://atcoder.jp/users/" + rows["user_screen_name"])
                        try:
                            userpage.raise_for_status()
                            userpageData = BeautifulSoup(userpage.text, "html.parser")
                        except:
                            print("cpcontest_bot-ranking: userpageData Error (user_screen_name = " + rows["user_screen_name"] + ")")
                            continue
                        downloadImage(userpageData.find("img", class_ = "avatar").attrs["src"], "cpcontest_bot/data/" + rows["user_screen_name"] + ".png")

                        # 投稿する画像を作成
                        succeedFlag = True
                        try:
                            font = ImageFont.truetype("cpcontest_bot/data/fontR.ttc", 96)
                            fontB = ImageFont.truetype("cpcontest_bot/data/fontB.ttc", 96)
                            resImg = Image.new("RGB", (1405, 562), (255, 255, 255))
                            resDraw = ImageDraw.Draw(resImg)
                            resImg.paste(Image.open("cpcontest_bot/data/" + rows["user_screen_name"] + ".png").resize((512, 512)), (25, 25))
                            resDraw.text((567, 165), str(rankings[contest][rows["user_screen_name"]]) + " 位 ⇒", fill = (64, 64, 64), font = font)
                            resDraw.text((617, 281), str(rankNum) + " 位 (" + str(int(rankings[contest][rows["user_screen_name"]]) - int(rankNum)) + " 位 UP)", fill = (255, 64, 64), font = fontB)
                            resImg.save("cpcontest_bot/data/resImg.jpg")
                        except:
                            succeedFlag = False

                        # ツイート
                        if flag:
                            if succeedFlag:
                                api.update_with_media(filename = "cpcontest_bot/data/resImg.jpg", status = "〔" + contestName + " 実況〕\n" + rows["user_screen_name"] + " ( @" + userTwitterID + " ) さんが " + str(rankings[contest][rows["user_screen_name"]]) + " 位から " + str(rankNum) + " 位に浮上しました！\nhttps://atcoder.jp/contests/" + contest + "/standings\n" + timeStamp)
                            else:
                                api.update_status("〔" + contestName + " 実況〕\n" + rows["user_screen_name"] + " ( @" + userTwitterID + " ) さんが " + str(rankings[contest][rows["user_screen_name"]]) + " 位から " + str(rankNum) + " 位に浮上しました！\nhttps://atcoder.jp/contests/" + contest + "/standings\n" + timeStamp)
                        else:
                            if succeedFlag:
                                api.update_with_media(filename = "cpcontest_bot/data/resImg.jpg", status = "〔" + contestName + " 実況〕\n" + rows["user_screen_name"] + " さんが " + str(rankings[contest][rows["user_screen_name"]]) + " 位から " + str(rankNum) + " 位に浮上しました！\nhttps://atcoder.jp/contests/" + contest + "/standings\n" + timeStamp)
                            else:
                                api.update_status("〔" + contestName + " 実況〕\n" + rows["user_screen_name"] + " さんが " + str(rankings[contest][rows["user_screen_name"]]) + " 位から " + str(rankNum) + " 位に浮上しました！\nhttps://atcoder.jp/contests/" + contest + "/standings\n" + timeStamp)
                        print("cpcontest_bot-ranking: detected ranking updated (" + rows["user_screen_name"] + ")")
            newData[rows["user_screen_name"]] = rankNum
            rankNum += 1
            index += 1
        newRankings[contest] = newData
    
    rankings = newRankings
    uploadToDropbox()

if __name__ == '__main__':
    print("cpcontest_bot-ranking: Running as debug...")
    ranking(["abc001"])
    print("cpcontest_bot-ranking: Debug finished")
