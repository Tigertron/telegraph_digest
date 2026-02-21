# encoding:utf-8

from urllib.parse import urlparse
import requests
import os
import imghdr

from imgurpython import ImgurClient
import yaml


TYPE_IMG = 'img'
CONTENT_JPEG = 'image/jpeg'
CONTENT_PNG = 'image/png'
TYPE_GIF = 'gif'
CONTENT_GIF = 'image/gif'
CONTENT_MP4 = 'video/mp4'
TYPE_TEXT = 'text'
TYPE_OTHER = 'other'
TYPE_ALBUM = 'album'


TEMP_FOLDER = 'tmp'


def do_magic(submission):
    stuff = get_url(submission)
    return {
        'type': stuff[0],
        'url': stuff[1],
        'extension': stuff[2]
    }


def get_url(submission, mp4_instead_gif=False):
    '''
    return TYPE, URL, EXTENSION
    E.x.: return 'img', 'http://example.com/pic.png', 'png'
    '''
    
    def what_is_inside(url):
        try:
            resp = requests.head(url, timeout=10, allow_redirects=True)
            header = resp.headers
            if 'Content-Type' in header:
                return header['Content-Type']
            return ''
        except requests.RequestException as e:
            # DNS, timeout, etc
            print (f"Error getting URL {url}: {e}")
            return ''

    url = submission.url
    url_content = what_is_inside(url)

    if (CONTENT_JPEG == url_content or CONTENT_PNG == url_content):
        return TYPE_IMG, url, url_content.split('/')[1]

    if CONTENT_GIF in url_content:
        if url.endswith('.gif') and mp4_instead_gif:
            # Let's try to find .mp4 file.
            url_mp4 = url[:-4] + '.mp4'
            if CONTENT_MP4 == what_is_inside(url_mp4):
                return TYPE_GIF, url_mp4, 'mp4'
        return TYPE_GIF, url, 'gif'
    
    if url.endswith('.gifv'):
        if mp4_instead_gif:
            url_mp4 = url[:-5] + '.mp4'
            if CONTENT_MP4 == what_is_inside(url_mp4):
                return TYPE_GIF, url_mp4, 'mp4'
        if CONTENT_GIF in what_is_inside(url[0:-1]):
            return TYPE_GIF, url[0:-1], 'gif'

    if submission.is_self is True:
        # Self submission with text
        return TYPE_TEXT, None, None

    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path_parts = [p for p in parsed.path.split('/') if p]

    # www.redgifs.com, redgifs.com, v3.redgifs.com 
    if 'redgifs.com' in netloc and len(path_parts) >= 2 and path_parts[0] == 'watch':
        gif_id = path_parts[1]
        try:
            from redgifs import API
            api = API()
            api.login()
            gif = api.get_gif(gif_id)
            # gif.urls contains a lot of different links. But only gif.urls.sd is displayed on telegraph
            if gif.urls and gif.urls.sd:
                return TYPE_GIF, gif.urls.sd, 'mp4'
        except Exception as e:
            print (f"Error getting Redgifs GIF {gif_id}: {e}")
        return TYPE_OTHER, url, None

    if parsed.netloc == 'imgur.com':
        # Imgur
        imgur_config = yaml.safe_load(open('prod.yml').read())
        imgur_client = ImgurClient(imgur_config['imgur']['client_id'], imgur_config['imgur']['client_secret'])
        path_parts = urlparse(url).path.split('/')
        if path_parts[1] == 'gallery':
            # TODO: gallary handling
            return TYPE_OTHER, url, None
        elif path_parts[1] == 'topic':
            # TODO: topic handling
            return TYPE_OTHER, url, None
        elif path_parts[1] == 'a':
            # An imgur album
            album = imgur_client.get_album(path_parts[2])
            story = dict()
            for num, img in enumerate(album.images):
                number = num + 1
                what = TYPE_IMG
                link = img['link']
                ext = img['type'].split('/')[1]
                if img['animated']:
                    what = TYPE_GIF
                    link = img['mp4'] if mp4_instead_gif else img['gifv'][:-1]
                    ext = 'mp4' if mp4_instead_gif else 'gif'
                story[number] = {
                    'url': link,
                    'what': what,
                    'ext': ext
                }
            if len(story) == 1:
                return story[1]['what'], story[1]['url'], story[1]['ext']
            return TYPE_ALBUM, story, None
        else:
            # Just imgur img
            img = imgur_client.get_image(path_parts[1].split('.')[0])
            if not img.animated:
                return TYPE_IMG, img.link, img.type.split('/')[1]
            else:
                if mp4_instead_gif:
                    return TYPE_GIF, img.mp4, 'mp4'
                else:
                    # return 'gif', img.link, 'gif'
                    return TYPE_GIF, img.gifv[:-1], 'gif'
    else:
        return TYPE_OTHER, url, None
