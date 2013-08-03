# -*- coding: utf-8 -*-

###################################################################################################

PLUGIN_TITLE     = "Dabdate"
PLUGIN_PREFIX    = "/video/dabdate"
ICON_DEFAULT     = "icon-default.png"
ROOT_URL         = "http://www.dabdate.com"
MOBILE_URL       = "http://m.dabdate.com"
RE_VIDEO_ID      = Regex('idx=(\d+)')

QUALITY_MAP = {
    'Medium' : '1',
    'Low'    : '2',
    'High'   : '3'
}
LOCAL_MAP = {
    'Austrailia'    : 'au',
    'Europe'        : 'eu',
    'South America' : 'sa',
    'Los Angeles'   : 'la',
    'New York'      : 'ny'
}

###################################################################################################
def Start():
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

  ObjectContainer.title1     = PLUGIN_TITLE
  ObjectContainer.view_group = "InfoList"
  DirectoryObject.thumb      = R(ICON_DEFAULT)

  HTTP.CacheTime = CACHE_1DAY
  #HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:10.0.2) Gecko/20100101 Firefox/10.0.2"

####################################################################################################
@handler(PLUGIN_PREFIX, PLUGIN_TITLE, thumb = ICON_DEFAULT)
def VideoMainMenu():
  oc = ObjectContainer(view_group="List")

  oc.add( DirectoryObject(key=Callback(VideoList, page=1, lang=0), title=u"방송") )
  oc.add( DirectoryObject(key=Callback(VideoList, page=1, lang=5), title=u"어린이") )

  oc.add(PrefsObject(title=u"설정"))
  return oc

@route(PLUGIN_PREFIX+'/list/{lang}')
def VideoList(page, lang):
  Log.Debug(Prefs['quality'])
  Log.Debug(Prefs['localsrv'])
  quality = QUALITY_MAP[ Prefs['quality'] ]
  localsrv = LOCAL_MAP[ Prefs['localsrv'] ]

  url = ROOT_URL + "/index.php?page=%s&lang=%s" % (page, lang)
  Log.Debug(url)
  try:
    html = HTML.ElementFromURL(url)
  except:
    raise Ex.MediaNotAvailable

  oc = ObjectContainer(view_group="List")

  base_url = ROOT_URL   # no more mobile page support

  for node in html.xpath("//a/span[@class='big']"):
    title = node.text
    video_id = RE_VIDEO_ID.search(node.xpath('..')[0].get('href')).group(1)
    video_url = base_url + '/player.php?idx=%s&pr=%s&local=%s' % (video_id, quality, localsrv)
    Log.Debug(u"video: %s = %s" %(title, video_url))
    thumb = node.xpath('ancestor::tr[2]/td/table/tr/td/img')[0].get('src')
    Log.Debug(u"thumb: "+thumb)
    if node.xpath('ancestor::tr[2]//b[contains(., "Free")]'):
      title = '*'+title
    oc.add(VideoClipObject(url=video_url, title=title, thumb=Function(Thumb, url=thumb)))
  if html.xpath("//a[@class='navi' and text()='[Next]']"):
    nextpage = int(page) + 1
    oc.add(NextPageObject(key=Callback(VideoList, page=nextpage, lang=lang), title=u"다음 페이지"))
  
  return oc

####################################################################################################
def Thumb(url):
  if url:
    try:
      data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
      return DataObject(data, 'image/jpeg')
    except:
      pass
  return Redirect(R(ICON_DEFAULT))
