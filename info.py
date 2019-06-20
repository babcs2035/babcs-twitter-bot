# import
import os
import dropbox

AtCoderID = []
AOJID = []
CFID = []
YKID = []

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
    print("info: Downloaded AtCoderID (size : ", str(len(AtCoderID)), ")")
    
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

    downloadFromDropbox()

    tweetText = ""
    tweetText += "AtCoder ID 登録数：" + str(len(AtCoderID)) + "\n"
    tweetText += "AOJ ID 登録数：" + str(len(AOJID)) + "\n"
    tweetText += "Codeforces ID 登録数：" + str(len(CFID)) + "\n"
    tweetText += "yukicoder ID 登録数：" + str(len(YKID)) + "\n"
    return tweetText

if __name__ == '__main__':
    print("info: Running as debug...")
    info()
    print("info: Debug finished")
