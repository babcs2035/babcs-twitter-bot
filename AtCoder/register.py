# import
import os
import datetime
import urllib.request
import dropbox

# グローバル変数
AtCoderID = []
AtCoder_TwitterID = []
AtCoder_listFixedFlag = False

# AtCoder ID が存在するか確認
def checkAtCoderID(atcoderID):

    try:
        html = urllib.request.urlopen("https://atcoder.jp/users/" + atcoderID)
        print("AtCoder-register: " + atcoderID + " is correct AtCoder ID")
        return True
    except:
        print("AtCoder-register: " + atcoderID + " is not correct AtCoder ID")
        return False

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global AtCoderID
    global AtCoder_TwitterID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # AtCoderID をダウンロード
    dbx.files_download_to_file("AtCoder/AtCoderID.txt", "/AtCoder/AtCoderID.txt")
    with open("AtCoder/AtCoderID.txt", "r") as f:
        AtCoderID.clear()
        for id in f:
            AtCoderID.append(id.rstrip("\n"))
    print("AtCoder-register: Downloaded AtCoderID (size : ", str(len(AtCoderID)), ")")
    
    # AtCoder_TwitterID をダウンロード
    dbx.files_download_to_file("AtCoder/TwitterID.txt", "/AtCoder/TwitterID.txt")
    with open("AtCoder/TwitterID.txt", "r") as f:
        AtCoder_TwitterID.clear()
        for id in f:
            AtCoder_TwitterID.append(id.rstrip("\n"))
    print("AtCoder-register: Downloaded AtCoder_TwitterID (size : ", str(len(AtCoder_TwitterID)), ")")

# Dropbox にアップロード
def uploadToDropbox():
    
    # グローバル変数
    global AtCoderID
    global AtCoder_TwitterID
    global AtCoder_listFixedFlag

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()
        
    if AtCoder_listFixedFlag:
        # AtCoderID をアップロード
        with open("AtCoder/AtCoderID.txt", "w") as f:
            for id in AtCoderID:
                f.write(str(id) + "\n")
        with open("AtCoder/AtCoderID.txt", "rb") as f:
            dbx.files_delete("/AtCoder/AtCoderID.txt")
            dbx.files_upload(f.read(), "/AtCoder/AtCoderID.txt")
            print("AtCoder-register: Uploaded AtCoderID (size : ", str(len(AtCoderID)), ")")
        with open("AtCoder/AtCoderID.txt", "rb") as f:
            dbx.files_upload(f.read(), "/_backup/AtCoder/AtCoderID/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".txt")
            print("AtCoder-register: Uploaded AtCoderID (for backup " + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ") (size : ", str(len(AtCoderID)), ")")

        # AtCoder_TwitterID をアップロード
        with open("AtCoder/TwitterID.txt", "w") as f:
            for id in AtCoder_TwitterID:
                f.write(str(id) + "\n")
        with open("AtCoder/TwitterID.txt", "rb") as f:
            dbx.files_delete("/AtCoder/TwitterID.txt")
            dbx.files_upload(f.read(), "/AtCoder/TwitterID.txt")
            print("AtCoder-register: Uploaded AtCoder_TwitterID (size : ", str(len(AtCoder_TwitterID)), ")")
        with open("AtCoder/TwitterID.txt", "rb") as f:
            dbx.files_upload(f.read(), "/_backup/AtCoder/TwitterID/" + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ".txt")
            print("AtCoder-register: Uploaded AtCoder_TwitterID (for backup " + str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")) + ") (size : ", str(len(AtCoder_TwitterID)), ")")
    
# list 内の要素の添え字を返す（無い場合は -1）
def myIndex(x, l):
    if x in l:
        return l.index(x)
    else:
        return -1

# AtCoder ID 登録・解除
def register(atcoderID, twitterID, flag):

    print("AtCoder-register: ----- AtCoder-register Start -----")

    # グローバル変数
    global AtCoderID
    global AtCoder_TwitterID
    global AtCoder_listFixedFlag
        
    # 時刻表示を作成
    timeStamp = datetime.datetime.today()
    timeStamp = str(timeStamp.strftime("%Y/%m/%d %H:%M"))
    
    # データをダウンロード
    downloadFromDropbox()

    # 登録・解除処理
    AtCoder_listFixedFlag = False
    tweetText = ""
    if flag == 0:
        if checkAtCoderID(atcoderID):
            AtCoderID.append(atcoderID)
            AtCoder_TwitterID.append(twitterID)
            tweetText = "@" + str(twitterID) + " AtCoder ID を登録しました！\n";
            print("AtCoder-register: Registered new AtCoder ID : " + atcoderID)
            AtCoder_listFixedFlag = True
        else:
            tweetText = "@" + str(twitterID) + " 正しい AtCoder ID ではありません！\n"
            print("AtCoder-register: Rejected to AtCoder-register new AtCoder ID : " + atcoderID)
    if flag == 1:
        if checkAtCoderID(atcoderID):
            if myIndex(atcoderID, AtCoderID) != -1 and myIndex(str(twitterID), AtCoder_TwitterID) != -1 and myIndex(atcoderID, AtCoderID) == myIndex(str(twitterID), AtCoder_TwitterID):
                AtCoderID.pop(myIndex(str(twitterID), AtCoder_TwitterID))
                AtCoder_TwitterID.pop(myIndex(str(twitterID), AtCoder_TwitterID))
                tweetText = "@" + str(twitterID) + " AtCoder ID を登録解除しました！\n"
                print("AtCoder-register: Unregistered AtCoder ID : " + atcoderID)
                AtCoder_listFixedFlag = True
            else:
                tweetText = "@" + str(twitterID) + " この AtCoder ID は登録されていません！\n"
                print("AtCoder-register: Rejected to unregister AtCoder ID : " + atcoderID)
        else:
            tweetText = "@" + str(twitterID) + " 正しい AtCoder ID ではありません！\n"
            print("AtCoder-register: Rejected to unregister AtCoder ID : " + atcoderID)


    # 変更されたデータをアップロード
    uploadToDropbox()
    
    print("AtCoder-register: ----- AtCoder-register End -----")
    return tweetText
