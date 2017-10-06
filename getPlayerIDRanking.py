import sys
import requests
from bs4 import BeautifulSoup
import sqlite3
import random
from datetime import date, datetime, timedelta
import time
import re
from multiprocessing.dummy import Pool as ThreadPool
import os
import threading

TIMEOUT = 10
TOTAL_PLAYER_NUM = 1000
TOTAL_WEEKS = 918
SLEEPTIME = 3

def getHTML(url):
    connected = False
    while not connected:
        try:
            with open('user-agents.txt', 'r') as agents:
                user_agents = agents.readlines()
            with open('proxies.txt', 'r') as p:
                proxies = p.readlines()
            headers = {'User-Agent': random.choice(user_agents).strip()}
            proxy = random.choice(proxies).strip()
            my_proxy = {proxy.split(':')[0]: proxy}
            html = requests.get(url, timeout = TIMEOUT, \
            headers = headers, proxies = my_proxy).text
            time.sleep(random.uniform(SLEEPTIME-1,SLEEPTIME+1))
            connected = True
            print threading.current_thread().name, my_proxy, url
        except IOError:
            print threading.current_thread().name, "Connection error! (Check proxy)", url
    return html.encode('utf-8')

# get ranking on any date
# input: a single date in string format
# saves the rankings of the input date in a txt file named after the date
def getHTMLRanking(rankingDate):
    f = "./rankingHistory/" + str(rankingDate) + ".txt"
    date = rankingDate
    rankingsURL = 'http://www.atpworldtour.com/en/rankings/singles'
    historyRankingURL = rankingsURL + '?rankDate=' + date + '&rankRange=1-' + str(TOTAL_PLAYER_NUM)

    def validFile(f):
        if os.path.isfile(f):
            ATPPlayerRank = open(f, 'r').readlines()
            if len(ATPPlayerRank)== TOTAL_PLAYER_NUM and \
            ATPPlayerRank[TOTAL_PLAYER_NUM-1].startswith(rankingDate):
                return  True
        return False

    while not validFile(f):
        ATPPlayerRank = open(f, 'w')
        playerTag = BeautifulSoup(getHTML(historyRankingURL), 'lxml').find_all('td', 'player-cell')
        if (playerTag is not None and len(playerTag) >= TOTAL_PLAYER_NUM):
            for r in range(0, TOTAL_PLAYER_NUM):
                playerURL = playerTag[r].contents[1].get('href', None).split("/")
                playerName = playerTag[r].find('a').contents[0]
                playerstr = date + "," + str(r+1) + "," + playerURL[3] + \
                    "," + playerURL[4] + "," + str(playerName) + "\n"
                ATPPlayerRank.write(playerstr)
    print rankingDate, 'is valid!'


# Process the raw ranking file and fill in any missing dates of ranking
def fillMissingDates():
    def getinfo(week_str):
        _, rank, _, player, _ = week_str.split(',')
        return [player, rank]
    def getdate(week_str):
        wk, _, _, _, _ = week_str.split(',')
        week = datetime.strptime(wk, "%Y-%m-%d").date()
        return week

    ranking_files = os.listdir('./rankingHistory')#[0:TOTAL_WEEKS]
    all_rankings_file = './rankingHistory/allRankings.txt'

    with open(all_rankings_file, 'w') as rk:
        for f in ranking_files:
            if (f.endswith('.txt') and f.startswith('20')):
                with open('./rankingHistory/' + f) as infile:
                    rk.write(infile.read())

    with open(all_rankings_file, 'r') as f:
        lines = f.readlines()

    fullRankingDates = []
    currDate = getdate(lines[0])
    for i in range(0, TOTAL_WEEKS):
        fullRankingDates.append(currDate)
        currDate += timedelta(days = 7)
    fullRankingDates = sorted(fullRankingDates * TOTAL_PLAYER_NUM)

    i, j = 0, 0
    fnew = open('./rankingHistory/ATPPlayerFullRank.txt', 'w')
    while (i < len(lines) and j < len(fullRankingDates)):
        if (getdate(lines[i]) == fullRankingDates[j]):
            player, rank = getinfo(lines[i])
            s = fullRankingDates[j].strftime('%Y-%m-%d') + '\t' + player + '\t' + rank + '\n'
            fnew.write(s)
            i+=1
            j+=1
        else:
            i -= 1000
            for k in range(0, TOTAL_PLAYER_NUM):
                player, rank = getinfo(lines[i])
                s = fullRankingDates[j].strftime('%Y-%m-%d') + '\t' + player + '\t' + rank + '\n'
                fnew.write(s)
                i+=1
                j+=1
    fnew.close()

# Use multi-threading to crawl all ranking info
def getAllRankings():
    rankingsURL = 'http://www.atpworldtour.com/en/rankings/singles'
    playerRankingHtml = getHTML(rankingsURL)
    datesoup = BeautifulSoup(playerRankingHtml, 'lxml')
    dates = []
    for datevalue in datesoup('ul', "dropdown")[0].find_all('li'):
        dates.append(datevalue.get('data-value'))
    pool = ThreadPool(8)
    pool.map(getRanking, dates)
    pool.close()
    pool.join()
    fillMissingDates()

# if __name__ == "__main__":
    # getHTMLRanking('2002-04-08')
