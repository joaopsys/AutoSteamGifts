#!/usr/bin/python3
__author__ = 'jota'

from io import BytesIO
import gzip
import urllib.request
import urllib.parse
import sys
import re
import os
import ctypes

MAIN_URL = 'http://www.steamgifts.com'
PAGING_URL = 'http://www.steamgifts.com/giveaways/search?page='
USER_AGENT = 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
GLOBAL_HEADERS = {'User-Agent': USER_AGENT, 'Accept': 'application/json, text/javascript, */*; q=0.01', 'Accept-encoding': 'gzip, deflate', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
MAIN_REGEX = 'href="\/giveaway\/(?P<Code>[a-zA-Z0-9]*?)\/[^\/]*?"'
XSRF_REGEX = 'name="xsrf_token" value="(?P<XSRF>[0-9a-zA-Z]*?)"'
POINTS_REGEX = "<span class=\"nav__points\">(?P<Points>[0-9]+)</span>"
POINTS_RESPONSE_REGEX = "\"points\":\"(?P<Points>[0-9]+)\""
COOKIE_FILE_NAME = ".steamgifts"

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

def saveCookie(cookie):
    ## https://stackoverflow.com/questions/25432139/python-cross-platform-hidden-file
    ## Just Windows things
    if os.name == 'nt':
        ret = ctypes.windll.kernel32.SetFileAttributesW(COOKIE_FILE_NAME, 0)
            
    with open(COOKIE_FILE_NAME, 'w') as f:
        f.write(cookie)

    if os.name == 'nt':
        ret = ctypes.windll.kernel32.SetFileAttributesW(COOKIE_FILE_NAME, 2)

def getCookieFromfile():
    try:
        with open(COOKIE_FILE_NAME, 'r') as f:
            return f.read()
    except:
        return ''
def main():
    try:
        if (len(sys.argv) < 2):
            sgCookie = getCookieFromfile()
            if (not sgCookie or len(sgCookie) < 1):
                print('<<<AutoSteamGifts>>>')
                print('Usage: ./steamgifts.py <Cookie> [<starting page (default=1)>]')
                print('Please insert your cookie. Press CTRL+SHIFT+J on the website (CTRL+SHIFT+K on Firefox) and type document.cookie. Then paste the whole string as an argument.')
                print('You only need need to do this once because AutoSteamGifts will remember your cookie (if valid).')
                return
        else:
            sgCookie = sys.argv[1]
        regex = re.compile(MAIN_REGEX)
        xsrfRegex = re.compile(XSRF_REGEX)
        pointsRegex = re.compile(POINTS_REGEX)
        pointsResponseRegex = re.compile(POINTS_RESPONSE_REGEX)

        if (len(sys.argv) > 2):
            startingPage = sys.argv[2]
        else:
            startingPage = 1

        while True:
            homePage = getWebPage(PAGING_URL+str(startingPage), GLOBAL_HEADERS, sgCookie)
            if (not homePage):
                print('An error occurred while fetching results (probably expired/invalid cookie). Terminating...')
                return
            saveCookie(sgCookie)
            xsrfToken = xsrfRegex.findall(str(homePage))[0]
            points = pointsRegex.findall(str(homePage))[0]
            gamesList = regex.findall(str(homePage))
            gamesList = nodup(gamesList)
            print(gamesList)
            for g in gamesList:
                if (int(points) <= 0):
                    print('You have 0 points, exiting...')
                    return
                postData = {'xsrf_token':xsrfToken, 'do':'entry_insert', 'code':g}
                postResponse = getWebPage(MAIN_URL+'/ajax.php',GLOBAL_HEADERS,sgCookie,postData)
                points = pointsResponseRegex.findall(str(postResponse))[0]
                print(postResponse)
            startingPage = int(startingPage)+1

    except KeyboardInterrupt:
        print("Interrupted.")

if __name__ == '__main__':
    main()
