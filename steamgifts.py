#!/usr/bin/python3
__author__ = 'jota'

from io import BytesIO
import gzip
import urllib.request
import urllib.parse
import sys
import re

MAIN_URL = 'http://www.steamgifts.com'
PAGING_URL = 'http://www.steamgifts.com/giveaways/search?page='
USER_AGENT = 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
GLOBAL_HEADERS = {'User-Agent': USER_AGENT, 'Accept': 'application/json, text/javascript, */*; q=0.01', 'Accept-encoding': 'gzip, deflate', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
MAIN_REGEX = 'href="\/giveaway\/(?P<Code>[a-zA-Z0-9]*?)\/[^\/]*?"'
XSRF_REGEX = 'name="xsrf_token" value="(?P<XSRF>[0-9a-zA-Z]*?)"'

def getWebPage(url, headers, cookies, postData=None):
    try:
        if (postData):
            params = urllib.parse.urlencode(postData)
            params = params.encode('utf-8')
            request = urllib.request.Request(url, data=params, headers=headers)
        else:
            print('Fetching '+url)
            request = urllib.request.Request(url, None, headers)
        request.add_header('Cookie', cookies)
        if (postData):
            response = urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(request)
        else:
            response = urllib.request.urlopen(request)
        if response.info().get('Content-Encoding') == 'gzip':
            buf = BytesIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            r = f.read()
        else:
            r = response.read()

        return r
    except Exception as e:
        print("Error processing webpage: "+str(e))
        return None

## https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
def nodup(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def main():
    try:
        if (len(sys.argv) < 2):
            print('./steamgifts.py <Cookie> [<SteamGifts Page Number (default=1)>]')
            print('Please insert your cookie (CTRL+SHIFT+J on the website and type document.cookie. Then paste the whole string as an argument).')
            return
        regex = re.compile(MAIN_REGEX)
        xsrfRegex = re.compile(XSRF_REGEX)

        if (len(sys.argv) > 2):
            homePage = getWebPage(PAGING_URL+sys.argv[2], GLOBAL_HEADERS, sys.argv[1])
        else:
            homePage = getWebPage(PAGING_URL+'1', GLOBAL_HEADERS, sys.argv[1])

        if (homePage is None):
            print('An error occurred while fetching results (probably expired cookie?). Terminating...')
            return

        xsrfToken = xsrfRegex.findall(str(homePage))[0]
        gamesList = regex.findall(str(homePage))
        gamesList = nodup(gamesList)
        print(gamesList)
        for g in gamesList:
            postData = {'xsrf_token':xsrfToken, 'do':'entry_insert', 'code':g}
            print(getWebPage(MAIN_URL+'/ajax.php',GLOBAL_HEADERS,sys.argv[1],postData))

    except KeyboardInterrupt:
        print("Interrupted.")

if __name__ == '__main__':
    main()
