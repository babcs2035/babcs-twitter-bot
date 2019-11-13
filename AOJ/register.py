# import
import os
import datetime
import urllib.request
import dropbox

# グローバル変数
AOJID = []
AOJ_TwitterID = []
AOJ_listFixedFlag = False

# AOJ ID が存在するか確認
def checkAOJID(aojID):

    try:
        html = urllib.request.urlopen("https://judgeapi.u-aizu.ac.jp/users/" + aojID)
        print("cper_bot-AOJ-register: " + aojID + " is correct AOJ ID")
        return True
    except:
        print("cper_bot-AOJ-register: " + aojID + " is not correct AOJ ID")
        return False

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global AOJID
    global AOJ_TwitterID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # AOJID をダウンロード
    dbx.files_download_to_file("cper_bot/AOJ/AOJID.txt", "/cper_bot/AOJ/AOJID.txt")
    with open("cper_bot/AOJ/AOJID.txt", "r") as f:
        AOJID.clear()
        for id in f:
            AOJID.append(id.rstrip("\n"))
    print("cper_bot-AOJ-register: Downloaded AOJID (size : ", str(len(AOJID)), ")")
    
    # AOJ_TwitterID をダウンロード
    dbx.files_download_to_file("cper_bot/AOJ/TwitterID.txt", "/cper_bot/AOJ/TwitterID.txt")
    with open("cper_bot/AOJ/TwitterID.txt", "r") as f:
        AOJ_TwitterID.clear()
        for id in f:
            AOJ_TwitterID.append(id.rstrip("\n"))
    print("cper_bot-AOJ-register: Downloaded AOJ_TwitterID (size : ", str(len(AOJ_TwitterID)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global AOJID
    global AOJ_TwitterID
    global AOJ_listFixedFlag

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
        
    if AOJ_listFixedFlag:
        # AOJID をアップロード
        with open("cper_bot/AOJ/AOJID.txt", "w") as f:
            for id in AOJID:
                f.write(str(id) + "\n")
        with open("cper_bot/AOJ/AOJID.txt", "rb") as f:
            dbx.files_delete("/cper_bot/AOJ/AOJID.txt")
            dbx.files_upload(f.read(), "/cper_bot/AOJ/AOJID.txt")
            print("cper_bot-AOJ-register: Uploaded AOJID (size : ", str(len(AOJID)), ")")
        with open("cper_bot/AOJ/AOJID.txt", "rb") as f:
            dbx.files_upload(f.read(), "/cper_bot/_backup/AOJ/AOJID/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".txt")
            print("cper_bot-AOJ-register: Uploaded AOJID (for backup " + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ") (size : ", str(len(AOJID)), ")")

        # AOJ_TwitterID をアップロード
        with open("cper_bot/AOJ/TwitterID.txt", "w") as f:
            for id in AOJ_TwitterID:
                f.write(str(id) + "\n")
        with open("cper_bot/AOJ/TwitterID.txt", "rb") as f:
            dbx.files_delete("/cper_bot/AOJ/TwitterID.txt")
            dbx.files_upload(f.read(), "/cper_bot/AOJ/TwitterID.txt")
            print("cper_bot-AOJ-register: Uploaded AOJ_TwitterID (size : ", str(len(AOJ_TwitterID)), ")")
        with open("cper_bot/AOJ/TwitterID.txt", "rb") as f:
            dbx.files_upload(f.read(), "/cper_bot/_backup/AOJ/TwitterID/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".txt")
            print("cper_bot-AOJ-register: Uploaded AOJ_TwitterID (for backup " + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ") (size : ", str(len(AOJ_TwitterID)), ")")
    
# list 内の要素の添え字を返す（無い場合は -1）
def myIndex(x, l):
    if x in l:
        return l.index(x)
    else:
        return -1

# AOJ ID 登録・解除
def register(aojID, twitterID, flag):

    print("AOJ-register: ----- AOJ-register Start -----")

    # グローバル変数
    global AOJID
    global AOJ_TwitterID
    global AOJ_listFixedFlag
        
    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # データをダウンロード
    downloadFromDropbox()

    # 登録・解除処理
    AOJ_listFixedFlag = False
    tweetText = ""
    if flag == 0:
        if checkAOJID(aojID):
            AOJID.append(aojID)
            AOJ_TwitterID.append(twitterID)
            tweetText = "@" + str(twitterID) + " AOJ ID を登録しました！\n";
            print("cper_bot-AOJ-register: Registered new AOJ ID : " + aojID)
            AOJ_listFixedFlag = True
        else:
            tweetText = "@" + str(twitterID) + " 正しい AOJ ID ではありません！\n"
            print("cper_bot-AOJ-register: Rejected to AOJ-register new AOJ ID : " + aojID)
    if flag == 1:
        if checkAOJID(aojID):
            if myIndex(aojID, AOJID) != -1 and myIndex(str(twitterID), AOJ_TwitterID) != -1 and myIndex(aojID, AOJID) == myIndex(str(twitterID), AOJ_TwitterID):
                AOJID.pop(myIndex(str(twitterID), AOJ_TwitterID))
                AOJ_TwitterID.pop(myIndex(str(twitterID), AOJ_TwitterID))
                tweetText = "@" + str(twitterID) + " AOJ ID を登録解除しました！\n"
                print("cper_bot-AOJ-register: Unregistered AOJ ID : " + aojID)
                AOJ_listFixedFlag = True
            else:
                tweetText = "@" + str(twitterID) + " この AOJ ID は登録されていません！\n"
                print("cper_bot-AOJ-register: Rejected to unregister AOJ ID : " + aojID)
        else:
            tweetText = "@" + str(twitterID) + " 正しい AOJ ID ではありません！\n"
            print("cper_bot-AOJ-register: Rejected to unregister AOJ ID : " + aojID)

    # 変更されたデータをアップロード
    uploadToDropbox()
    
    print("cper_bot-AOJ-register: ----- AOJ-register End -----")
    return tweetText
