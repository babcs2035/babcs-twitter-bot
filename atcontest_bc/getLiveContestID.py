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
    session = requests.Session()
    request = session.get(url = "https://atcoder-api.appspot.com/contests")
    contestsJsonData = json.loads(request.text)
    print("atcontest_bc-getLiveContestID: Downloaded contestsJsonData")
    
    results = []
    for contest in contestsJsonData:
        date1 = epoch_to_datetime(contest["startTimeSeconds"])
        date2 = epoch_to_datetime(contest["startTimeSeconds"] + contest["durationSeconds"])
        now = datetime.datetime.today()
        if date1 <= now and now <= date2:
            results.append(contest["id"])

    print("atcontest_bc-getLiveContestID: found " + str(len(results)) + " contests")
    return results

if __name__ == '__main__':
    print("atcontest_bc-getLiveContestID: Running as debug...")
    print(get())
    print("atcontest_bc-getLiveContestID: Debug finished")
