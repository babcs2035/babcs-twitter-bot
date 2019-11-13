# import
import os
import datetime
import urllib.request
import dropbox

# グローバル変数
YKID = []
YK_TwitterID = []
YK_listFixedFlag = False

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
    global YKID
    global YK_TwitterID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # YKID をダウンロード
    dbx.files_download_to_file("cper_bot/YK/YKID.txt", "/cper_bot/YK/YKID.txt")
    with open("cper_bot/YK/YKID.txt", "r") as f:
        YKID.clear()
        for id in f:
            YKID.append(id.rstrip("\n"))
    print("cper_bot-YK-register: Downloaded YKID (size : ", str(len(YKID)), ")")
    
    # YK_TwitterID をダウンロード
    dbx.files_download_to_file("cper_bot/YK/TwitterID.txt", "/cper_bot/YK/TwitterID.txt")
    with open("cper_bot/YK/TwitterID.txt", "r") as f:
        YK_TwitterID.clear()
        for id in f:
            YK_TwitterID.append(id.rstrip("\n"))
    print("cper_bot-YK-register: Downloaded YK_TwitterID (size : ", str(len(YK_TwitterID)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global YKID
    global YK_TwitterID
    global YK_listFixedFlag

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
        
    if YK_listFixedFlag:
        # YKID をアップロード
        with open("cper_bot/YK/YKID.txt", "w") as f:
            for id in YKID:
                f.write(str(id) + "\n")
        with open("cper_bot/YK/YKID.txt", "rb") as f:
            dbx.files_delete("/cper_bot/YK/YKID.txt")
            dbx.files_upload(f.read(), "/cper_bot/YK/YKID.txt")
            print("cper_bot-YK-register: Uploaded YKID (size : ", str(len(YKID)), ")")
        with open("cper_bot/YK/YKID.txt", "rb") as f:
            dbx.files_upload(f.read(), "/_backup/YK/YKID/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".txt")
            print("cper_bot-YK-register: Uploaded YKID (for backup " + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ") (size : ", str(len(YKID)), ")")

        # YK_TwitterID をアップロード
        with open("cper_bot/YK/TwitterID.txt", "w") as f:
            for id in YK_TwitterID:
                f.write(str(id) + "\n")
        with open("cper_bot/YK/TwitterID.txt", "rb") as f:
            dbx.files_delete("/cper_bot/YK/TwitterID.txt")
            dbx.files_upload(f.read(), "/cper_bot/YK/TwitterID.txt")
            print("cper_bot-YK-register: Uploaded YK_TwitterID (size : ", str(len(YK_TwitterID)), ")")
        with open("cper_bot/YK/TwitterID.txt", "rb") as f:
            dbx.files_upload(f.read(), "/_backup/YK/TwitterID/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".txt")
            print("cper_bot-YK-register: Uploaded YK_TwitterID (for backup " + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ") (size : ", str(len(YK_TwitterID)), ")")
    
# list 内の要素の添え字を返す（無い場合は -1）
def myIndex(x, l):
    if x in l:
        return l.index(x)
    else:
        return -1

# YK ID 登録・解除
def register(ykID, twitterID, flag):

    print("cper_bot-YK-register: ----- YK-register Start -----")

    # グローバル変数
    global YKID
    global YK_TwitterID
    global YK_listFixedFlag
        
    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # データをダウンロード
    downloadFromDropbox()

    # 登録・解除処理
    YK_listFixedFlag = False
    tweetText = ""
    if flag == 0:
        if checkYKID(ykID):
            YKID.append(ykID)
            YK_TwitterID.append(twitterID)
            tweetText = "@" + str(twitterID) + " yukicoder ID を登録しました！\n";
            print("cper_bot-YK-register: Registered new YK ID : " + ykID)
            YK_listFixedFlag = True
        else:
            tweetText = "@" + str(twitterID) + " 正しい yukicoder ID ではありません！\n"
            print("cper_bot-YK-register: Rejected to YK-register new YK ID : " + ykID)
    if flag == 1:
        if checkYKID(ykID):
            if myIndex(ykID, YKID) != -1 and myIndex(str(twitterID), YK_TwitterID) != -1 and myIndex(ykID, YKID) == myIndex(str(twitterID), YK_TwitterID):
                YKID.pop(myIndex(str(twitterID), YK_TwitterID))
                YK_TwitterID.pop(myIndex(str(twitterID), YK_TwitterID))
                tweetText = "@" + str(twitterID) + " yukicoder ID を登録解除しました！\n"
                print("cper_bot-YK-register: Unregistered YK ID : " + ykID)
                YK_listFixedFlag = True
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
