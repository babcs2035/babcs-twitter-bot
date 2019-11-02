# import
import datetime
import time
import requests
import json
from bs4 import BeautifulSoup

def epoch_to_datetime(epoch):
    return datetime.datetime(*time.localtime(epoch)[:6])

def get():

    # コンテスト一覧から取得
    results = []
    contestsHTML = requests.get("https://atcoder.jp/contests/?lang=ja")
    try:
        contestsHTML.raise_for_status()
        contestsData = BeautifulSoup(contestsHTML.text, "html.parser")
    except:
        print("atcontest_bc-getLiveContestID: contestsHTML Error")
        return
    divs = contestsData.find_all("div", class_ = "col-lg-9 col-md-8")
    if str(divs[0].contents[1].contents[1].contents[0]) == "開催中のコンテスト":
        a = divs[0].contents[1].find_all("a")
        for index in range(1, len(a), 2):
            results.append(str(a[index].attrs["href"][10:]))

    print("atcontest_bc-getLiveContestID: found " + str(len(results)) + " contests")
    return results

if __name__ == '__main__':
    print("atcontest_bc-getLiveContestID: Running as debug...")
    print(get())
    print("atcontest_bc-getLiveContestID: Debug finished")
