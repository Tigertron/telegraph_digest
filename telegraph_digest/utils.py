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
        header = requests.head(url).headers
        if 'Content-Type' in header:
            return header['Content-Type']
        else:
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

    if urlparse(url).netloc == 'imgur.com':
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
