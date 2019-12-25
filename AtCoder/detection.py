# import
import os
import tweepy
import datetime
import time
import dropbox
import requests
import pickle
import json
from bs4 import BeautifulSoup

# グローバル変数
AtCoderIDs = []
lastSubID_All = {}
lastSubID_Recent = {}
noticeFlag = {}

# Dropbox からダウンロード
# type = 0 : all
# type = 1 : recent only
# type = 2 : noticeFlag only
def downloadFromDropbox(type):
    
    # グローバル変数
    global AtCoderIDs
    global lastSubID_All
    global lastSubID_Recent
    global noticeFlag

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # AtCoderIDs をダウンロード
    dbx.files_download_to_file("AtCoder/AtCoderIDs.txt", "/AtCoder/AtCoderIDs.txt")
    with open("AtCoder/AtCoderIDs.txt", "rb") as f:
        AtCoderIDs = pickle.load(f)
    print("cper_bot-AtCoder-detection: Downloaded AtCoderIDs (size : ", str(len(AtCoderIDs)), ")")

    if type == 0:
        
        # lastSubID をダウンロード
        dbx.files_download_to_file("AtCoder/lastSubID.txt", "/AtCoder/lastSubID.txt")
        dbx.files_delete("/AtCoder/lastSubID.txt")
        with open("AtCoder/lastSubID.txt", "rb") as f:
            lastSubID_All = pickle.load(f)
        print("cper_bot-AtCoder-detection: Downloaded lastSubID (size : ", str(len(lastSubID_All)), ")")

    if type == 1:
        
        # lastSubID_recent をダウンロード
        dbx.files_download_to_file("AtCoder/lastSubID_recent.txt", "/AtCoder/lastSubID_recent.txt")
        dbx.files_delete("/AtCoder/lastSubID_recent.txt")
        with open("AtCoder/lastSubID_recent.txt", "rb") as f:
            lastSubID_Recent = pickle.load(f)
        print("cper_bot-AtCoder-detection: Downloaded lastSubID_recent (size : ", str(len(lastSubID_Recent)), ")")
    
    # noticeFlag をダウンロード
    dbx.files_download_to_file("AtCoder/noticeFlag.txt", "/AtCoder/noticeFlag.txt")
    with open("AtCoder/noticeFlag.txt", "rb") as f:
        noticeFlag = pickle.load(f)
    print("cper_bot-AtCoder-detection: Downloaded noticeFlag (size : ", str(len(noticeFlag)), ")")

# Dropbox にアップロード
# type = 0 : all
# type = 1 : recent only
# type = 2 : noticeFlag only
def uploadToDropbox(type):
    
    # グローバル変数
    global lastSubID_All
    global lastSubID_Recent
    global noticeFlag

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    if type == 0:

        # lastSubID をアップロード
        with open("AtCoder/lastSubID.txt", "wb") as f:
            pickle.dump(lastSubID_All, f)
        with open("AtCoder/lastSubID.txt", "rb") as f:
            dbx.files_upload(f.read(), "/AtCoder/lastSubID.txt")
        print("cper_bot-AtCoder-detection: Uploaded lastSubID (size : ", str(len(lastSubID_All)), ")")

    if type == 1:

        # lastSubID_recent をアップロード
        with open("AtCoder/lastSubID_recent.txt", "wb") as f:
            pickle.dump(lastSubID_Recent, f)
        with open("AtCoder/lastSubID_recent.txt", "rb") as f:
            dbx.files_upload(f.read(), "/AtCoder/lastSubID_recent.txt")
        print("cper_bot-AtCoder-detection: Uploaded lastSubID_recent (size : ", str(len(lastSubID_Recent)), ")")

    if type == 2:

        # noticeFlag をアップロード
        with open("AtCoder/noticeFlag.txt", "wb") as f:
            pickle.dump(noticeFlag, f)
        with open("AtCoder/noticeFlag.txt", "rb") as f:
            dbx.files_delete("/AtCoder/noticeFlag.txt")
            dbx.files_upload(f.read(), "/AtCoder/noticeFlag.txt")
        print("cper_bot-AtCoder-detection: Uploaded noticeFlag (size : ", str(len(noticeFlag)), ")")

# 通知の on/off 切り替え
def setFlag(atcoderID, twitterID, f):

    # グローバル変数
    global AtCoderIDs
    global noticeFlag

    downloadFromDropbox(2)

    if (atcoderID, twitterID) in AtCoderIDs and (f == "on" or f == "off"): 
        noticeFlag[str(atcoderID)] = str(f)
        uploadToDropbox(2)
        return "AtCoder での AC 通知を " + str(f) + " にしました！\n"
    else:
        return "この AtCoder ID が登録されていないか，無効な引数が与えられました！\n"

def epoch_to_datetime(epoch):
    return datetime.datetime(*time.localtime(epoch)[:6])

