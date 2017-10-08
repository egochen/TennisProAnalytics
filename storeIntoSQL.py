'''
Use python-MySQL connector to store the data in local files to database
'''
import MySQLdb as mc
import sys
import re
import xml.etree.ElementTree as ET
import os
import math

try:
    connection = mc.connect(read_default_group='ATPData',
                            db='ATPData',
                            user = "pytester")
    except mc.Error as e:
    print("Error %d: %s" % (e.args[0], e.args[1]))
    sys.exit(1)

cursor = connection.cursor()

########################################################
############## Match info ############################
########################################################
def saveMatchStats():
    cursor.execute("DROP TABLE IF EXISTS MatchStats")
    cursor.execute('''
    CREATE TABLE MatchStats (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    tourney_id INTEGER,
    match_stage TEXT,
    match_score TEXT,
    match_time TIME,
    p1_name TEXT,
    p2_name TEXT,
    p1_Aces INT,
    p1_AcesPercentage FLOAT,
    p1_DoubleFaults INT,
    p1_DoubleFaultsPercentage FLOAT,
    p1_FirstServePercentage FLOAT,
    p1_FirstServeDividend INT,
    p1_FirstServeDivisor INT,
    p1_FirstServePointsWonPercentage FLOAT,
    p1_FirstServePointsWonDividend INT,
    p1_FirstServePointsWonDivisor INT,
    p1_SecondServePointsWonPercentage FLOAT,
    p1_SecondServePointsWonDividend INT,
    p1_SecondServePointsWonDivisor INT,
    p1_BreakPointsSavedPercentage FLOAT,
    p1_BreakPointsSavedDividend INT,
    p1_BreakPointsSavedDivisor INT,
    p1_ServiceGamesPlayed INT,
    p1_ServiceGamesPlayedPercentage FLOAT,
    p1_FirstServeReturnPointsPercentage FLOAT,
    p1_FirstServeReturnPointsDividend INT,
    p1_FirstServeReturnPointsDivisor INT,
    p1_SecondServePointsPercentage FLOAT,
    p1_SecondServePointsDividend INT,
    p1_SecondServePointsDivisor INT,
    p1_BreakPointsConvertedPercentage FLOAT,
    p1_BreakPointsConvertedDividend INT,
    p1_BreakPointsConvertedDivisor INT,
    p1_ReturnGamesPlayed INT,
    p1_ReturnGamesPlayedPercentage FLOAT,
    p1_TotalServicePointsWonPercentage FLOAT,
    p1_TotalServicePointsWonDividend INT,
    p1_TotalServicePointsWonDivisor INT,
    p1_TotalReturnPointsWonPercentage FLOAT,
    p1_TotalReturnPointsWonDividend INT,
    p1_TotalReturnPointsWonDivisor INT,
    p1_TotalPointsWonPercentage FLOAT,
    p1_TotalPointsWonDividend INT,
    p1_TotalPointsWonDivisor INT,
    p2_Aces INT,
    p2_AcesPercentage FLOAT,
    p2_DoubleFaults INT,
    p2_DoubleFaultsPercentage FLOAT,
    p2_FirstServePercentage FLOAT,
    p2_FirstServeDividend INT,
    p2_FirstServeDivisor INT,
    p2_FirstServePointsWonPercentage FLOAT,
    p2_FirstServePointsWonDividend INT,
    p2_FirstServePointsWonDivisor INT,
    p2_SecondServePointsWonPercentage FLOAT,
    p2_SecondServePointsWonDividend INT,
    p2_SecondServePointsWonDivisor INT,
    p2_BreakPointsSavedPercentage FLOAT,
    p2_BreakPointsSavedDividend INT,
    p2_BreakPointsSavedDivisor INT,
    p2_ServiceGamesPlayed INT,
    p2_ServiceGamesPlayedPercentage FLOAT,
    p2_FirstServeReturnPointsPercentage FLOAT,
    p2_FirstServeReturnPointsDividend INT,
    p2_FirstServeReturnPointsDivisor INT,
    p2_SecondServePointsPercentage FLOAT,
    p2_SecondServePointsDividend INT,
    p2_SecondServePointsDivisor INT,
    p2_BreakPointsConvertedPercentage FLOAT,
    p2_BreakPointsConvertedDividend INT,
    p2_BreakPointsConvertedDivisor INT,
    p2_ReturnGamesPlayed INT,
    p2_ReturnGamesPlayedPercentage FLOAT,
    p2_TotalServicePointsWonPercentage FLOAT,
    p2_TotalServicePointsWonDividend INT,
    p2_TotalServicePointsWonDivisor INT,
    p2_TotalReturnPointsWonPercentage FLOAT,
    p2_TotalReturnPointsWonDividend INT,
    p2_TotalReturnPointsWonDivisor INT,
    p2_TotalPointsWonPercentage FLOAT,
    p2_TotalPointsWonDividend INT,
    p2_TotalPointsWonDivisor INT
    )''')

    for year in range(2000, 2017):
        file_root_name = 'tourneyHistory/' + str(year) + 'tourneys/'

        for i in range(0, len(os.listdir(file_root_name))):
            if not os.listdir(file_root_name)[i].endswith('.txt'):
                continue
            tourney_name = os.listdir(file_root_name)[i]
            tourney_url_name = re.findall('_([a-z\-]+)', tourney_name)[0]

            sql_cmd = 'SELECT id FROM Tournaments WHERE YEAR(DATE_ADD(starting_date, INTERVAL 3 DAY)) = ' + \
            str(year) + ' AND url_name = "' + tourney_url_name + '"'

            print sql_cmd
            cursor.execute(sql_cmd)
            t_id = int(cursor.fetchone()[0])

            file_path = file_root_name + str(year) + tourney_url_name + '/'
            for j in range(0, len(os.listdir(file_path))):
                stats_file = os.listdir(file_path)[j]
                if (stats_file.startswith('.')):
                    continue
                # print stats_file
                tree = ET.parse(file_path + stats_file)
                root = tree.getroot()
                m_score = root.attrib['match_score']
                m_stage = root.attrib['match_stage']
                m_time = root.attrib['match_time']
                p1, p2 = root[0], root[1]
                p1_name = p1.attrib['playerID']
                p2_name = p2.attrib['playerID']

                stats_list = [0] + [t_id] + [m_stage] + [m_score] + [m_time] + [p1_name] + [p2_name]
                for stat in p1.getchildren():
                    if (stat.text == '"NaN"'):
                        stats_list.append(None)
                    else:
                        stats_list.append(stat.text)
                for stat in p2.getchildren():
                    if (stat.text == '"NaN"'):
                        stats_list.append(None)
                    else:
                        stats_list.append(stat.text)

                # if full stats are present in xml
                if (len(stats_list) == 83):
                    # parse out an error in original data file
                    stats_list[-1] = stats_list[-1][0:-1]
                    tp = tuple(stats_list)
                else:
                    #
                    # infer match stage from .txt summary file
                    #
                    sql_cmd = 'SELECT draw_size FROM Tournaments WHERE YEAR(DATE_ADD(starting_date, INTERVAL 3 DAY)) = ' + \
                    str(year) + ' AND url_name = "' + tourney_url_name + '"'
                    cursor.execute(sql_cmd)
                    draw_size = int(cursor.fetchone()[0])
                    with open(file_root_name + tourney_name, 'r') as tourney_file:
                        matchlines = tourney_file.readlines()

                    stage_dict = {}
                    for k in range(0, len(matchlines)):
                        p1_n, p2_n, m_score, _ = matchlines[k].split(',')
                        # calculate match stage from sequencing number
                        stage = int(math.floor(math.log(k+1, 2)))
                        if (stage == 0):
                            calc_stage = 'Finals'
                        elif (stage == 1):
                            calc_stage = 'Semi-Finals'
                        elif (stage == 2):
                            calc_stage = 'Quarter-Finals'
                        elif (stage == 3):
                            calc_stage = 'Round of 16'
                        elif (stage == 4 and k < draw_size):
                            calc_stage = 'Round of 32'
                        elif (stage == 5 and k < draw_size):
                            calc_stage = 'Round of 64'
                        elif (stage == 6 and k < draw_size):
                            calc_stage = 'Round of 128'
                        else:
                            calc_stage = 'Qualifying'
                        stage_dict[p1_n + p2_n] = calc_stage

                    stats_list[2] = stage_dict[p1_name+p2_name]
                    tp = tuple(stats_list + [None] * 76)

                holders = ''
                for t in ['%s'] * len(tp):
                    holders += t + ','

                sql_stats_cmd = 'INSERT INTO MatchStats VALUES({0})'.format(holders[0:-1])
                cursor.execute(sql_stats_cmd, tp)
                connection.commit()

