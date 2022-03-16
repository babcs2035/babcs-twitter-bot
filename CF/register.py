# import
import os
import datetime
import urllib.request
import dropbox
import pickle

# グローバル変数
CFIDs = set()
CFIDsFixedFlag = False

# CF ID が存在するか確認
def checkCFID(cfID):

    try:
        html = urllib.request.urlopen("https://codeforces.com/api/user.status?handle=" + cfID)
        print("cper_bot-CF-register: " + cfID + " is correct Codeforces ID")
        return True
    except:
        print("cper_bot-CF-register: " + cfID + " is not correct Codeforces ID")
        return False

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global CFIDs

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # CFIDs をダウンロード
    dbx.files_download_to_file("CF/CFIDs.txt", "/CF/CFIDs.txt")
    with open("CF/CFIDs.txt", "rb") as f:
        CFIDs = pickle.load(f)
    print("cper_bot-CF-register: Downloaded CFIDs (size : ", str(len(CFIDs)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global CFIDs
    global CFIDsFixedFlag

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
        
    if CFIDsFixedFlag:

        # CFIDs をアップロード
        with open("CF/CFIDs.txt", "wb") as f:
            pickle.dump(CFIDs, f)
        with open("CF/CFIDs.txt", "rb") as f:
            dbx.files_upload(f.read(), "/CF/CFIDs.txt", mode = dropbox.files.WriteMode.overwrite)
            print("cper_bot-CF-register: Uploaded CFIDs (size : ", str(len(CFIDs)), ")")
        with open("CF/CFIDs.txt", "rb") as f:
            dbx.files_upload(f.read(), "/_backup/CF/CFIDs/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".txt")
            print("cper_bot-CF-register: Uploaded CFIDs (for backup " + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ") (size : ", str(len(CFIDs)), ")")

# CF ID 登録・解除
def register(cfID, twitterID, flag):

    print("cper_bot-CF-register: ----- CF-register Start -----")

    # グローバル変数
    global CFIDs
    global CFIDsFixedFlag
        
    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # データをダウンロード
    downloadFromDropbox()

    # 登録・解除処理
    CFIDsFixedFlag = False
    tweetText = ""
    if flag == 0:
        if checkCFID(cfID):
            if (cfID, twitterID) not in CFIDs:
                CFIDs.add((cfID, twitterID))
                tweetText = "@" + str(twitterID) + " Codeforces ID を登録しました！\n";
                print("cper_bot-CF-register: Registered new CF ID : " + cfID)
                CFIDsFixedFlag = True
            else:
                tweetText = "@" + str(twitterID) + " この Codeforces ID は既に登録されています！\n"
                print("cper_bot-AtCoder-register: Rejected to register CF ID : " + cfID)
        else:
            tweetText = "@" + str(twitterID) + " 正しい Codeforces ID ではありません！\n"
            print("cper_bot-CF-register: Rejected to CF-register new CF ID : " + cfID)
    if flag == 1:
        if checkCFID(cfID):
            if (cfID, twitterID) in CFIDs:
                CFIDs.remove((cfID, twitterID))
                tweetText = "@" + str(twitterID) + " Codeforces ID を登録解除しました！\n"
                print("cper_bot-CF-register: Unregistered CF ID : " + cfID)
                CFIDsFixedFlag = True
            else:
                tweetText = "@" + str(twitterID) + " この Codeforces ID は登録されていません！\n"
                print("cper_bot-CF-register: Rejected to unregister CF ID : " + cfID)
        else:
            tweetText = "@" + str(twitterID) + " 正しい Codeforces ID ではありません！\n"
            print("cper_bot-CF-register: Rejected to unregister CF ID : " + cfID)

    # 変更されたデータをアップロード
    uploadToDropbox()
    
    print("cper_bot-CF-register: ----- CF-register End -----")
    return tweetText
