from pprint import pprint

from telegraph import Telegraph
import yaml

from digest import load_posts


def create_article(posts, config_name, stats=None):
    token = yaml.safe_load(open(config_name).read())['telegraph']['token']
    telegraph = Telegraph(token)
    content_list = []
    for number, post in enumerate(posts.values()):
        title = post['self'].title
        url = post['img_data']['url']
        ext = post['img_data'].get('extension') or ''
        # title
        content_list.extend([{
                'tag': 'p',
                'children': ['%d. %s' % (number + 1, title)]
            }])
        # content
        if ext == 'mp4':
            content_list.extend([
                {
                    'tag': 'video',
                    'attrs': {'src': url}
                },
                {
                    'tag': 'p',
                    'children': [{
                        'tag': 'a', 'attrs': {'href': url}, 
                        'children': ['Source link (download in progress)']
                    }]
                }
            ])
        else:
            content_list.extend([
                {
                    'tag': 'img',
                    'attrs': {'src': url}
                }
            ])
        # next line
        content_list.extend([ { 'tag': 'br' } ])
    
    if stats is not None:
        content_list.append({
            'tag': 'p',
            'children': ['Posts analyzed: %d, duplicates: %d.' % (stats['analyzed'], stats['repeats'])]
        })
        content_list.append({'tag': 'hr'})
    response = telegraph.create_page(
        'Boobs',
        content_list,
        author_name='Boobs Digest Bot',
        author_url='https://t.me/boobs_digest_bot'
    )
    return response['url']