########################################################
############## Player info ############################
########################################################
def savePlayers():
    # Strict mode affects whether the server permits '0000-00-00' as a valid date
    # Turn strict mode off
    cursor.execute("SET sql_mode = ''")

    cursor.execute ("DROP TABLE IF EXISTS Players")
    cursor.execute('''
    CREATE TABLE Players (
    player_id VARCHAR(5) PRIMARY KEY UNIQUE,
    name TEXT,
    birth_date DATE,
    turned_pro YEAR,
    weight INTEGER,
    height INTEGER,
    country TEXT,
    birth_place TEXT,
    residence TEXT,
    dominant_hand TEXT,
    backhand TEXT
    )''')
    with open('player_info.txt', 'r') as f:
        lines = f.readlines()

    tuplelines = []
    for line in lines:
        tuplelines.append(line.split(';'))
    cursor.executemany('''INSERT INTO Players
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', tuplelines)
    connection.commit()


########################################################
############## Ranking info ############################
########################################################
def saveRankings():
    cursor.execute ("DROP TABLE IF EXISTS Rankings")
    cursor.execute('''
    CREATE TABLE Rankings (
    idx INTEGER AUTO_INCREMENT PRIMARY KEY,
    ranking_date DATE,
    player_id TEXT,
    player_rank INTEGER
    )''')
    with open('./rankingHistory/ATPPlayerFullRank.txt', 'r') as f:
        lines = f.readlines()
    tuplelines = []
    for line in lines:
        tuplelines.append(line.split())

    L = len(tuplelines)

    cursor.executemany('''INSERT INTO Rankings (ranking_date, player_id, player_rank)
    VALUES (%s,%s,%s)''',  tuplelines)

    connection.commit()
########################################################
############## Tournament info #########################
########################################################
def saveTournamentList():
    cursor.execute ("DROP TABLE IF EXISTS Tournaments")
    cursor.execute('''
    CREATE TABLE Tournaments (
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        name    TEXT,
        location TEXT,
        country TEXT,
        starting_date   DATE,
        category TEXT,
        surface TEXT,
        draw_size INT,
        winner TEXT,
        url_name TEXT
        )''')

    for year in range(2000, 2017):
        with open('./tourneyHistory/' + str(year) + 'tourneys.txt', 'r') as f:
            tourneys = f.readlines()
        for tourney in tourneys:
            print tourney
            link = tourney.split(',')[-1]
            if (len(tourney.split(',')) == 9):
                name, loc, country, starting, cate, surf, draw, winner,_ = tourney.split(',')
            else:
                name, loc, starting, cate, surf, draw, winner, _ = tourney.split(',')
                country = '---';
            if link.startswith('/en/'):
                urlName = re.findall('([a-z\-]+)\/[0-9]+', link)[0]
            else:
                continue
            cursor.execute('''INSERT INTO Tournaments
            (name, location, country, starting_date,
            category, surface, draw_size, winner, url_name)
            VALUES (%s,%s,%s,%s,%s,%s,%s, %s, %s)''', \
            (name, loc, country, starting, cate, surf, draw, winner, urlName) )

    connection.commit()

    cursor.execute("SELECT * FROM Tournaments")
    print 'Result of "SELECT * FROM Tournaments":'

    result = cursor.fetchall()
    for r in result:
        print(r)

# if __name__ == "__main__":
    # saveTournamentList()
    # savePlayers()
    # saveRankings()
    # saveMatchStats()
cursor.close()
connection.close()
