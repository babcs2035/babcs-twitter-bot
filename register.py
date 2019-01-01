# import
import subprocess
import os
import tweepy
import datetime
import json
import urllib.request
import dropbox
from apscheduler.schedulers.blocking import BlockingScheduler
from requests_oauthlib import OAuth1Session

# グローバル変数
lastTweetID = 0
AtCoderID = []
AtCoder_TwitterID = []
AtCoder_listFixedFlag = False
AOJID = []
AOJ_TwitterID = []
AOJ_listFixedFlag = False
CFID = []
CF_TwitterID = []
CF_listFixedFlag = False
idFixedFlag = False

# AtCoder ID が存在するか確認
def checkAtCoderID(atcoderID):

    # AtCoder ユーザーページにアクセス
    try:
        html = urllib.request.urlopen("https://atcoder.jp/users/" + atcoderID)
        print("register: " + atcoderID + " is correct AtCoder ID")
        return True
    except:
        print("register: " + atcoderID + " is not correct AtCoder ID")
        return False

# AOJ ID が存在するか確認
def checkAOJID(aojID):

    # AOJ ユーザーページにアクセス
    try:
        html = urllib.request.urlopen("https://judgeapi.u-aizu.ac.jp/users/" + aojID)
        print("register: " + aojID + " is correct AOJ ID")
        return True
    except:
        print("register: " + aojID + " is not correct AOJ ID")
        return False

