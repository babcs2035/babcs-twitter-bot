# import
import os
import dropbox
import pickle

AtCoderIDs = []
AOJID = []
CFID = []
YKID = []

# Dropbox からダウンロード
def downloadFromDropbox():
    
    # グローバル変数
    global AtCoderIDs
    global AOJID
    global CFID
    global YKID

    # Dropbox オブジェクトの生成
    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    # AtCoderIDs をダウンロード
    dbx.files_download_to_file("AtCoder/AtCoderIDs.txt", "/AtCoder/AtCoderIDs.txt")
    with open("AtCoder/AtCoderIDs.txt", "rb") as f:
        AtCoderIDs = pickle.load(f)
    print("info: Downloaded AtCoderIDs (size : ", str(len(AtCoderIDs)), ")")
    
    # AOJID をダウンロード
    dbx.files_download_to_file("AOJ/AOJID.txt", "/AOJ/AOJID.txt")
    with open("AOJ/AOJID.txt", "r") as f:
        AOJID.clear()
        for id in f:
            AOJID.append(id.rstrip("\n"))
    print("info: Downloaded AOJID (size : ", str(len(AOJID)), ")")

    # CFID をダウンロード
    dbx.files_download_to_file("CF/CFID.txt", "/CF/CFID.txt")
    with open("CF/CFID.txt", "r") as f:
        CFID.clear()
        for id in f:
            CFID.append(id.rstrip("\n"))
    print("info: Downloaded CFID (size : ", str(len(CFID)), ")")

    # YKID をダウンロード
    dbx.files_download_to_file("YK/YKID.txt", "/YK/YKID.txt")
    with open("YK/YKID.txt", "r") as f:
        YKID.clear()
        for id in f:
            YKID.append(id.rstrip("\n"))
    print("info: Downloaded YKID (size : ", str(len(YKID)), ")")

def info():
    
    # グローバル変数
    global AtCoderIDs
    global AOJID
    global CFID
    global YKID

    downloadFromDropbox()

    tweetText = ""
    tweetText += "AtCoder ID 登録数：" + str(len(AtCoderIDs)) + "\n"
    tweetText += "AOJ ID 登録数：" + str(len(AOJID)) + "\n"
    tweetText += "Codeforces ID 登録数：" + str(len(CFID)) + "\n"
    tweetText += "yukicoder ID 登録数：" + str(len(YKID)) + "\n"
    return tweetText

if __name__ == '__main__':
    print("info: Running as debug...")
    info()
    print("info: Debug finished")
