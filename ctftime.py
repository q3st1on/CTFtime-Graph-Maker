import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import numpy as np
import requests
import datetime
import time
import json

TEAMTRACK = 10
COUNTRY = "AU"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

def getCTFs():
    res = {}
    year = int(datetime.date.today().year)
    starttime = int(time.mktime(datetime.datetime.strptime(f"01/01/{year}", "%d/%m/%Y").timetuple()))
    endtime = int(time.mktime(datetime.datetime.strptime(f"01/01/{year+1}", "%d/%m/%Y").timetuple()))
    ctfs = json.loads(requests.get(f'https://ctftime.org/api/v1/events/?limit=1000&start={starttime}&finish={endtime}', headers=HEADERS).content.decode())
    for i in ctfs:
        res[i["title"].strip()] = {"id": i["id"], "ctf_id": i["ctf_id"], "start": i["start"], "finish": i["finish"], "paricipants": i["participants"]}
    return res

def getTeamResults(ID):
    page = requests.get(f'https://ctftime.org/team/{ID}', headers=HEADERS)
    table = BeautifulSoup(page.content, 'html.parser').find(id="rating_2023")
    strings = list(filter(('*').__ne__, [text for text in table.find(class_="table table-striped").stripped_strings]))
    placements = [strings[i:i+4] for i in range(0, len(strings), 4)]
    placements.pop(0)
    return placements

def getCountryStats(country):
    page = requests.get(f'https://ctftime.org/stats/{country}', headers=HEADERS)
    soup = BeautifulSoup(page.content, 'html.parser')
    strings = list(filter(('*').__ne__, [text for text in soup.find(class_="table table-striped").stripped_strings]))
    placements = [strings[i:i+5] for i in range(0, len(strings), 5)]
    placements.pop(0)
    teams = [i[2] for i in placements[0:TEAMTRACK]]
    for i in range(TEAMTRACK):
        working = []
        working.append(teams[i])
        working.append(str(soup.find_all("a", string=teams[i])).split('"')[1][6:])
        teams[i] = working
    return teams

def getData():
    ctfs = getCTFs()

    teams = (getCountryStats(COUNTRY))
    for i in range(TEAMTRACK):
        placements = getTeamResults(teams[i][1])
        teams[i] = [teams[i][0], teams[i][1], placements]

    for x in range(TEAMTRACK):
        for i in range(len(teams[x][2])):
            teams[x][2][i].append(datetime.datetime.strftime(datetime.datetime.strptime((ctfs[teams[x][2][i][1]]["finish"].replace(':', '')), "%Y-%m-%dT%H%M%S%z"),"%W"))

    days = ["Day"]
    for i in range(int(datetime.date.today().strftime("%W"))+1):
        days.append(i)

    data = [days]
    for i in teams:
        working = [i[0]]
        for j in range(int(datetime.date.today().strftime("%W"))+1):
            ctfs = [x for x in i[2] if int(x[4])<=j]
            if len(ctfs) <= 10:
                working.append(round(sum([float(y[3]) for y in ctfs]), 3))
            else:
                placements = np.array(ctfs)
                placements = placements[np.array(placements[:,3], dtype=float).argsort()]
                placements = [f for f in reversed([list(f) for f in list(placements)])][0:10]
                working.append(round(sum([float(i[3]) for i in placements]), 3))
        data.append(working)
    return data

def plotData(data):
    plt.title(f'{COUNTRY} top {TEAMTRACK} CTFtime teams for {datetime.date.today()}')
    x = data[0][1:]
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.xlabel('Week')
    plt.ylabel('CTFtime score')
    for i in range(len(data[1:])):
        plt.plot(x, data[i+1][1:], label = data[i+1][0])
        try:
            plt.fill_between(x, data[i+1][1:], data[i+2][1:], alpha=0.5)
        except:
            if i == TEAMTRACK-1:
                plt.fill_between(x, data[i+1][1:], alpha=0.5)
    plt.legend(facecolor='black', framealpha=0)
    plt.show()

data = getData()
print(data)
plotData(data)