# Codeforces ID が存在するか確認
def checkCFID(cfID):

    # AOJ ユーザーページにアクセス
    try:
        html = urllib.request.urlopen("https://codeforces.com/api/user.status?handle=" + cfID)
        print("register: " + cfID + " is correct Codeforces ID")
        return True
    except:
        print("register: " + cfID + " is not correct Codeforces ID")
        return False

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global lastTweetID
    global AtCoderID
    global AtCoder_TwitterID
    global AOJID
    global AOJ_TwitterID
    global CFID
    global CF_TwitterID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # lastTweetID をダウンロード
    dbx.files_download_to_file("lastTweetID.txt", "/lastTweetID.txt")
    with open("lastTweetID.txt", "r") as f:
        lastTweetID = f.readline()
    print("register: Downloaded lastTweetID : ", str(lastTweetID))
    
    # AtCoderID をダウンロード
    dbx.files_download_to_file("AtCoder/AtCoderID.txt", "/AtCoder/AtCoderID.txt")
    with open("AtCoder/AtCoderID.txt", "r") as f:
        AtCoderID.clear()
        for id in f:
            AtCoderID.append(id.rstrip("\n"))
    print("register: Downloaded AtCoderID (size : ", str(len(AtCoderID)), ")")
    
    # AtCoder_TwitterID をダウンロード
    dbx.files_download_to_file("AtCoder/TwitterID.txt", "/AtCoder/TwitterID.txt")
    with open("AtCoder/TwitterID.txt", "r") as f:
        AtCoder_TwitterID.clear()
        for id in f:
            AtCoder_TwitterID.append(id.rstrip("\n"))
    print("register: Downloaded AtCoder_TwitterID (size : ", str(len(AtCoder_TwitterID)), ")")

    # AOJID をダウンロード
    dbx.files_download_to_file("AOJ/AOJID.txt", "/AOJ/AOJID.txt")
    with open("AOJ/AOJID.txt", "r") as f:
        AOJID.clear()
        for id in f:
            AOJID.append(id.rstrip("\n"))
    print("register: Downloaded AOJID (size : ", str(len(AOJID)), ")")
    
    # AOJ_TwitterID をダウンロード
    dbx.files_download_to_file("AOJ/TwitterID.txt", "/AOJ/TwitterID.txt")
    with open("AOJ/TwitterID.txt", "r") as f:
        AOJ_TwitterID.clear()
        for id in f:
            AOJ_TwitterID.append(id.rstrip("\n"))
    print("register: Downloaded AOJ_TwitterID (size : ", str(len(AOJ_TwitterID)), ")")

    # CFID をダウンロード
    dbx.files_download_to_file("CF/CFID.txt", "/CF/CFID.txt")
    with open("CF/CFID.txt", "r") as f:
        CFID.clear()
        for id in f:
            CFID.append(id.rstrip("\n"))
    print("register: Downloaded CFID (size : ", str(len(CFID)), ")")
    
    # CF_TwitterID をダウンロード
    dbx.files_download_to_file("CF/TwitterID.txt", "/CF/TwitterID.txt")
    with open("CF/TwitterID.txt", "r") as f:
        CF_TwitterID.clear()
        for id in f:
            CF_TwitterID.append(id.rstrip("\n"))
    print("register: Downloaded CF_TwitterID (size : ", str(len(CF_TwitterID)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global lastTweetID
    global AtCoderID
    global AtCoder_TwitterID
    global AtCoder_listFixedFlag
    global AOJID
    global AOJ_TwitterID
    global AOJ_listFixedFlag
    global CFID
    global CF_TwitterID
    global CF_listFixedFlag
    global idFixedFlag

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
    
    # lastTweetID をアップロード
    if idFixedFlag:
        with open("lastTweetID.txt", "w") as f:
            f.write(str(lastTweetID))
        with open("lastTweetID.txt", "rb") as f:
            dbx.files_delete("/lastTweetID.txt")
            dbx.files_upload(f.read(), "/lastTweetID.txt")
        print("register: Uploaded lastTweetID : ", str(lastTweetID))
    
    if AtCoder_listFixedFlag:
        # AtCoderID をアップロード
        with open("AtCoder/AtCoderID.txt", "w") as f:
            for id in AtCoderID:
                f.write(str(id) + "\n")
        with open("AtCoder/AtCoderID.txt", "rb") as f:
            dbx.files_delete("/AtCoder/AtCoderID.txt")
            dbx.files_upload(f.read(), "/AtCoder/AtCoderID.txt")
            print("register: Uploaded AtCoderID (size : ", str(len(AtCoderID)), ")")
        with open("AtCoder/AtCoderID.txt", "rb") as f:
            dbx.files_upload(f.read(), "/_backup/AtCoder/AtCoderID/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".txt")
            print("register: Uploaded AtCoderID (for backup " + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ") (size : ", str(len(AtCoderID)), ")")

        # AtCoder_TwitterID をアップロード
        with open("AtCoder/TwitterID.txt", "w") as f:
            for id in AtCoder_TwitterID:
                f.write(str(id) + "\n")
        with open("AtCoder/TwitterID.txt", "rb") as f:
            dbx.files_delete("/AtCoder/TwitterID.txt")
            dbx.files_upload(f.read(), "/AtCoder/TwitterID.txt")
            print("register: Uploaded AtCoder_TwitterID (size : ", str(len(AtCoder_TwitterID)), ")")
        with open("AtCoder/TwitterID.txt", "rb") as f:
            dbx.files_upload(f.read(), "/_backup/AtCoder/TwitterID/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".txt")
            print("register: Uploaded AtCoder_TwitterID (for backup " + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ") (size : ", str(len(AtCoder_TwitterID)), ")")
    
    if AOJ_listFixedFlag:
        # AOJID をアップロード
        with open("AOJ/AOJID.txt", "w") as f:
            for id in AOJID:
                f.write(str(id) + "\n")
        with open("AOJ/AOJID.txt", "rb") as f:
            dbx.files_delete("/AOJ/AOJID.txt")
            dbx.files_upload(f.read(), "/AOJ/AOJID.txt")
            print("register: Uploaded AOJID (size : ", str(len(AOJID)), ")")
        with open("AOJ/AOJID.txt", "rb") as f:
            dbx.files_upload(f.read(), "/_backup/AOJ/AOJID/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".txt")
            print("register: Uploaded AOJID (for backup " + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ") (size : ", str(len(AOJID)), ")")

        # AOJ_TwitterID をアップロード
        with open("AOJ/TwitterID.txt", "w") as f:
            for id in AOJ_TwitterID:
                f.write(str(id) + "\n")
        with open("AOJ/TwitterID.txt", "rb") as f:
            dbx.files_delete("/AOJ/TwitterID.txt")
            dbx.files_upload(f.read(), "/AOJ/TwitterID.txt")
            print("register: Uploaded AOJ_TwitterID (size : ", str(len(AOJ_TwitterID)), ")")
        with open("AOJ/TwitterID.txt", "rb") as f:
            dbx.files_upload(f.read(), "/_backup/AOJ/TwitterID/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".txt")
            print("register: Uploaded AOJ_TwitterID (for backup " + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ") (size : ", str(len(AOJ_TwitterID)), ")")
    
    if CF_listFixedFlag:
        # CFID をアップロード
        with open("CF/CFID.txt", "w") as f:
            for id in CFID:
                f.write(str(id) + "\n")
        with open("CF/CFID.txt", "rb") as f:
            dbx.files_delete("/CF/CFID.txt")
            dbx.files_upload(f.read(), "/CF/CFID.txt")
            print("register: Uploaded CFID (size : ", str(len(CFID)), ")")
        with open("CF/CFID.txt", "rb") as f:
            dbx.files_upload(f.read(), "/_backup/CF/CFID/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".txt")
            print("register: Uploaded CFID (for backup " + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ") (size : ", str(len(CFID)), ")")

        # CF_TwitterID をアップロード
        with open("CF/TwitterID.txt", "w") as f:
            for id in CF_TwitterID:
                f.write(str(id) + "\n")
        with open("CF/TwitterID.txt", "rb") as f:
            dbx.files_delete("/CF/TwitterID.txt")
            dbx.files_upload(f.read(), "/CF/TwitterID.txt")
            print("register: Uploaded CF_TwitterID (size : ", str(len(CF_TwitterID)), ")")
        with open("CF/TwitterID.txt", "rb") as f:
            dbx.files_upload(f.read(), "/_backup/CF/TwitterID/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".txt")
            print("register: Uploaded CF_TwitterID (for backup " + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ") (size : ", str(len(CF_TwitterID)), ")")

# list 内の要素の添え字を返す（無い場合は -1）
def myIndex(x, l):
    if x in l:
        return l.index(x)
    else:
        return -1

# インスタンス化
sched = BlockingScheduler(job_defaults = {'max_instances' : 5})

# AtCoder, AOJ, Codeforces ID 登録（20 秒ごと）
@sched.scheduled_job('interval', seconds = 20)
def scheduled_job():

    print("register: ----- AtCoder, AOJ, Codeforces register Start -----")

    # グローバル変数
    global lastTweetID
    global AtCoderID
    global AtCoder_TwitterID
    global AtCoder_listFixedFlag
    global AOJID
    global AOJ_TwitterID
    global AOJ_listFixedFlag
    global CFID
    global CF_TwitterID
    global CF_listFixedFlag
    global idFixedFlag

    # 各種キー設定
    CK = os.environ["CONSUMER_KEY"]
    CS = os.environ["CONSUMER_SECRET"]
    AT = os.environ["ACCESS_TOKEN_KEY"]
    AS = os.environ["ACCESS_TOKEN_SECRET"]
    
    # Twitter オブジェクトの生成
    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    api = tweepy.API(auth)
    
    # OAuth でツイートを取得
    api_OAuth = OAuth1Session(CK, CS, AT, AS)
    timeline_json = api_OAuth.get("https://api.twitter.com/1.1/statuses/mentions_timeline.json")
    
    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # データをダウンロード
    downloadFromDropbox()

    # ツイートを解析
    myTwitterID = "babcs_bot"
    defSubID = 0
    if timeline_json.status_code == 200:
        timeline = json.loads(timeline_json.text)
        AtCoder_listFixedFlag = False
        AOJ_listFixedFlag = False
        CF_listFixedFlag = False
        idFixedFlag = False
        for tweet in timeline:
            if int(tweet["id_str"]) <= int(lastTweetID):
                break
            idFixedFlag = True
            tweetText = str(tweet["text"])
            tweetSplited = tweetText.split()
            if len(tweetSplited) >= 3:
                userData_json = api_OAuth.get("https://api.twitter.com/1.1/users/show.json?user_id=" + tweet["user"]["id_str"])
                userData = json.loads(userData_json.text)

                # AtCoder ID 登録
                if tweetSplited[1] == "reg_atcoder":
                    if checkAtCoderID(tweetSplited[2]):
                        AtCoderID.append(tweetSplited[2])
                        AtCoder_TwitterID.append(userData["screen_name"])
                        api.update_status("@" + str(userData["screen_name"]) + " AtCoder ID を登録しました！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                        print("register: Register new AtCoder ID : " + tweetSplited[2])
                        AtCoder_listFixedFlag = True
                    else:
                        api.update_status("@" + str(userData["screen_name"]) + " 正しい AtCoder ID ではありません！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                        print("register: Reject to register new AtCoder ID : " + tweetSplited[2])
                
                # AtCoder ID 解除    
                if tweetSplited[1] == "del_atcoder":
                    if checkAtCoderID(tweetSplited[2]):
                        if myIndex(tweetSplited[2], AtCoderID) != -1 and myIndex(str(userData["screen_name"]), AtCoder_TwitterID) != -1 and myIndex(tweetSplited[2], AtCoderID) == myIndex(str(userData["screen_name"]), AtCoder_TwitterID):
                            AtCoderID.pop(myIndex(str(userData["screen_name"]), AtCoder_TwitterID))
                            AtCoder_TwitterID.pop(myIndex(str(userData["screen_name"]), AtCoder_TwitterID))
                            api.update_status("@" + str(userData["screen_name"]) + " AtCoder ID を登録解除しました！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                            print("register: Unregister AtCoder ID : " + tweetSplited[2])
                            AtCoder_listFixedFlag = True
                        else:
                            api.update_status("@" + str(userData["screen_name"]) + " この AtCoder ID は登録されていません！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                            print("register: Reject to unregister AtCoder ID : " + tweetSplited[2])
                    else:
                        api.update_status("@" + str(userData["screen_name"]) + " 正しい AtCoder ID ではありません！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                        print("register: Reject to unregister AtCoder ID : " + tweetSplited[2])

                # AOJ ID 登録
                if tweetSplited[1] == "reg_aoj":
                    if checkAOJID(tweetSplited[2]):
                        AOJID.append(tweetSplited[2])
                        AOJ_TwitterID.append(userData["screen_name"])
                        api.update_status("@" + str(userData["screen_name"]) + " AOJ ID を登録しました！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                        print("register: Register new AOJ ID : " + tweetSplited[2])
                        AOJ_listFixedFlag = True
                    else:
                        api.update_status("@" + str(userData["screen_name"]) + " 正しい AOJ ID ではありません！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                        print("register: Reject to register new AOJ ID : " + tweetSplited[2])

                # AOJ ID 解除    
                if tweetSplited[1] == "del_aoj":
                    if checkAOJID(tweetSplited[2]):
                        if myIndex(tweetSplited[2], AOJID) != -1 and myIndex(str(userData["screen_name"]), AOJ_TwitterID) != -1 and myIndex(tweetSplited[2], AOJID) == myIndex(str(userData["screen_name"]), AOJ_TwitterID):
                            AOJID.pop(myIndex(str(userData["screen_name"]), AOJ_TwitterID))
                            AOJ_TwitterID.pop(myIndex(str(userData["screen_name"]), AOJ_TwitterID))
                            api.update_status("@" + str(userData["screen_name"]) + " AOJ ID を登録解除しました！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                            print("register: Unregister AOJ ID : " + tweetSplited[2])
                            AOJ_listFixedFlag = True
                        else:
                            api.update_status("@" + str(userData["screen_name"]) + " この AOJ ID は登録されていません！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                            print("register: Reject to unregister AOJ ID : " + tweetSplited[2])
                    else:
                        api.update_status("@" + str(userData["screen_name"]) + " 正しい AOJ ID ではありません！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                        print("register: Reject to unregister AOJ ID : " + tweetSplited[2])

                # CF ID 登録
                if tweetSplited[1] == "reg_cf":
                    if checkCFID(tweetSplited[2]):
                        CFID.append(tweetSplited[2])
                        CF_TwitterID.append(userData["screen_name"])
                        api.update_status("@" + str(userData["screen_name"]) + " Codeforces ID を登録しました！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                        print("register: Register new Codeforces ID : " + tweetSplited[2])
                        CF_listFixedFlag = True
                    else:
                        api.update_status("@" + str(userData["screen_name"]) + " 正しい Codeforces ID ではありません！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                        print("register: Reject to register new Codeforces ID : " + tweetSplited[2])

                # CF ID 解除    
                if tweetSplited[1] == "del_cf":
                    if checkCFID(tweetSplited[2]):
                        if myIndex(tweetSplited[2], CFID) != -1 and myIndex(str(userData["screen_name"]), CF_TwitterID) != -1 and myIndex(tweetSplited[2], CFID) == myIndex(str(userData["screen_name"]), CF_TwitterID):
                            CFID.pop(myIndex(str(userData["screen_name"]), CF_TwitterID))
                            CF_TwitterID.pop(myIndex(str(userData["screen_name"]), CF_TwitterID))
                            api.update_status("@" + str(userData["screen_name"]) + " Codeforces ID を登録解除しました！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                            print("register: Unregister Codeforces ID : " + tweetSplited[2])
                            CF_listFixedFlag = True
                        else:
                            api.update_status("@" + str(userData["screen_name"]) + " この Codeforces ID は登録されていません！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                            print("register: Reject to unregister Codeforces ID : " + tweetSplited[2])
                    else:
                        api.update_status("@" + str(userData["screen_name"]) + " 正しい Codeforces ID ではありません！\n" + timeStamp, in_reply_to_status_id = tweet["id"])
                        print("register: Reject to unregister Codeforces ID : " + tweetSplited[2])

        lastTweetID = int(timeline[0]["id_str"])

        # 変更されたデータをアップロード
        uploadToDropbox()

    else:
        print("register: Twitter API Error: %d" % timeline_json.status_code)

    print("register: ----- AtCoder, AOJ, Codeforces register End -----")
    
# おまじない
sched.start()
