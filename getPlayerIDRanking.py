import sys
import requests
from bs4 import BeautifulSoup
import sqlite3
import numpy as np
from datetime import date, datetime, timedelta
import time
import re
from multiprocessing.dummy import Pool as ThreadPool

SLEEPTIME = 0.1
TOTAL_PLAYER_NUM = 10
TOTAL_WEEKS = 10
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

# get player ID
# url = 'http://www.atpworldtour.com/en/rankings/singles?rankDate=2017-06-26&rankRange=1-' + str(TOTAL_PLAYER_NUM)
#
# playerPageHtml = requests.get(url, headers=headers).text
# soup = BeautifulSoup(playerPageHtml, "lxml")
#
# ATPPlayerID = open("ATPPlayerID.txt", 'w')
# playerList = soup("td", "player-cell")
#
# for playerLink in playerList:
#     playerURL =  playerLink.find("a")["href"].split("/")
#     playerstr = playerURL[3] + "\t" + playerURL[4] + "\n"
#     ATPPlayerID.write(playerstr)
# ATPPlayerID.close()

# get ranking on any date
# input: a single date in string format
# saves the rankings of the input date in a txt file named after the date
def getRanking(rankingDate):
    time.sleep(np.random.rand()*5)
    f = "./rankingHistory/" + str(rankingDate) + ".txt"
    ATPPlayerRank = open(f, 'w')
    date = rankingDate
    rankingsURL = 'http://www.atpworldtour.com/en/rankings/singles'
    historyRankingURL = rankingsURL + '?rankDate=' + date + '&rankRange=1-' + str(TOTAL_PLAYER_NUM)
    historyRankingHtml = requests.get(historyRankingURL, headers = headers).text
    playerTag = BeautifulSoup(historyRankingHtml, 'lxml').find_all('td', 'player-cell')
    print date
    for r in range(0, TOTAL_PLAYER_NUM):
        try:
            playerURL = playerTag[r].contents[1].get('href', None).split("/")
            playerName = playerTag[r].find('a').contents[0]
            playerstr = date + "\t" + str(r+1) + "\t" + playerURL[3] + \
                "\t" + playerURL[4] + "\t" + str(playerName) + "\n"
            # print playerstr
        except:
            playerstr = 'data not found'
        ATPPlayerRank.write(playerstr)
    ATPPlayerRank.close()

# Process the raw ranking file and fill in any missing dates of ranking
def fillMissingDates(dateList):
    filenames = []
    for i in dateList:
        s = i + ".txt"
        filenames.append(s)
    with open('./rankingHistory/allRankings.txt', 'w') as rankfile:
        for fname in filenames:
            with open("./rankingHistory/"+ fname) as infile:
                rankfile.write(infile.read())

        f = open(rankfile, 'r')
        lines = f.readlines()

        rankingDates = []
        currDate = getdate(lines[0])

        for i in range(0, TOTAL_WEEKS):
            rankingDates.append(currDate)
            currDate -= timedelta(days = 7)

        def getinfo(week_str):
            _, rank, _, player, _ = week_str.split("\t")
            return [player, rank]
        def getdate(week_str):
            wk, _, _, _, _ = week_str.split("\t")
            week = datetime.strptime(wk, "%Y-%m-%d").date()
            return week

        i = 0
        fnew = open('ATPPlayerFullRank.txt', 'w')
        for j in range(0, len(rankingDates)):
            while (re.findall('\d', lines[i]) == []):
                i += 1
            if (getdate(lines[i]) == rankingDates[j]):
                for k in range(0, TOTAL_PLAYER_NUM):
                    player, rank = getinfo(lines[i])
                    s = rankingDates[j].strftime('%Y-%m-%d') + '\t' + player + '\t' + rank + '\n'
                    fnew.write(s)
                    i+=1
            else:
                offset = i
                for k in range(0, TOTAL_PLAYER_NUM):
                    player, rank = getinfo(lines[i])
                    s = rankingDates[j].strftime('%Y-%m-%d') + '\t' + player + '\t' + rank + '\n'
                    fnew.write(s)
                    i+=1
                i = offset
        f.close()
        fnew.close()

# Use multi-threading to crawl all ranking info
def getAllRankings():
    rankingsURL = 'http://www.atpworldtour.com/en/rankings/singles'
    playerRankingHtml = requests.get(rankingsURL, headers = headers).text
    datesoup = BeautifulSoup(playerRankingHtml, 'lxml')
    dates = []
    for datevalue in datesoup('ul', "dropdown")[0].find_all('li'):
        dates.append(datevalue.get('data-value'))
    dates = dates[1 : TOTAL_WEEKS + 1]

    pool = ThreadPool(2)
    pool.map(getRanking, dates)
    pool.close()
    pool.join()
    fillMissingDates(dates)

def createRankingDB():
    conn = sqlite3.connect('PlayerRanking.sqlite')
    cur = conn.cursor()

    cur.execute('''
    DROP TABLE IF EXISTS PlayerRanking''')

    cur.execute('''
    CREATE TABLE PlayerRanking (
        week_year   DATETIME,
        player_id TEXT,
        player_rank INTEGER
        )''')
    ph = open('ATPPlayerFullRank.txt')
    for line in ph:
        pieces = line.split()
        cur.execute('''INSERT INTO PlayerRanking (week_year, player_id, player_rank)
                VALUES (?, ?, ?)''', (pieces[0], pieces[1], pieces[2]))
    conn.commit()
    cur.close()

getAllRankings()
# createRankingDB()
