'''
Crawl and save in XML format the statistics of any match.
'''
from getPlayerIDRankingTourneys import getHTML
from lxml import etree, objectify
from xml.dom import minidom
from crawl_proxies import crawlproxy

class Match:
    def __init__(self, year, tourney, p1name, p2name, score, link):
        self.year = year
        self.tourney = tourney
        self.player1name = p1name
        self.player2name = p2name
        self.match_score = score
        self.player1stat = {}
        self.player2stat = {}
        self.match_time = ''
        self.match_stage = ''
        self.filename = self.setFileName()
        if (re.findall('^\/en/tournaments/[a-z]+', link) != []):
            self.url = 'https://www.atpworldtour.com' + link.strip()
        else:
            # when the given url is '---' or simply not valid
            # raise ValueError('Error: ' + link + '\n')
            self.url = '---'
    def setFileName(self):
        playernames = self.player1name + '_' + self.player2name
        pathname = './tourneyHistory/' + str(self.year) + 'tourneys/'+ \
        str(self.year) + self.tourney + '/'
        if not os.path.isdir(pathname):
            os.mkdir(pathname)
        filename = str(self.year) +'_' + self.tourney + '_' + playernames + '.xml'
        return pathname + filename

    def getMatchStats(self):
        statSoup = BeautifulSoup(getHTML(self.url), 'lxml')
        try:
            self.match_stage = statSoup.find('td', class_ = 'title-area').text.strip()
        except:
            raise ValueError('Cannot find match stage:' + self.url)
        self.match_time = re.findall('[0-9:]+[0-9:]+[0-9:]+', statSoup.find('td', class_='time').text)[0]
        stats = statSoup.find('script', id='matchStatsData')
        sclean =re.sub('[ \r\n\t]', '', stats.text)
        p1p2 = re.findall('setNum":0,(.*)setNum":1', sclean)[0]
        playerW = re.findall('playerStats":{(.*)},"opponentStats', p1p2)[0].split(',')
        playerL = re.findall('opponentStats":{(.*)}',p1p2)[0].split(',')
        def format_match_data(playerStats):
            """
            create a dictionary from a list of stats
            """
            dataDict = {}
            for i in playerStats:
                k = i.split(':')[0].strip('"')
                v = i.split(':')[1]
                dataDict[k] = v
            return dataDict
        self.player1stat = format_match_data(playerW)
        self.player2stat = format_match_data(playerL)
    def create_stats_for_xml(self, data, pid):
        """
        Create a matchstats XML element
        """
        stats = objectify.Element("matchstats")
        # player = objectify.SubElement(stats, pid)
        stats.set("playerID", pid)
        stats.IsSetActive = data["IsSetActive"]
        stats.Time = data["Time"]
        stats.Aces = data["Aces"]
        stats.AcesPercentage = data["AcesPercentage"]
        stats.DoubleFaults = data["DoubleFaults"]
        stats.DoubleFaultsPercentage = data["DoubleFaultsPercentage"]
        stats.FirstServePercentage = data["FirstServePercentage"]
        stats.FirstServeDividend = data["FirstServeDividend"]
        stats.FirstServeDivisor = data["FirstServeDivisor"]
        stats.FirstServePointsWonPercentage = data["FirstServePointsWonPercentage"]
        stats.FirstServePointsWonDividend = data["FirstServePointsWonDividend"]
        stats.FirstServePointsWonDivisor = data["FirstServePointsWonDivisor"]
        stats.SecondServePointsWonPercentage = data["SecondServePointsWonPercentage"]
        stats.SecondServePointsWonDividend = data["SecondServePointsWonDividend"]
        stats.SecondServePointsWonDivisor = data["SecondServePointsWonDivisor"]
        stats.BreakPointsSavedPercentage = data["BreakPointsSavedPercentage"]
        stats.BreakPointsSavedDividend = data["BreakPointsSavedDividend"]
        stats.BreakPointsSavedDivisor = data["BreakPointsSavedDivisor"]
        stats.ServiceGamesPlayed = data["ServiceGamesPlayed"]
        stats.ServiceGamesPlayedPercentage = data["ServiceGamesPlayedPercentage"]
        stats.FirstServeReturnPointsPercentage = data["FirstServeReturnPointsPercentage"]
        stats.FirstServeReturnPointsDividend = data["FirstServeReturnPointsDividend"]
        stats.FirstServeReturnPointsDivisor = data["FirstServeReturnPointsDivisor"]
        stats.SecondServePointsPercentage = data["SecondServePointsPercentage"]
        stats.SecondServePointsDividend = data["SecondServePointsDividend"]
        stats.SecondServePointsDivisor = data["SecondServePointsDivisor"]
        stats.BreakPointsConvertedPercentage = data["BreakPointsConvertedPercentage"]
        stats.BreakPointsConvertedDividend = data["BreakPointsConvertedDividend"]
        stats.BreakPointsConvertedDivisor = data["BreakPointsConvertedDivisor"]
        stats.ReturnGamesPlayed = data["ReturnGamesPlayed"]
        stats.ReturnGamesPlayedPercentage = data["ReturnGamesPlayedPercentage"]
        stats.TotalServicePointsWonPercentage = data["TotalServicePointsWonPercentage"]
        stats.TotalServicePointsWonDividend = data["TotalServicePointsWonDividend"]
        stats.TotalServicePointsWonDivisor = data["TotalServicePointsWonDivisor"]
        stats.TotalReturnPointsWonPercentage = data["TotalReturnPointsWonPercentage"]
        stats.TotalReturnPointsWonDividend = data["TotalReturnPointsWonDividend"]
        stats.TotalReturnPointsWonDivisor = data["TotalReturnPointsWonDivisor"]
        stats.TotalPointsWonPercentage = data["TotalPointsWonPercentage"]
        stats.TotalPointsWonDividend = data["TotalPointsWonDividend"]
        stats.TotalPointsWonDivisor = data["TotalPointsWonDivisor"]
        stats.remove(stats.IsSetActive)
        stats.remove(stats.Time)
        return stats
    def create_xml(self):
        """
        Create an XML file for a match with detailed statistics
        """
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <MatchStats>
        </MatchStats>'''

        root = objectify.fromstring(xml)
        root.set("match_stage", self.match_stage)
        root.set("match_time", self.match_time)
        root.set("match_score", self.match_score)
        statsW = self.create_stats_for_xml(self.player1stat, self.player1name)
        statsL = self.create_stats_for_xml(self.player2stat, self.player2name)
        root.append(statsW)
        root.append(statsL)

        # remove lxml annotation
        objectify.deannotate(root)
        etree.cleanup_namespaces(root)

        # create the xml string
        obj_xml = minidom.parseString(etree.tostring(root)).toprettyxml(indent="   ")

        try:
            with open(self.filename, "w") as xml_writer:
                xml_writer.write(obj_xml)
        except:
            raise IOError('Cound not write' + filename)
    def create_xml_no_stats(self):
        """
        Create an XML file for a match with no match statistics
        """
        def create_header_for_xml(pid):
            """
            Create a matchstats XML element
            """
            stats = objectify.Element("matchstats")
            # player = objectify.SubElement(stats, pid)
            stats.set("playerID", pid)
            return stats

        xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <MatchStats>
        </MatchStats>'''
        root = objectify.fromstring(xml)
        root.set("match_stage", self.match_stage)
        root.set("match_time", '00:00:00')
        root.set("match_score", self.match_score)
        root.append(create_header_for_xml(self.player1name))
        root.append(create_header_for_xml(self.player2name))
        # remove lxml annotation
        objectify.deannotate(root)
        etree.cleanup_namespaces(root)
        # create the xml string
        obj_xml = minidom.parseString(etree.tostring(root)).toprettyxml(indent="   ")

        try:
            with open(self.filename, "w") as xml_writer:
                xml_writer.write(obj_xml)
        except:
            raise IOError('Cound not write' + filename)

def create_match_xml(year):
    pathname = './tourneyHistory/' + str(year) + 'tourneys/'
    logfile = open('./Match_log_' + str(year) + '.txt', 'w')
    for i in range(0,len(os.listdir(pathname))):
        tourneyfile = os.listdir(pathname)[i]
        if tourneyfile.endswith('.txt'):
            tourneyname = re.findall('[a-z\-]+', tourneyfile)[0]
            with open(pathname + tourneyfile, 'r') as f:
                matches = f.readlines()
            for j in range(0, len(matches)):
                p1, p2, score, link = matches[j].split(',')
                match = Match(year, tourneyname, p1, p2, score, link)
                if not os.path.isfile(match.filename):
                    if (match.url == '---' or tourneyname == 'kuala-lumpur'):
                        match.create_xml_no_stats()
                    else:
                        try:
                            match.getMatchStats()
                        except ValueError as e:
                            print str(e) + '\n'
                            logfile.write(str(e) + '\n')
                            crawlproxy()
                        else:
                            match.create_xml()
    logfile.close()

if __name__ == "__main__":
    for year in range(2000, 2017):
        print year
        create_match_xml(year)
