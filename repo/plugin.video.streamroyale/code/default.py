# -*- coding: utf-8 -*-
import xbmc, xbmcaddon, xbmcplugin, xbmcgui
import requests
import os.path
import random
import pickle
import urllib
import string
import json
import sys
import re

addon_name = "plugin.video.streamroyale"
addon = xbmcaddon.Addon(addon_name)
userdata_path = xbmc.translatePath("special://userdata")
addon_userdata_path = os.path.join(userdata_path, "addon_data", addon_name)
cookie_file = os.path.join(addon_userdata_path, "cookie")
contenttype = "application/json"
useragent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36"

def storecredentials(store_type):
    Keyboard = xbmc.Keyboard('default', 'heading', True)
    Keyboard.setDefault('')
    Keyboard.setHeading("Enter Your " + store_type)
    if store_type == "password":
        Keyboard.setHiddenInput(True)
    else:
        Keyboard.setHiddenInput(False)
    Keyboard.doModal()
    if (Keyboard.isConfirmed()):
        addon.setSetting(id=store_type, value=Keyboard.getText())

baseurl = 'https://gafork.com'
loginurl = baseurl + "/api/v1/user/login"
closesessionsurl = baseurl + "/logout-elsewhere"

def save_cookies(requests_cookiejar, filename):
    with open(filename, 'wb') as f:
        pickle.dump(requests_cookiejar, f)

