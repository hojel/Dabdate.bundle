# -*- coding: utf-8 -*-

###################################################################################################

PLUGIN_TITLE     = "Dabdate"
PLUGIN_PREFIX    = "/video/dabdate"
ICON_DEFAULT     = "icon-default.png"
ROOT_URL         = "http://www.dabdate.com"
RE_VIDEO_ID      = Regex('idx=(\d+)')
RE_VIDEO_ID2     = Regex('thumb/df_(\d+)\.jpg')

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

###------ direct video link
VIDEO_MAP_TABLE  = "vidmap.json"
VIDEO_URL        = "http://vod{host:d}.dabdate.com/video2/{name:s}{mon:02d}{date:02d}-{bitrate:d}.mp4?test@example.com"
RE_DATE          = Regex('(.*) \d{4},(\d{2}),(\d{2})')
RE_EPISODE       = Regex(u'(.*) (\d+|최종)회 *$')
RE_SUBTITLE      = Regex('(.+\S)\((.+?)\) *$')

HOST_MAP = {
    'au1' : 48,   # au(medium)
    'au2' : 48,   # au(low)
    'eu1' : 33,   # eu(medium)
    'eu2' : 34,   # eu(low)
    'sa1' : 53,   # sa(medium)
    'sa2' : 54,   # sa(low)
    'la1' : 30,   # la(medium)
    'la2' : 31,   # la(low)
    'ny1' : 53,   # ny(medium)
    'ny2' : 55,   # ny(low)
}
BITRATE_MAP = {
    '1' : 640,    # medium
    '2' : 320,    # low
}

###################################################################################################
def Start():
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

  ObjectContainer.title1     = PLUGIN_TITLE
  ObjectContainer.view_group = "InfoList"
  DirectoryObject.thumb      = R(ICON_DEFAULT)

  HTTP.CacheTime = CACHE_1MINUTE
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
    html = HTML.ElementFromURL(url, encoding='cp949')
  except:
    raise Ex.MediaNotAvailable

  oc = ObjectContainer(view_group="List")

  base_url = ROOT_URL   # no more mobile page support

  for node in html.xpath("//td/div/b[@class='big']"):
    title = node.text
    thumb = node.xpath('ancestor::tr[2]//img')[0].get('src')
    #video_id = RE_VIDEO_ID.search(node.xpath('ancestor::table[2]//a')[0].get('href')).group(1)
    video_id = RE_VIDEO_ID2.search(thumb).group(1)
    video_url = base_url + '/player.php?idx=%s&pr=%s&local=%s' % (video_id, quality, localsrv)
    Log.Debug(u"video: %s = %s" %(title, video_url))
    Log.Debug(u"thumb: "+thumb)
    is_free = True if node.xpath("ancestor::tr[2]//img[@src='/image/ico_free.gif']") else False

    vtitle = title
    if is_free:
      vtitle = '*'+title
    elif Prefs['direct_link']:
      vidmap_str = Resource.Load(VIDEO_MAP_TABLE)
      vidmap = JSON.ObjectFromString(vidmap_str)

      match = RE_DATE.search(title)
      title2, mon, dt = match.group(1,2,3) if match else ('unknown','13','13')
      match = RE_EPISODE.match(title2)
      if match: title2 = match.group(1)
      else:
        match = RE_SUBTITLE.match(title2)
        if match: title2 = match.group(1)
      Log.Debug(u"title: "+title2)

      if title2 in vidmap:
        video_url = VIDEO_URL.format(host=HOST_MAP[localsrv+quality],
                                     name=vidmap[title2],
                                     mon=int(mon),
                                     date=int(dt),
                                     bitrate=BITRATE_MAP[quality])
        vtitle = '^'+title
    oc.add(VideoClipObject(url=video_url, title=vtitle, thumb=Function(Thumb, url=thumb)))
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
