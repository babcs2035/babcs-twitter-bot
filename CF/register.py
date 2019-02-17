# import
import os
import datetime
import urllib.request
import dropbox

# グローバル変数
CFID = []
CF_TwitterID = []
CF_listFixedFlag = False

# CF ID が存在するか確認
def checkCFID(cfID):

    try:
        html = urllib.request.urlopen("https://codeforces.com/api/user.status?handle=" + cfID)
        print("CF-register: " + cfID + " is correct Codeforces ID")
        return True
    except:
        print("CF-register: " + cfID + " is not correct Codeforces ID")
        return False

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global CFID
    global CF_TwitterID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # CFID をダウンロード
    dbx.files_download_to_file("CF/CFID.txt", "/CF/CFID.txt")
    with open("CF/CFID.txt", "r") as f:
        CFID.clear()
        for id in f:
            CFID.append(id.rstrip("\n"))
    print("CF-register: Downloaded CFID (size : ", str(len(CFID)), ")")
    
    # CF_TwitterID をダウンロード
    dbx.files_download_to_file("CF/TwitterID.txt", "/CF/TwitterID.txt")
    with open("CF/TwitterID.txt", "r") as f:
        CF_TwitterID.clear()
        for id in f:
            CF_TwitterID.append(id.rstrip("\n"))
    print("CF-register: Downloaded CF_TwitterID (size : ", str(len(CF_TwitterID)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global CFID
    global CF_TwitterID
    global CF_listFixedFlag

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
        
    if CF_listFixedFlag:
        # CFID をアップロード
        with open("CF/CFID.txt", "w") as f:
            for id in CFID:
                f.write(str(id) + "\n")
        with open("CF/CFID.txt", "rb") as f:
            dbx.files_delete("/CF/CFID.txt")
            dbx.files_upload(f.read(), "/CF/CFID.txt")
            print("CF-register: Uploaded CFID (size : ", str(len(CFID)), ")")
        with open("CF/CFID.txt", "rb") as f:
            dbx.files_upload(f.read(), "/_backup/CF/CFID/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".txt")
            print("CF-register: Uploaded CFID (for backup " + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ") (size : ", str(len(CFID)), ")")

        # CF_TwitterID をアップロード
        with open("CF/TwitterID.txt", "w") as f:
            for id in CF_TwitterID:
                f.write(str(id) + "\n")
        with open("CF/TwitterID.txt", "rb") as f:
            dbx.files_delete("/CF/TwitterID.txt")
            dbx.files_upload(f.read(), "/CF/TwitterID.txt")
            print("CF-register: Uploaded CF_TwitterID (size : ", str(len(CF_TwitterID)), ")")
        with open("CF/TwitterID.txt", "rb") as f:
            dbx.files_upload(f.read(), "/_backup/CF/TwitterID/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".txt")
            print("CF-register: Uploaded CF_TwitterID (for backup " + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ") (size : ", str(len(CF_TwitterID)), ")")
    
# list 内の要素の添え字を返す（無い場合は -1）
def myIndex(x, l):
    if x in l:
        return l.index(x)
    else:
        return -1

# CF ID 登録・解除
def register(cfID, twitterID, flag):

    print("CF-register: ----- CF-register Start -----")

    # グローバル変数
    global CFID
    global CF_TwitterID
    global CF_listFixedFlag
        
    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # データをダウンロード
    downloadFromDropbox()

    # 登録・解除処理
    CF_listFixedFlag = False
    tweetText = ""
    if flag == 0:
        if checkCFID(cfID):
            CFID.append(cfID)
            CF_TwitterID.append(twitterID)
            tweetText = "@" + str(twitterID) + " Codeforces ID を登録しました！\n";
            print("CF-register: Registered new CF ID : " + cfID)
            CF_listFixedFlag = True
        else:
            tweetText = "@" + str(twitterID) + " 正しい Codeforces ID ではありません！\n"
            print("CF-register: Rejected to CF-register new CF ID : " + cfID)
    if flag == 1:
        if checkCFID(cfID):
            if myIndex(cfID, CFID) != -1 and myIndex(str(twitterID), CF_TwitterID) != -1 and myIndex(cfID, CFID) == myIndex(str(twitterID), CF_TwitterID):
                CFID.pop(myIndex(str(twitterID), CF_TwitterID))
                CF_TwitterID.pop(myIndex(str(twitterID), CF_TwitterID))
                tweetText = "@" + str(twitterID) + " Codeforces ID を登録解除しました！\n"
                print("CF-register: Unregistered CF ID : " + cfID)
                CF_listFixedFlag = True
            else:
                tweetText = "@" + str(twitterID) + " この Codeforces ID は登録されていません！\n"
                print("CF-register: Rejected to unregister CF ID : " + cfID)
        else:
            tweetText = "@" + str(twitterID) + " 正しい Codeforces ID ではありません！\n"
            print("CF-register: Rejected to unregister CF ID : " + cfID)

    # 変更されたデータをアップロード
    uploadToDropbox()
    
    print("CF-register: ----- CF-register End -----")
    return tweetText