def load_cookies(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

def dologin(url,payload,headers):
    session = requests.session()
    response = session.post(url, data = json.dumps(payload), headers = headers)
    save_cookies(response.cookies, cookie_file)
    return json.loads(response.text)

def cookiecheck(url, username, password, contenttype, useragent):
    loginpayload = {'user': username, 'password': password}
    loginheaders = {'content-type': contenttype, 'user-agent': useragent}
    if not os.path.isfile(cookie_file):    
        dologin(url,loginpayload,loginheaders)
        xbmcgui.Dialog().ok("Warning", "No previous login detected, You will now be logged in.")
    else:
        response = requests.get(baseurl + "/api/v1/user/settings", cookies=load_cookies(cookie_file))
        if not response.status_code == 200:
            dologin(url,loginpayload,loginheaders)
            xbmcgui.Dialog().ok("Warning", "Your login has expired, You will now be logged back in.")
                                
if addon.getSetting('username') =="":
    storecredentials("username")

if addon.getSetting('password') =="":
    storecredentials("password")
    
username = addon.getSetting('username')
password = addon.getSetting('password')

def onlyascii(oldstring):
    newstring = filter(lambda x: x in string.printable, oldstring)
    return newstring
        
def getsource(url):
    response = requests.get(url, cookies=load_cookies(cookie_file))
    return response.text

def search(query, search_type):
    query_url = "https://xxdazcoul3-dsn.algolia.net/1/indexes/al_titles_index/query?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%20(lite)%203.24.3&x-algolia-application-id=XXDAZCOUL3&x-algolia-api-key=c5c1279f5ad09819ecf2af9d6b5ee06a"
    search_contenttype = "application/x-www-form-urlencoded"
    payload = {"query":query, "facets":"*", "hitsPerPage":"30", "filters":"yr>=1919 AND yr<=2017 AND " + search_type}
    headers = {'content-type': search_contenttype, 'user-agent': useragent}
    session = requests.session()
    response = session.post(query_url, data = json.dumps(payload), headers = headers)
    response = onlyascii(response.text)
    return json.loads(response)

def searchentry(message):
    Keyboard = xbmc.Keyboard('default', 'heading', True)
    Keyboard.setDefault('')
    Keyboard.setHeading(message)
    Keyboard.setHiddenInput(False)
    Keyboard.doModal()
    if (Keyboard.isConfirmed()):
        return Keyboard.getText()
    
def Main(url):
    addDir('MOVIES', url,1,'','Browse Movies')
    addDir('TV SERIES', url,2,'','Browse TV Series')
    addDir('MY LIST', url + '/api/v1/user/list/mylist?type=all&sort=added_on',4,'','Browse My List')
    addDir('[COLORblue]SEARCH[/COLOR]', url,3,'','Search Movies & TV Series')

def Movies(url):
    addDir('[COLORblue]SEARCH[/COLOR]', "searchmovie",4,'','Search Movies')
    addDir('BROWSE BY GENRES', url,7,'','Browse Movies By Genre')
    addDir('HIGHEST GROSSING', url + '/api/v1/list/movies.highest_grossing',4,'','Highest Grossing Movies Of All Time') 
    addDir('HIGHEST VOTED', url + '/api/v1/discover/movies?from=0&to=50&sort=score&quality=all&genre=all',4,'','Highest Voted Movies Of All Time')
    addDir('MOST POPULAR', url + '/api/v1/discover/movies?from=0&to=50&sort=popularity&quality=all&genre=all',4,'','Most Popular Movies Of All Time')
    addDir('MOST POPULAR 2015', url + '/api/v1/list/movies.most_popular_2015',4,'','Highest Popular Movies Released In 2015')
    addDir('MOST POPULAR 2016', url + '/api/v1/list/movies.most_popular_2016',4,'','Highest Popular Movies Released In 2016')
    addDir('BROWSE RECENTLY ADDED', url + '/api/v1/discover/movies?from=0&to=50&sort=added_on&quality=all&genre=all',4,'','Recently Added Movies')
    addDir('BROWSE BY TRENDING', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=all',4,'','Highest Trending Movies Of All Time')

def MovieGenres(url):
    addDir('DRAMA', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=drama',4,'','Browse Drama Movies')
    addDir('COMEDY', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=comedy',4,'','Browse Comedy Movies')
    addDir('THRILLER', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=thriller',4,'','Browse Thriller Movies')
    addDir('ACTION', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=action',4,'','Browse Action Movies')
    addDir('CRIME', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=crime',4,'','Browse Crime Movies')
    addDir('ADVENTURE', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=adventure',4,'','Browse Adventure Movies')
    addDir('ROMANCE', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=romance',4,'','Browse Romance Movies')
    addDir('HORROR', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=horror',4,'','Browse Horror Movies')
    addDir('SCI-FI', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=sci-fi',4,'','Browse Sci-Fi Movies')
    addDir('FANTASY', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=fantasy',4,'','Browse Fantasy Movies')
    addDir('MYSTERY', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=mystery',4,'','Browse Mystery Movies')
    addDir('FAMILY', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=family',4,'','Browse Family Movies')
    addDir('ANIMATION', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=animation',4,'','Browse Aminated Movies')
    addDir('BIOGRAPHY', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=biography',4,'','Browse Biography Movies')
    addDir('HISTORY', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=history',4,'','Browse History Movies')
    addDir('MUSIC', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=music',4,'','Browse Music Movies')
    addDir('WAR', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=war',4,'','Browse War Movies')
    addDir('DOCUMENTARY', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=documentary',4,'','Browse Documentary Movies')
    addDir('SPORT', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=sport',4,'','Browse Sport Movies')
    addDir('WESTERN', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=western',4,'','Browse Western Movies')
    addDir('MUSICAL', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=musical',4,'','Browse Musical Movies')
    addDir('FOREIGN', url + '/api/v1/discover/movies?from=0&to=50&sort=trending&quality=all&genre=foreign',4,'','Browse Foregin Movies')
    
def TVSeries(url):
    addDir('[COLORblue]SEARCH[/COLOR]', 'searchseries',4,'','Search TV Series')
    addDir('BROWSE BY GENRES', url,8,'','Browse TV Shows By Genre')
    addDir('HIGHEST VOTED', url + "/api/v1/discover/tv?from=0&to=50&sort=score&quality=all&genre=all",4,'','Highest Voted TV Series Of All Time')
    addDir('MOST POPULAR', url + "/api/v1/discover/tv?from=0&to=50&sort=popularity&quality=all&genre=all",4,'','Most Popular TV Series Of All Time')
    addDir('MOST POPULAR 2015', url + "/api/v1/list/tv.most_popular_2015",4,'','Highest Popular TV Series Released In 2015')
    addDir('MOST POPULAR 2016', url + "/api/v1/list/tv.most_popular_2016",4,'','Highest Popular TV Series Released In 2016')
    addDir('BROWSE BY TRENDING', url + "/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=all",4,'','Highest Trending TV Series Of All Time')
    addDir('BROWSE RECENTLY ADDED', url + "/api/v1/discover/tv?from=0&to=50&sort=added_on&quality=all&genre=all",4,'','Recently Added TV Episodes')

def TVSeriesGenres(url):
    addDir('DRAMA', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=drama',4,'','Browse Drama TV Shows')
    addDir('COMEDY', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=comedy',4,'','Browse Comedy TV Shows')
    addDir('THRILLER', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=thriller',4,'','Browse Thriller TV Shows')
    addDir('ACTION', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=action',4,'','Browse Action TV Shows')
    addDir('CRIME', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=crime',4,'','Browse Crime TV Shows')
    addDir('ADVENTURE', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=adventure',4,'','Browse Adventure TV Shows')
    addDir('ROMANCE', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=romance',4,'','Browse Romance TV Shows')
    addDir('HORROR', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=horror',4,'','Browse Horror TV Shows')
    addDir('SCI-FI', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=sci-fi',4,'','Browse Sci-Fi TV Shows')
    addDir('FANTASY', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=fantasy',4,'','Browse Fantasy TV Shows')
    addDir('MYSTERY', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=mystery',4,'','Browse Mystery TV Shows')
    addDir('FAMILY', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=family',4,'','Browse Family TV Shows')
    addDir('ANIMATION', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=animation',4,'','Browse Aminated TV Shows')
    addDir('BIOGRAPHY', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=biography',4,'','Browse Biography TV Shows')
    addDir('HISTORY', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=history',4,'','Browse History TV Shows')
    addDir('MUSIC', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=music',4,'','Browse Music TV Shows')
    addDir('WAR', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=war',4,'','Browse War TV Shows')
    addDir('DOCUMENTARY', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=documentary',4,'','Browse Documentary TV Shows')
    addDir('SPORT', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=sport',4,'','Browse Sport TV Shows')
    addDir('WESTERN', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=western',4,'','Browse Western TV Shows')
    addDir('MUSICAL', url + '/api/v1/discover/tv?from=0&to=50&sort=trending&quality=all&genre=musical',4,'','Browse Musical TV Shows')
    
def Search(url):
    addDir('[COLORblue]SEARCH MOVIES[/COLOR]', "searchmovie",4,'','Browse Movies')
    addDir('[COLORblue]SEARCH TV SERIES[/COLOR]', 'searchseries',4,'','Browse TV Series')

def nextpage(url):
    ToRegex = re.compile(".to=(.*).sort")
    new_from = re.findall(ToRegex,url)
    new_from = int(new_from[0])
    new_from = new_from + 1
    new_to = new_from + 49
    LeftRegex = re.compile("(.*)from")
    left_url = re.findall(LeftRegex,url)
    left = left_url[0]
    left = left + "from="
    RightRegex = re.compile("to=[0-9]+.sort(.*)")
    right_url = re.findall(RightRegex,url)
    right = right_url[0]
    return left + str(new_from) + "&to=" + str(new_to) + "&sort" + right 
    
def listcontent(url):
    item_count = 0
    if "from" in url:
        next_page_url = nextpage(url)
    if url == "searchseries":
        query = searchentry("Enter Show Name:")
        sourcecode = search(query, "tv")
        sourcecode = sourcecode['hits']
    elif url == "searchmovie":
        query = searchentry("Enter Movie Name:")
        sourcecode = search(query, "movie")
        sourcecode = sourcecode['hits'] 
    else:
        sourcecode = getsource(url)
        sourcecode = onlyascii(sourcecode)
        sourcecode = json.loads(sourcecode)
        if "listings" in sourcecode:
            sourcecode = sourcecode['listings']

    for i in sourcecode:
        item_count = item_count + 1
        try:
            title = i['title']
        except:
            title = ""
        try:
            movie_url = baseurl + i['permalink']
        except:
            movie_url = ""
        try:
            poster = "https://image.tmdb.org/t/p/w300" + i['poster']
        except:
            poster = ""
        if "movies" in movie_url:
            addDir(title,movie_url,5,poster,'')
        else:
            addDir(title,movie_url,6,poster,'')
    if "from" in url:
        if item_count == 50:        
            if "movies" in url:
                addDir("[COLORblue]NEXT PAGE[/COLOR]",next_page_url,4,'','')
            else:
                addDir("[COLORblue]NEXT PAGE[/COLOR]",next_page_url,4,'','')
    
def getmovielinks(url):
    ImdbRegex = re.compile(baseurl[8:] + "\/movies\/(.*)\/")
    IMDB = re.findall(ImdbRegex,url)
    link_url = "https://" + baseurl[8:] + "/api/v1/title/" + IMDB[0]
    sourcecode = getsource(link_url)
    sourcecode = json.loads(sourcecode)
    domain_prefix = sourcecode['domain']['prefix']
    domain_suffix = sourcecode['domain']['suffix']
    poster = "https://image.tmdb.org/t/p/w300"+sourcecode['poster']
    mediaTitle=sourcecode['title']
    desc=sourcecode['storyline']

    try:
        mirror_jsonlist = sourcecode['links']['mirrors']
        trimmed_mirror_list = list(set(mirror_jsonlist))
        mirror_list = []
        random_server=""
        for i in trimmed_mirror_list:
            mirror_list.append("https://" + domain_prefix + str(i) + "." + domain_suffix)

            if i == 15:
                random_server = "https://" + domain_prefix + str(i) + "." + domain_suffix

        if not random_server:
            random_server = (random.choice(mirror_list))
        try:
            addLink('[COLORgold]PLAY:[/COLOR] 480p LINK',random_server + sourcecode['links']['links']['480p'],poster,{"Title": mediaTitle, "Plot": desc})
        except:
            pass
        try:
            addLink('[COLORgold]PLAY:[/COLOR] 720p LINK',random_server + sourcecode['links']['links']['720p'],poster,{"Title": mediaTitle, "Plot": desc})
        except:
            pass
        try:
            addLink('[COLORgold]PLAY:[/COLOR] SD LINK',random_server + sourcecode['links']['links']['normal'],poster,{"Title": mediaTitle, "Plot": desc})
        except:
            pass
        try:
            addLink('[COLORgold]PLAY:[/COLOR] HD LINK',random_server + sourcecode['links']['links']['hd'],poster,{"Title": mediaTitle, "Plot": desc})
        except:
            pass
        try:
            addLink('[COLORgold]PLAY:[/COLOR] 1080p LINK',random_server + sourcecode['links']['links']['1080p'],poster,{"Title": mediaTitle, "Plot": desc})
        except:
            pass
        try:
            addLink('[COLORgold]PLAY:[/COLOR] Webrip LINK',random_server + sourcecode['links']['links']['webrip'],poster,{"Title": mediaTitle, "Plot": desc})
        except:
            pass
    except:
        addDir('[COLORred]NO STREAMS AVAILABLE[/COLOR]', "",999,'','No Streams Found on StreamRoyale')

def getserieslinks(url):
    ImdbRegex = re.compile(baseurl[8:] + "\/tv\/(.*)\/")
    IMDB = re.findall(ImdbRegex,url)
    link_url = "https://" + baseurl[8:] + "/api/v1/title/" + IMDB[0]
    sourcecode = getsource(link_url)
    sourcecode = onlyascii(sourcecode)
    sourcecode = json.loads(sourcecode)
    domain_prefix = sourcecode['domain']['prefix']
    domain_suffix = sourcecode['domain']['suffix']
    watchedList = sourcecode['lists']['watched']
    mediaTitle=sourcecode['title']
    desc=sourcecode['storyline']
    poster = "https://image.tmdb.org/t/p/w300"+sourcecode['poster']
    raw_list = []
    for key, value in sourcecode['links'].items():
        mirror_jsonlist = value['mirrors']
        trimmed_mirror_list = list(set(mirror_jsonlist))
        mirror_list = []
        random_server=""
        for i in trimmed_mirror_list:
            mirror_list.append("https://" + domain_prefix + str(i) + "." + domain_suffix)

            if i == 15:
                random_server = "https://" + domain_prefix + str(i) + "." + domain_suffix

        if not random_server:
            random_server = (random.choice(mirror_list))
        title = key
        match=re.search('s\d{1,}',title)
        seasonNum=match.group()
        seasonNum=seasonNum.replace("s","")
        match=re.search('e\d{1,}',title)
        episodeNum=match.group()
        episodeNum=episodeNum.replace("e","")
        title="S"+seasonNum.zfill(2)+"E"+episodeNum.zfill(2)
        rawnum="s"+seasonNum+"e"+episodeNum
        episodeNum=int(episodeNum)
        seasonNum=int(seasonNum)
        playcount=0
        if rawnum in watchedList:
            playcount = 1
            
        try:
            name=sourcecode['seasons'][seasonNum-1]['episodes'][episodeNum-1]['name']
        except:
            name=mediaTitle
        try:
            stream_url = random_server + value['links']['normal']
        except:
            try:
                stream_url = random_server + value['links']['720p']
            except:
                stream_url = random_server + value['links']['webrip']
        episode = {'Title': title, 'URL': stream_url, "episode": episodeNum, "season":seasonNum,"name":name, "playcount": playcount}
        raw_list.append(episode)
    episode_list = sorted(raw_list)
    for i in episode_list:
        addLink("[COLORgold]"+i['Title']+"[/COLOR] - " + i['name'],i['URL'],poster,{"tvshowtitle": mediaTitle, "title":i['name'], "plot": desc, "mediatype":"episode", "episode": i['episode'], "season":i['season'], "playcount":i['playcount']})
        
def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

def addLink(name,url,iconimage,mediaInfoLabels):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels=mediaInfoLabels )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok

def addDir(name,url,mode,iconimage,desc):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    contextMenuItems=[]
    contextMenuItems.append(("Add To SR List", 'XBMC.RunPlugin(%s?url=%s&mode=%s)' % (sys.argv[0], urllib.quote_plus(url), 24)))
    contextMenuItems.append(("Remove From SR List", 'XBMC.RunPlugin(%s?url=%s&mode=%s)' % (sys.argv[0], urllib.quote_plus(url), 25)))
    liz.addContextMenuItems(contextMenuItems)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": desc } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def extractIMDBUrl(url):
    match = re.search('tt\d{7}', url)
    found=""
    if match:                      
        found=match.group() ## 'found word:cat'
    return found

def addToMyList(imdbID):
    r = requests.patch('https://streamroyale.com/api/v1/user/list/mylist', json={"id":imdbID, "episodeID":"", "added":True}, cookies=load_cookies(cookie_file))

def removeFromList(imdbID):
    r = requests.patch('https://streamroyale.com/api/v1/user/list/mylist', json={"id":imdbID, "episodeID":"", "added":False}, cookies=load_cookies(cookie_file))

params=get_params()
url=None
name=None
mode=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass
if mode==None or url==None or len(url)<1:
    cookiecheck(loginurl, username, password, contenttype, useragent)
    Main(baseurl)
elif mode==1:
    Movies(url)
elif mode==2:
    TVSeries(url)
elif mode==3:
    Search(url)
elif mode==4:
    listcontent(url)
elif mode==5:
    getmovielinks(url)
elif mode==6:
    getserieslinks(url)
elif mode==7:
    MovieGenres(url)
elif mode==8:
    TVSeriesGenres(url)
elif mode==24:
    xbmc.executebuiltin('Container.Refresh')
    addToMyList(extractIMDBUrl(url))

elif mode==25:
    xbmc.executebuiltin('Container.Refresh')
    removeFromList(extractIMDBUrl(url))
    
xbmcplugin.endOfDirectory(int(sys.argv[1]))