# type = 0 : all
# type = 1 : recent only
def detection(type):
    
    # グローバル変数
    global AtCoderIDs
    global lastSubID_All
    global lastSubID_Recent
    
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
    
    # データをダウンロード
    downloadFromDropbox(type)
    lastSubID = {}
    if type == 0:
        lastSubID = lastSubID_All
    if type == 1:
        lastSubID = lastSubID_Recent

    # コンテストごとに提出を解析
    session = requests.Session()
    request = session.get(url = "https://atcoder-api.appspot.com/contests")
    contestsJsonData = json.loads(request.text)
    print("cper_bot-AtCoder-detection: Downloaded contestsJsonData")
    
    checkContests = []
    border = datetime.datetime.today() - datetime.timedelta(14)
    for contest in contestsJsonData:
        date = epoch_to_datetime(contest["startTimeSeconds"] + contest["durationSeconds"])
        contest["title"] = contest["title"].replace("◉", "")
        contest["title"] = contest["title"].replace("\n", "")
        contest["title"] = contest["title"].replace("\t", "")
        if type == 0:
            if date < border:
                checkContests.append(contest)
        if type == 1:
            if border <= date and date <= datetime.datetime.today():
                checkContests.append(contest)

    newLastSubID = {}
    for contest in checkContests:

        # ページ送り
        sublistPageNum = 1
        subCount = 0
        newLastSubID[str(contest["id"])] = -1

        while True:
            sublistURL = "https://atcoder.jp/contests/" + str(contest["id"]) + "/submissions?page=" + str(sublistPageNum)
            sublistHTML = requests.get(sublistURL)
            try:
                sublistHTML.raise_for_status()
                sublistData = BeautifulSoup(sublistHTML.text, "html.parser")
            except:
                print("cper_bot-AtCoder-detection: sublistHTML Error")
                break
            sublistTable = sublistData.find_all("table", class_ = "table table-bordered table-striped small th-center")
            if len(sublistTable) == 0:
                break

            # １行ずつ解析
            sublistRows = sublistTable[0].find_all("tr")
            del sublistRows[0]
            skipFlag = False
            for row in sublistRows:

                subData = [cell.get_text() for cell in row.select("td")]
                if subData[6] == "WJ" or ('0' <= subData[6][0] and subData[6][0] <= '9'):
                    continue

                links = row.find_all("a")
                subID = int(str(links[3].get("href")).split("/")[4])
                userID = str(links[1].get("href")).split("/")[2]
                if newLastSubID[str(contest["id"])] == -1:
                    newLastSubID[str(contest["id"])] = subID
                if str(contest["id"]) not in lastSubID:
                    skipFlag = True
                    break
                if subID <= int(lastSubID[str(contest["id"])]) or int(lastSubID[str(contest["id"])]) == -1:
                    skipFlag = True
                    break
                subCount = subCount + 1

                # ユーザーの AC 提出かどうか判定
                if subData[6] == "AC":
                    for atcoderID, twitterID in AtCoderIDs:
                        if atcoderID == userID:
                            if atcoderID in noticeFlag:
                                if noticeFlag[atcoderID] == "off":
                                    break
                            else:
                                noticeFlag[atcoderID] = "on"
                            try:
                                api.update_status(atcoderID + " ( @" + twitterID + " ) さんが <AtCoder> " + str(contest["title"]) + "：" + str(subData[1]) + " を AC しました！\nhttps://atcoder.jp" + str(links[3].get("href")) + "\n" + timeStamp)
                                print("cper_bot-AtCoder-detection: " + atcoderID + " ( @" + twitterID + " ) 's new AC submission (contest : " + str(contest["title"]) + ", problem : " + str(subData[1]) + ")")
                            except:
                                print("cper_bot-AtCoder-detection: Tweet Error")
                
                # エラーであれば無条件に報告
                if subData[6] == "IE" or subData[6] == "NG":
                    try:
                        api.update_status("AtCoder で " + subData[6]  + " となっている提出が検出されました！\nhttps://atcoder.jp" + str(links[3].get("href")) + "\n" + timeStamp)
                        print("cper_bot-AtCoder-detection: detected " + subData[6] + " submission!")
                    except:
                        print("cper_bot-AtCoder-detection: Tweet Error")
            if skipFlag:
                break
            sublistPageNum = sublistPageNum + 1

        print("cper_bot-AtCoder-detection: Checked " + contest["title"] + " submissions (subCount : " + str(subCount) + ", newlastSubID : " + str(newLastSubID[str(contest["id"])]) + ")")

    # データをアップロード
    if type == 0:
        lastSubID_All = newLastSubID
    if type == 1:
        lastSubID_Recent = newLastSubID
    uploadToDropbox(type)

if __name__ == '__main__':
    print("cper_bot-AtCoder-detection: Running as debug...")
    detection(1)
    print("cper_bot-AtCoder-detection: Debug finished")
