#coding:utf8
import downloader
import ree as re
from utils import Soup, Downloader, clean_title, lazy
import json
import os
from translator import tr_
from timee import sleep


class Image(object):
    def __init__(self, url, id):
        self.url = url
        self.id = id
        ext = os.path.splitext(url)[1]
        self.filename = u'{}{}'.format(id, ext)


@Downloader.register
class Downloader_worldcos(Downloader):
    type = 'worldcos'
    URLS = ['worldcosplay.net']
    display_name = 'World Cosplay'
    
    def init(self):
        if 'worldcosplay.net' in self.url.lower():
            self.url = self.url.replace('http://', 'https://')
        else:
            self.url = u'https://worldcosplay.net/member/{}'.format(self.url)
        self.url = self.url.replace('m.', '')

    @lazy
    def name(self):
        return clean_title(get_name(self.url))

    def read(self):
        self.title = self.name

        imgs = get_imgs(self.url, self.name, cw=self.cw)

        for img in imgs:
            self.urls.append(img.url)
            self.filenames[img.url] = img.filename

        self.title = self.name


def get_name(url):
    html = downloader.read_html(url)
    soup = Soup(html)
    name = re.find(r'"nickname" *: *"(.+?)"', html)
    if not name:
        raise Exception('no name')
    return json.loads('"{}"'.format(name))

            
def get_imgs(url, title=None, cw=None):
    username = re.findall('/member/([^/]+)', url)[0]

    url = 'https://worldcosplay.net/member/{}'.format(username)
    html = downloader.read_html(url)
    soup = Soup(html)
    userid = re.find('"member_id" *: *([0-9]+)', html)
    if userid is None:
        raise Exception('no userid')
    print('userid:', userid)

    p = 1
    imgs = []
    while True:
        url = 'http://worldcosplay.net/en/api/member/photos?member_id={}&page={}&limit=100000&rows=16&p3_photo_list=1'.format(userid, p)

        html = downloader.read_html(url)
        j = json.loads(html)
        list = j['list']

        print(len(list))
        if not list:
            break
        
        for img in list:
            photo = img['photo']
            id = photo['id']
            url_img = photo['sq300_url']
            sizes = re.findall('/max-([0-9]+)/', url_img)
            if sizes:
                size = sizes[0]
            else:
                size = 3000
            url_img = url_img.replace('-350x600', '-{}'.format(size))
            img = Image(url_img, id)
            imgs.append(img)

        p += 1

        if cw is not None:
            if not cw.alive:
                break
            cw.setTitle(u'{}  {} - {}'.format(tr_(u'읽는 중...'), title, len(imgs)))
 
        
    return imgs
