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

def sec_to_time(sec):
    return str(int(sec / 60)) + ":" + str(int(sec % 60)).zfill(2)

FAFlags = {}
rankings = {}
AtCoderIDs = []
scores = {}

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global FAFlags
    global rankings
    global AtCoderIDs
    global scores

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # FAFlags をダウンロード
    dbx.files_download_to_file("cpcontest_bot/FAFlags.txt", "/cpcontest_bot/FAFlags.txt")
    with open("cpcontest_bot/FAFlags.txt", "rb") as f:
        FAFlags = pickle.load(f)
    print("cpcontest_bot-FA: Downloaded FAFlags (size : ", str(len(FAFlags)), ")")

    # rankings をダウンロード
    dbx.files_download_to_file("cpcontest_bot/rankings.txt", "/cpcontest_bot/rankings.txt")
    with open("cpcontest_bot/rankings.txt", "rb") as f:
        rankings = pickle.load(f)
    print("cpcontest_bot-ranking: Downloaded rankings (size : ", str(len(rankings)), ")")

    # scores をダウンロード
    dbx.files_download_to_file("cpcontest_bot/scores.txt", "/cpcontest_bot/scores.txt")
    with open("cpcontest_bot/scores.txt", "rb") as f:
        scores = pickle.load(f)
    print("cpcontest_bot-updateHighestScore: Downloaded scores (size : ", str(len(scores)), ")")

    # AtCoderIDs をダウンロード
    dbx.files_download_to_file("cpcontest_bot/AtCoderIDs.txt", "/cpcontest_bot/AtCoderIDs.txt")
    with open("cpcontest_bot/AtCoderIDs.txt", "rb") as f:
        AtCoderIDs = pickle.load(f)
    print("cpcontest_bot-ranking: Downloaded AtCoderIDs (size : ", str(len(AtCoderIDs)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global FAFlags
    global rankings
    global scores

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # FAFlags をアップロード
    with open("cpcontest_bot/FAFlags.txt", "wb") as f:
        pickle.dump(FAFlags, f)
    with open("cpcontest_bot/FAFlags.txt", "rb") as f:
        dbx.files_upload(f.read(), "/cpcontest_bot/FAFlags.txt", mode = dropbox.files.WriteMode.overwrite)
    print("cpcontest_bot-FA: Uploaded FAFlags (size : ", str(len(FAFlags)), ")")

    # rankings をアップロード
    with open("cpcontest_bot/rankings.txt", "wb") as f:
        pickle.dump(rankings, f)
    with open("cpcontest_bot/rankings.txt", "rb") as f:
        dbx.files_upload(f.read(), "/cpcontest_bot/rankings.txt", mode = dropbox.files.WriteMode.overwrite)
    print("cpcontest_bot-ranking: Uploaded rankings (size : ", str(len(rankings)), ")")

    # scores をアップロード
    with open("cpcontest_bot/scores.txt", "wb") as f:
        pickle.dump(scores, f)
    with open("cpcontest_bot/scores.txt", "rb") as f:
        dbx.files_upload(f.read(), "/cpcontest_bot/scores.txt", mode = dropbox.files.WriteMode.overwrite)
    print("cpcontest_bot-updateHighestScore: Uploaded scores (size : ", str(len(scores)), ")")

def downloadImage(url, dst_path):
    if url[0] != 'h':
        shutil.copy("AtCoder/data/default.png", dst_path)
        return
    try:
        with urllib.request.urlopen(url) as web_file, open(dst_path, 'wb') as local_file:
            local_file.write(web_file.read())
    except:
        print("cpcontest_bot-ranking: downloadImage Error (url = " + url + ", dst_path = " + dst_path + ")")

def cpcontest(contests):

    global FAFlags
    global rankings
    global AtCoderIDs
    global scores

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
    
    # ログイン
    session = requests.Session()
    loginHTML = session.get("https://atcoder.jp/login")
    loginHTML.raise_for_status()
    loginData = BeautifulSoup(loginHTML.text, "html.parser")
    payload = {
        "username" : os.environ["ATCODER_ID"],
        "password" : os.environ["ATCODER_PASSWORD"]
    }
    payload["csrf_token"] = loginData.find(attrs = { "name" : "csrf_token" }).get("value")
    session.post("https://atcoder.jp/login", data = payload)

    newRankings = {}
    for contest in contests:

        # チーム戦かどうか判定
        teamFlag = False
        if contest[-5:] == "_team":
            teamFlag = True
            contest = contest.replace("_team", "")

        # コンテスト名を取得
        topHTML = session.get("https://atcoder.jp/contests/" + str(contest))
        try:
            topHTML.raise_for_status()
            topData = BeautifulSoup(topHTML.text, "html.parser")
        except:
            print("cpcontest_bot-FA: topHTML Error")
            break
        contestName = str(topData.contents[3].contents[1].contents[1].contents[0])[0:-10]


        # 順位表 json データを取得
        request = session.get(url = "https://atcoder.jp/contests/" + str(contest) + "/standings" + ("/team" if teamFlag else "") + "/json")
        try:
            standingsJsonData = json.loads(request.text)
            print("cpcontest_bot-FA: Downloaded standingsJsonData")
        except:
            print("cpcontest_bot-FA: standingsJsonData Error")
            break

        # 順位表から最高得点を見つける
        for task in standingsJsonData["TaskInfo"]:
            if task["TaskScreenName"] + ("_team" if teamFlag else "") not in scores:
                scores[task["TaskScreenName"] + ("_team" if teamFlag else "")] = 0
        taskIndex = 0
        for task in standingsJsonData["TaskInfo"]:
            maxScore = -1
            minTime = "-1"
            maxUser = ""
            isUserTeam = False
            taskID = contest + "_" + chr(ord('a') + taskIndex)
            for rows in standingsJsonData["StandingsData"]:
                if taskID not in rows["TaskResults"]:
                    continue
                if rows["TaskResults"][taskID]["Score"] == 0:
                    continue
                userScore = int(rows["TaskResults"][taskID]["Score"])
                userTime = str(rows["TaskResults"][taskID]["Elapsed"])
                if userScore > maxScore or ((maxScore == -1 or userScore >= maxScore) and userScore > 0 and (minTime == "-1" or int(userTime) < int(minTime))):
                    maxScore = userScore
                    minTime = userTime
                    maxUser = str(rows["UserScreenName"])
                    isUserTeam = rows["IsTeam"]
            if maxScore > scores[task["TaskScreenName"] + ("_team" if teamFlag else "")]:
                flag = False
                userTwitterID = ""
                for atcoderID, twitterID in AtCoderIDs:
                    if atcoderID == maxUser:
                        flag = True
                        userTwitterID = twitterID
                        break
                scores[task["TaskScreenName"] + ("_team" if teamFlag else "")] = maxScore
                assign = chr(ord('A') + taskIndex)
                maxScore /= 100
                minTime = int(minTime) / 1000000000
                minTime = sec_to_time(int(minTime))
                if isUserTeam:
                    maxUser = "チーム「" + maxUser + "」"
                else:
                    maxUser = maxUser + (" ( @" + userTwitterID + " ) " if flag else " ")
                api.update_status("〔" + contestName + ("（チーム戦）" if teamFlag else "") + " 実況〕\n" + maxUser + "さんが " + assign + " 問題で " + str(maxScore) + " 点を " + minTime + " に獲得し，最高得点を更新しました！\nhttps://atcoder.jp/contests/" + contest + "/standings\n" + timeStamp)
                print("cpcontest_bot-updateHighestScore: detected " + str(task["TaskScreenName"] + ("_team" if teamFlag else "")) + " updated the highest score (" + maxUser + ")")
            taskIndex += 1

        # 順位表から FA を見つける
        for task in standingsJsonData["TaskInfo"]:
            if task["TaskScreenName"] + ("_team" if teamFlag else "") not in FAFlags:
                FAFlags[task["TaskScreenName"] + ("_team" if teamFlag else "")] = False
        for task in standingsJsonData["TaskInfo"]:
            if FAFlags[task["TaskScreenName"] + ("_team" if teamFlag else "")]:
                continue
            minTime = -1
            minUser = ""
            isUserTeam = False
            for rows in standingsJsonData["StandingsData"]:
                if task["TaskScreenName"] not in rows["TaskResults"]:
                    continue
                userTime = int(rows["TaskResults"][task["TaskScreenName"]]["Elapsed"])
                if (minTime == -1 or userTime < minTime) and userTime > 0 and rows["TaskResults"][task["TaskScreenName"]]["Status"] == 1:
                    minTime = int(rows["TaskResults"][task["TaskScreenName"]]["Elapsed"])
                    minUser = str(rows["UserScreenName"])
                    isUserTeam = rows["IsTeam"]
            if minTime != -1:
                FAFlags[task["TaskScreenName"] + ("_team" if teamFlag else "")] = True
                flag = False
                userTwitterID = ""
                for atcoderID, twitterID in AtCoderIDs:
                    if atcoderID == maxUser:
                        flag = True
                        userTwitterID = twitterID
                        break
                minTime /= 1000000000
                if isUserTeam:
                    minUser = "チーム「" + minUser + "」"
                else:
                    minUser = " " + minUser + (" ( @" + userTwitterID + " ) " if flag else " ")
                api.update_status("〔" + contestName + ("（チーム戦）" if teamFlag else "") + " 実況〕\n" + task["Assignment"] + " 問題の FA を " + str(sec_to_time(minTime)) + " で" + minUser + "さんが獲得しました！\nhttps://atcoder.jp/contests/" + contest + "/standings\n" + timeStamp)
                print("cpcontest_bot-FA: detected " + str(task["TaskScreenName"] + ("_team" if teamFlag else "")) + " FA (" + minUser + ")")

        # 順位表から順位の浮上を見つける
        newData = {}
        for rows in standingsJsonData["StandingsData"]:
            if contest + ("_team" if teamFlag else "") in rankings:
                if "Rank" in rows:
                    rankNum = int(rows["Rank"])
                    newData[rows["UserScreenName"]] = rankNum
                if rows["UserScreenName"] in rankings[contest + ("_team" if teamFlag else "")]:
                    flag = False
                    userTwitterID = ""
                    for atcoderID, twitterID in AtCoderIDs:
                        if atcoderID == rows["UserScreenName"]:
                            flag = True
                            userTwitterID = twitterID
                            break
                    if rankings[contest + ("_team" if teamFlag else "")][rows["UserScreenName"]] > rankNum and (rankNum <= 10 or flag):

                        # ユーザーのアバター画像をダウンロード
                        userpage = requests.get(url = "https://atcoder.jp/users/" + rows["UserScreenName"])
                        try:
                            userpage.raise_for_status()
                            userpageData = BeautifulSoup(userpage.text, "html.parser")
                        except:
                            print("cpcontest_bot-ranking: userpageData Error (user_screen_name = " + rows["UserScreenName"] + ")")
                        
                        # 投稿する画像を作成
                        succeedFlag = True
                        try:
                            downloadImage(("aaa" if rows["IsTeam"] else userpageData.find("img", class_ = "avatar").attrs["src"]), "cpcontest_bot/data/" + rows["UserScreenName"] + ".png")
                            font = ImageFont.truetype("cpcontest_bot/data/fontR.ttc", 96)
                            fontB = ImageFont.truetype("cpcontest_bot/data/fontB.ttc", 96)
                            resImg = Image.new("RGB", (1405, 562), (255, 255, 255))
                            resDraw = ImageDraw.Draw(resImg)
                            resImg.paste(Image.open("cpcontest_bot/data/" + rows["UserScreenName"] + ".png").resize((512, 512)), (25, 25))
                            resDraw.text((567, 165), str(rankings[contest + ("_team" if teamFlag else "")][rows["UserScreenName"]]) + " 位 ⇒", fill = (64, 64, 64), font = font)
                            resDraw.text((617, 281), str(rankNum) + " 位 (" + str(int(rankings[contest + ("_team" if teamFlag else "")][rows["UserScreenName"]]) - int(rankNum)) + " 位 UP)", fill = (255, 64, 64), font = fontB)
                            resImg.save("cpcontest_bot/data/resImg.jpg")
                        except:
                            succeedFlag = False

                        # ツイート
                        userName = rows["UserScreenName"]
                        if rows["IsTeam"]:
                            userName = "チーム「" + userName + "」"
                        else:
                            userName = userName + (" ( @" + userTwitterID + " ) " if flag else " ")
                        if succeedFlag:
                            api.update_with_media(filename = "cpcontest_bot/data/resImg.jpg", status = "〔" + contestName + ("（チーム戦）" if teamFlag else "") + " 実況〕\n" + userName + "さんが " + str(rankings[contest + ("_team" if teamFlag else "")][rows["UserScreenName"]]) + " 位から " + str(rankNum) + " 位に浮上しました！\nhttps://atcoder.jp/contests/" + contest + "/standings\n" + timeStamp)
                        else:
                            api.update_status("〔" + contestName + ("（チーム戦）" if teamFlag else "") + " 実況〕\n" + userName + "さんが " + str(rankings[contest + ("_team" if teamFlag else "")][rows["UserScreenName"]]) + " 位から " + str(rankNum) + " 位に浮上しました！\nhttps://atcoder.jp/contests/" + contest + "/standings\n" + timeStamp)
                        print("cpcontest_bot-ranking: detected ranking updated (" + rows["UserScreenName"] + ("_team" if teamFlag else "") + ")")
        newRankings[contest + ("_team" if teamFlag else "")] = newData

    rankings = newRankings
    uploadToDropbox()
