import os
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import dropbox
from dropbox.files import WriteMode
import pickle
import requests
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage
import gc

data = []

def download():
    
    global data

    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    dbx.files_download_to_file("LINE/data.txt", "/LINE/data.txt")
    with open("LINE/data.txt", "rb") as f:
        data = pickle.load(f)
        del f
        gc.collect()

def upload():

    global data

    dbx = dropbox.Dropbox(os.environ["DROPBOX_KEY"])
    dbx.users_get_current_account()

    with open("LINE/data.txt", "wb") as f:
        pickle.dump(data, f)
        del f
        gc.collect()
    with open("LINE/data.txt", "rb") as f:
        dbx.files_upload(f.read(), "/LINE/data.txt", mode = dropbox.files.WriteMode.overwrite)
        del f
        gc.collect()

sched = BlockingScheduler(
    executors = {
        'threadpool' : ThreadPoolExecutor(max_workers = 5),
        'processpool' : ProcessPoolExecutor(max_workers = 1)
    }
)

@sched.scheduled_job('interval', minutes = 5, executor = 'threadpool')
def scheduled_job():

    global data

    # Detect updates
    download()
    pageHTML = requests.get("https://www.c.u-tokyo.ac.jp/zenki/news/index.html")
    results = []
    try:
        pageHTML.raise_for_status()
        pageData = BeautifulSoup(pageHTML.text, "html.parser")
        pageDiv = pageData.find_all(id = "newslist2")
        pageDates = pageDiv[0].find_all("dt")
        pageTitles = pageDiv[0].find_all("dd")

        nums = len(pageDates)
        index = 0
        newData = []
        while index < nums:
            date = str(pageDates[index].contents[0])
            title = str(pageTitles[index].contents[0].contents[0])
            url = str(pageTitles[index].contents[0].attrs["href"])
            if url[0] != 'h':
                url = "https://www.c.u-tokyo.ac.jp" + url
            newData.append((date, title, url))
            index += 1

        for row in newData:
            if row not in data:
                results.append(row)
    except:
        print("line_bot: pageHTML Error")
        return

    # Send LINE messages
    line_bot_api = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
    for row in results:
        message = str("お知らせが更新されました：\n" + row[1] + "\n" + row[2])
        line_bot_api.broadcast(TextSendMessage(text = message))
        if os.environ["LINE_GROUP_ID"] != "NULL":
            line_bot_api.push_message(os.environ["LINE_GROUP_ID"], TextSendMessage(text = message))
        print("line_bot: Detected new information (title : " + row[1] + ")\n")

    # Update the data
    data = newData
    upload()

    del newData
    del pageHTML
    del results
    gc.collect()

# Run
sched.start()
