'''
Crawl and save all matches of any tournament.
'''

from getPlayerIDRankingTourneys import getHTML
import os
import sys

class Tournament:
    def __init__(self, link):
        if (link.startswith('/en/scores/')):
            self.year = re.findall('[0-9]+/([0-9]+)', link)[0]
        else:
            raise ValueError('Error: ' + link)
        self.name = re.findall('archive/([a-z\-]+)', link)[0]
        self.url = 'https://www.atpworldtour.com' + link
        self.matches = []
        self.players = []
        self.match_scores = []
    def getMatches(self):
        matchSoup = BeautifulSoup(getHTML(self.url), 'lxml')
        matchTags = matchSoup.find_all('td', class_='day-table-score')
        playerTags = matchSoup.find_all('td', class_='day-table-name')
        for player in playerTags:
            self.players.append(player.text.strip())

        def processScore(scores):
            # process scores with tie-break: 764 => 76(4)
            for i in range(0, len(scores)):
                score = scores[i]
                if (len(score) >= 3 and (score[0] == '7' or score[1] == '7') \
                and (score[0] == '6' or score[1] == '6')):
                    score = score[0:2] + '(' + score[2:] + ')'
                scores[i] = score
            return scores
        for match in matchTags:
            score = re.findall('[\S]+', match.text)
            self.match_scores.append(processScore(score))
            try:
                match_url = match.find('a')['href']
            except:
                match_url = '---'
            self.matches.append(match_url)
        try:
            assert len(self.matches) == len(self.match_scores)
            assert len(self.players) == 2 * len(self.match_scores)
        except:
            raise AssertionError('Data not correct')

        # write summary file of the tournament
        pathname = './tourneyHistory/' + str(self.year) + 'tourneys/'
        if not os.path.isdir(pathname):
            os.mkdir(pathname)
        filename = pathname + str(self.year) + '_' + self.name + '.txt'
        try:
            summaryfile = open(filename, 'w')
            for i in range(0, len(self.matches)):
                summaryfile.write(self.players[2*i] + ',' + self.players[2*i+1] + ',')
                summaryfile.write(' '.join(self.match_scores[i]) + ',')
                summaryfile.write(self.matches[i])
                summaryfile.write('\n')
            summaryfile.close()
        except:
            raise IOError('Cound not write' + str(self.year) + self.name + '.txt')


def create_tournament_file(year):
    with open('./tourneyHistory/' + str(year) + 'tourneys.txt', 'r') as f:
        tourneys = f.readlines()
    tries = 0
    for i in range(0, len(tourneys)):
        t = tourneys[i].split(',')[-1].strip()
        try:
            tourney = Tournament(t)
        except ValueError as e:
            print str(e)
        else:
            try:
                tourney.getMatches()
            except (AssertionError, IOError) as e:
                print str(e) + ': ' + tourneys[i] + '\n'


if __name__ == "__main__":
    create_tournament_file(2000)
