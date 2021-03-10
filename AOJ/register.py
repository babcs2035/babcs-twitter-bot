# import
import os
import datetime
import urllib.request
import dropbox
import pickle

# グローバル変数
AOJIDsFixedFlag = False
AOJIDs = set()

# AOJ ID が存在するか確認
def checkAOJIDs(AOJID):

    try:
        html = urllib.request.urlopen("https://judgeapi.u-aizu.ac.jp/users/" + AOJID)
        print("cper_bot-AOJ-register: " + AOJID + " is correct AOJ ID")
        return True
    except:
        print("cper_bot-AOJ-register: " + AOJID + " is not correct AOJ ID")
        return False

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global AOJIDs

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # AOJIDs をダウンロード
    dbx.files_download_to_file("AOJ/AOJIDs.txt", "/AOJ/AOJIDs.txt")
    with open("AOJ/AOJIDs.txt", "rb") as f:
        AOJIDs = pickle.load(f)
    print("cper_bot-AOJ-register: Downloaded AOJIDs (size : ", str(len(AOJIDs)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global AOJIDs
    global AOJIDsFixedFlag

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
        
    if AOJIDsFixedFlag:

        # AOJIDs をアップロード
        with open("AOJ/AOJIDs.txt", "wb") as f:
            pickle.dump(AOJIDs, f)
        with open("AOJ/AOJIDs.txt", "rb") as f:
            dbx.files_upload(f.read(), "/AOJ/AOJIDs.txt", mode = dropbox.files.WriteMode.overwrite)
            print("cper_bot-AOJ-register: Uploaded AOJIDs (size : ", str(len(AOJIDs)), ")")
        with open("AOJ/AOJIDs.txt", "rb") as f:
            dbx.files_upload(f.read(), "/_backup/AOJ/AOJIDs/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".txt")
            print("cper_bot-AOJ-register: Uploaded AOJIDs (for backup " + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ") (size : ", str(len(AOJIDs)), ")")
    
# AOJ ID 登録・解除
def register(AOJID, twitterID, flag):

    print("AOJ-register: ----- AOJ-register Start -----")

    # グローバル変数
    global AOJIDs
    global AOJIDsFixedFlag
        
    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # データをダウンロード
    downloadFromDropbox()

    # 登録・解除処理
    AOJIDsFixedFlag = False
    tweetText = ""
    if flag == 0:
        if checkAOJIDs(AOJID):
            if (AOJID, twitterID) not in AOJIDs:
                AOJIDs.add((AOJID, twitterID))
                tweetText = "@" + str(twitterID) + " AOJ ID を登録しました！\n";
                print("cper_bot-AOJ-register: Registered new AOJ ID : " + AOJID)
                AOJIDsFixedFlag = True
            else:
                tweetText = "@" + str(twitterID) + " この AOJ ID は既に登録されています！\n"
                print("cper_bot-AtCoder-register: Rejected to register AOJ ID : " + AOJID)
        else:
            tweetText = "@" + str(twitterID) + " 正しい AOJ ID ではありません！\n"
            print("cper_bot-AOJ-register: Rejected to AOJ-register new AOJ ID : " + AOJID)
    if flag == 1:
        if checkAOJIDs(AOJID):
            if (AOJID, twitterID) in AOJIDs:
                AOJIDs.remove((AOJID, twitterID))
                tweetText = "@" + str(twitterID) + " AOJ ID を登録解除しました！\n"
                print("cper_bot-AOJ-register: Unregistered AOJ ID : " + AOJID)
                AOJIDsFixedFlag = True
            else:
                tweetText = "@" + str(twitterID) + " この AOJ ID は登録されていません！\n"
                print("cper_bot-AOJ-register: Rejected to unregister AOJ ID : " + AOJID)
        else:
            tweetText = "@" + str(twitterID) + " 正しい AOJ ID ではありません！\n"
            print("cper_bot-AOJ-register: Rejected to unregister AOJ ID : " + AOJID)

    # 変更されたデータをアップロード
    uploadToDropbox()
    
    print("cper_bot-AOJ-register: ----- AOJ-register End -----")
    return tweetText
