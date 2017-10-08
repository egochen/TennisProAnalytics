'''
Crawl and validate proxies
'''
import requests
from bs4 import BeautifulSoup
import random

proxyURL = 'https://www.us-proxy.org/'
PROXYTOTAL = 40

def crawlproxy():
    success = False
    with open('user-agents.txt', 'r') as f:
        user_agents = f.readlines()
    headers = {'User-Agent': random.choice(user_agents).strip()}
    proxyhtml = requests.get(proxyURL, headers = headers).text
    proxiesList = open('proxies.txt', 'w')
    proxyTag = BeautifulSoup(proxyhtml, 'lxml').find_all('tr')
    proxyCount = 0
    for i in range(1, len(proxyTag)-1):
        tags = proxyTag[i].contents
        isTransparent = (str(tags[4].text) == 'transparent')
        if (isTransparent):
            continue
        isHttps = (str(tags[6].text) == 'yes')
        if (isHttps == False):
            h = 'http://'
        else:
            h = 'https://'
        url = h + str(tags[0].text) + ':' + str(tags[1].text)
        try:
            requests.get('http://example.com',
            timeout = 10,
            proxies = {h.split(':')[0]: url})
        except IOError:
            print "Connection error! (Check proxy)"
        else:
            print url
            proxiesList.write(url + '\n')
            proxyCount += 1
        if (proxyCount == PROXYTOTAL):
            break
    proxiesList.close()
    success = True
    return success

if __name__ == "__main__":
    crawlproxy()
