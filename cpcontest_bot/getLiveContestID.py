# import
from bs4 import BeautifulSoup
import json
import requests
import time
import datetime
import os


def get():

    # ログイン
    session = requests.Session()
    loginHTML = session.get("https://atcoder.jp/login")
    loginHTML.raise_for_status()
    loginData = BeautifulSoup(loginHTML.text, "html.parser")
    payload = {
        "username": os.environ["ATCODER_ID"],
        "password": os.environ["ATCODER_PASSWORD"]
    }
    payload["csrf_token"] = loginData.find(
        attrs={"name": "csrf_token"}).get("value")
    session.post("https://atcoder.jp/login", data=payload)

    # コンテスト一覧から取得
    results = []
    contestsHTML = session.get("https://atcoder.jp/contests/?lang=ja")
    try:
        contestsHTML.raise_for_status()
        contestsData = BeautifulSoup(contestsHTML.text, "html.parser")
    except:
        print("cpcontest_bot-getLiveContestID: contestsHTML Error")
        return
    divs = contestsData.find_all("div", class_="col-lg-9 col-md-8")
    if str(divs[0].contents[1].contents[1].contents[0]) == "開催中のコンテスト":
        a = divs[0].contents[1].find_all("a")
        for index in range(1, len(a), 2):
            contestID = str(a[index].attrs["href"][10:])
            results.append(contestID)
            try:
                contestHTML = session.get(
                    "https://atcoder.jp/contests/" + contestID + "/standings/team/json")
                contestHTML.raise_for_status()
            except:
                continue
            results.append(contestID + "_team")

    print("cpcontest_bot-getLiveContestID: found " +
                    str(len(results)) + " contests")
    return results


if __name__ == '__main__':
    print("cpcontest_bot-getLiveContestID: Running as debug...")
    print(get())
    print("cpcontest_bot-getLiveContestID: Debug finished")
