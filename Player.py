'''
Get the profiles of all players who has been ranking in top 1000 since 2000.
'''
from getPlayerIDRankingTourneys import getHTML
import codecs

class Player:
    def __init__(self, link):
        self.url = link
        self.id = ''
        self.name = ''
        self.bday = ''
        self.proyear = ''
        self.weight = ''
        self.height = ''
        self.residence = ''
        self.birthplace = ''
        self.majorhand = ''
        self.backhand = ''
        self.country = ''
    def getPlayerInfo(self, countryDict):
        playersoup = BeautifulSoup(getHTML(self.url), 'lxml')
        self.id = re.findall('([a-z0-9]+)\/overview', self.url)[0]
        self.name= playersoup.find('meta', property="pageTransitionTitle")['content']
        try:
            bd = playersoup.find('span', class_='table-birthday').text.strip()
        except:
            bd = '(0000.00.00)'
        self.bday = bd[1:len(bd)-1]
        _, pro, wt, ht = playersoup.find_all('div', class_ = 'table-big-value')
        birt, res, hand, _ = playersoup.find_all('div', class_ = 'table-value')
        try:
            self.proyear = re.findall('[0-9]+', pro.text)[0]
        except:
            self.proyear = '0000'
        try:
            self.weight = re.findall('([0-9]+)kg', wt.text)[0]
        except:
            self.weight = '0'
        try:
            self.height = re.findall('([0-9]+)cm', ht.text)[0]
        except:
            self.height = '0'
        self.birthplace = birt.text.strip()
        self.residence = res.text.strip()
        self.majorhand = hand.text.strip().split(',')[0]
        if (len(hand.text.strip().split(',')) == 2):
            self.backhand = hand.text.strip().split(',')[1]
        else:
            self.backhand = '---'
        try:
            flagcode = playersoup.find('div', class_='player-flag-code').text
        except:
            flagcode = '---'
        if (countryDict.has_key(flagcode)):
            self.country = countryDict[flagcode]
        else:
            self.country = '---'
        s1 = self.id + ';' + self.name + ';' + self.bday + ';' + self.proyear
        s2 = self.weight + ';' + self.height
        s3 = self.country + ';' + self.birthplace + ';' + self.residence
        s4 = self.majorhand + ';' + self.backhand
        s = s1 + ';' + s2 + ';' + s3 + ';' + s4
        return s

# Construct the players' profile link from the ranking files
def getPlayerLinks():
    result_set = set()
    pathname = './rankingHistory/'
    for i in range(0, len(os.listdir(pathname))):
        playerfile = os.listdir(pathname)[i]
        # only get players after year 2000
        if (playerfile.endswith('.txt') and playerfile.startswith('20')):
            with open(pathname + playerfile, 'r') as f:
                players = f.readlines()
                if len(players) == 0:
                    continue
                for i in range(0, len(players)):
                    playerstr = players[i].split(',')[2]
                    playerid = players[i].split(',')[3]
                    result_set.add('http://www.atpworldtour.com/en/players/' + \
                    playerstr + '/' + playerid + '/overview')
    with open('player_links.txt', 'w') as f:
        for i in result_set:
            f.write(i)
            f.write('\n')
    return list(result_set)

# Map the 3-letter country code to full country name
def getCountryCode(fname):
    with open(fname, 'r') as f:
        lines = f.readlines()
    countryDict = {}
    for line in lines:
        key, value = line.strip().split(',')
        countryDict[key] = value
    return countryDict

if __name__ == "__main__":
    players = getPlayerLinks()
    countryDict = getCountryCode('country code.txt')
    f = codecs.open('player_info2.txt', 'w', encoding='utf8')
    i = 0
    while i < len(players):
        p = players[i]
        print i, p
        success = False
        attempt = 0
        while not success and attempt < 10:
            try:
                s = Player(p).getPlayerInfo(countryDict)
            except Exception as e:
                attempt += 1
                print str(e)
            else:
                success = True
                f.write(s + '\n')
        i += 1
