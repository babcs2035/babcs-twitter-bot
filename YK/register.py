# import
import os
import datetime
import urllib.request
import dropbox
import pickle

# グローバル変数
YKIDs = set()
YKIDsFixedFlag = False

# YK ID が存在するか確認
def checkYKID(ykID):

    try:
        html = urllib.request.urlopen("https://yukicoder.me/api/v1/user/name/" + urllib.parse.quote_plus(ykID, encoding = "utf-8"))
        print("cper_bot-YK-register: " + ykID + " is correct yukicoder ID")
        return True
    except:
        print("cper_bot-YK-register: " + ykID + " is not correct yukicoder ID")
        return False

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global YKIDs

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # YKID をダウンロード
    dbx.files_download_to_file("YK/YKIDs.txt", "/YK/YKIDs.txt")
    with open("YK/YKIDs.txt", "rb") as f:
        YKIDs = pickle.load(f)
    print("cper_bot-YK-register: Downloaded YKIDs (size : ", str(len(YKIDs)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global YKIDs
    global YKIDsFixedFlag

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
        
    if YKIDsFixedFlag:

        # YKIDs をアップロード
        with open("YK/YKIDs.txt", "wb") as f:
            pickle.dump(YKIDs, f)
        with open("YK/YKIDs.txt", "rb") as f:
            dbx.files_upload(f.read(), "/YK/YKIDs.txt", mode = dropbox.files.WriteMode.overwrite)
            print("cper_bot-YK-register: Uploaded YKIDs (size : ", str(len(YKIDs)), ")")
        with open("YK/YKIDs.txt", "rb") as f:
            dbx.files_upload(f.read(), "/_backup/YK/YKIDs/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".txt")
            print("cper_bot-YK-register: Uploaded YKIDs (for backup " + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ") (size : ", str(len(YKIDs)), ")")

# YK ID 登録・解除
def register(ykID, twitterID, flag):

    print("cper_bot-YK-register: ----- YK-register Start -----")

    # グローバル変数
    global YKIDs
    global YKIDsFixedFlag
        
    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # データをダウンロード
    downloadFromDropbox()

    # 登録・解除処理
    YKIDsFixedFlag = False
    tweetText = ""
    if flag == 0:
        if checkYKID(ykID):
            if (ykID, twitterID) not in YKIDs:
                YKIDs.add((ykID, twitterID))
                tweetText = "@" + str(twitterID) + " yukicoder ID を登録しました！\n";
                print("cper_bot-YK-register: Registered new YK ID : " + ykID)
                YKIDsFixedFlag = True
            else:
                tweetText = "@" + str(twitterID) + " この yukicoder ID は既に登録されています！\n"
                print("cper_bot-AtCoder-register: Rejected to register YK ID : " + ykID)
        else:
            tweetText = "@" + str(twitterID) + " 正しい yukicoder ID ではありません！\n"
            print("cper_bot-YK-register: Rejected to YK-register new YK ID : " + ykID)
    if flag == 1:
        if checkYKID(ykID):
            if (ykID, twitterID) in YKIDs:
                YKIDs.remove((ykID, twitterID))
                tweetText = "@" + str(twitterID) + " yukicoder ID を登録解除しました！\n"
                print("cper_bot-YK-register: Unregistered YK ID : " + ykID)
                YKIDsFixedFlag = True
            else:
                tweetText = "@" + str(twitterID) + " この yukicoder ID は登録されていません！\n"
                print("cper_bot-YK-register: Rejected to unregister YK ID : " + ykID)
        else:
            tweetText = "@" + str(twitterID) + " 正しい yukicoder ID ではありません！\n"
            print("cper_bot-YK-register: Rejected to unregister YK ID : " + ykID)

    # 変更されたデータをアップロード
    uploadToDropbox()
    
    print("cper_bot-YK-register: ----- YK-register End -----")
    return tweetText
