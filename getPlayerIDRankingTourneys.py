'''
Crawl and store the following information in text files:
1. Player rankings on every Monday since year 2000
2. The basic information of all tournaments since year 2000

@author: Chenyang Wu
'''

import sys
import requests
from bs4 import BeautifulSoup
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

# A reliable method to get content of an HTML page, change proxy every time
# until success
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
# output: none
def getRanking(rankingDate):
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
# based on the previous valid ranking
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
    dates = dates[0:TOTAL_WEEKS]
    pool = ThreadPool(8)
    pool.map(getRanking, dates)
    pool.close()
    pool.join()
    fillMissingDates()

# Given a year in 4-digit int format, crawl the information of all tourneys
# of that year and store in text files
def getTournamentsInYear(year):
    year_url = "http://www.atpworldtour.com/en/scores/results-archive?year=" + str(year)
    yearSoup = BeautifulSoup(getHTML(year_url), 'lxml')
    tourneyInfo = yearSoup.find_all('tr', class_='tourney-result')
    def findInfo(tag, classname):
        return tag.find(class_=classname).text.strip()

    s = ''
    tourneyfile =  open('./tourneyHistory/'+str(year)+'tourneys.txt', 'w')
    for tourney in tourneyInfo:
        tourney_title = findInfo(tourney, 'tourney-title')
        tourney_location = findInfo(tourney, 'tourney-location')
        tourney_dates = findInfo(tourney, 'tourney-dates')
        # t_id = tourney.find('a')['href']
        # tourney_id = re.findall('([0-9]+)', t_id)[0]
        t_surface = tourney.find_all('div', class_='info-area')[1].text
        tourney_surface = t_surface.replace('\t', '').replace('\r', '').replace('\n', '')
        t_type = re.findall('tourtypes/([^S]+)\.', tourney.find('img')['src'])[0]
        t_type = t_type.split('_')
        t_link = tourney.find_all(class_='tourney-details')[4]
        winner = tourney.find('div', class_='tourney-detail-winner').text
        try:
            t_winner = re.findall('[a-zA-Z ]+', winner)[1]
        except:
            t_winner = re.findall('[a-zA-Z ]+', winner)[0]
        t_draw = tourney.find('span', class_ = 'item-value').text.strip()
        if (t_link.find('a').attrs.has_key('href')):
            tourney_link = t_link.find('a')['href']
        else:
            tourney_link = 'not-in-system'
        if (len(t_type) > 4):
            tourney_type = t_type[1] + t_type[2]
        else:
            tourney_type = t_type[1]
        s = tourney_title + ',' + tourney_location + ',' + tourney_dates + ',' + \
        tourney_type + ','+ tourney_surface + ',' + t_draw + ',' + \
        t_winner + ',' + tourney_link + '\n'
        tourneyfile.write(s.encode('utf-8'))
    tourneyfile.close()

# if __name__ == "__main__":
    # getAllRankings()
    # for i in range(2000, 2017):
    #     getTournamentsInYear(str(i))
