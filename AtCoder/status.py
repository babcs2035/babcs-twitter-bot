# import
import os
import dropbox
import requests
import pickle
import json

# グローバル変数
acCount = {}
acPoint = {}

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global acCount
    global acPoint

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # acCount をダウンロード
    dbx.files_download_to_file("AtCoder/daily_acCount.txt", "/AtCoder/daily_acCount.txt")
    with open("AtCoder/daily_acCount.txt", "rb") as f:
        acCount = pickle.load(f)
    print("cper_bot-AtCoder-status: Downloaded daily acCount (size : ", str(len(acCount)), ")")
    
    # acPoint をダウンロード
    dbx.files_download_to_file("AtCoder/daily_acPoint.txt", "/AtCoder/daily_acPoint.txt")
    with open("AtCoder/daily_acPoint.txt", "rb") as f:
        acPoint = pickle.load(f)
    print("cper_bot-AtCoder-status: Downloaded daily acPoint (size : ", str(len(acPoint)), ")")

def status(atcoderID):

    # グローバル変数
    global acCount
    global acPoint
    
    # データをダウンロード
    downloadFromDropbox()

    # json 形式で取得
    session = requests.Session()
    request = session.get(url = "https://kenkoooo.com/atcoder/atcoder-api/v2/user_info?user=" + atcoderID)
    userData = json.loads(request.text)
    print("cper_bot-AtCoder-status: Downloaded " + atcoderID + "'s userData")

    tweetText = ""
    if atcoderID in acCount:
        tweetText += "今日の Unique AC 数 : " + str(int(userData["accepted_count"]) - int(acCount[atcoderID])) + "\n"
    if atcoderID in acPoint:
        tweetText += "今日の Unique AC の Rated Point Sum : " + str(int(userData["rated_point_sum"]) - int(acPoint[atcoderID])) + "\n"
    if atcoderID in acCount and atcoderID in acPoint:
        if int(userData["accepted_count"]) - int(acCount[atcoderID]) > 0:
            tweetText += "今日の Rated Point Sum / Unique AC 数 : " + str((int(userData["rated_point_sum"]) - int(acPoint[atcoderID])) / (int(userData["accepted_count"]) - int(acCount[atcoderID]))) + "\n"
    else:
        tweetText += "この AtCoder ID は登録されていないか，まだ統計情報がありません（ID を登録してから日付をまたぐ必要があります）．\n"
    return tweetText

if __name__ == '__main__':
    print("cper_bot-AtCoder-status: Running as debug...")
    print(status("Bwambocos"))
    print("cper_bot-AtCoder-status: Debug finished")
