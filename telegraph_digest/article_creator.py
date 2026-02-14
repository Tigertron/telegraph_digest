from pprint import pprint

from telegraph import Telegraph
import yaml

from digest import load_posts


def create_article(posts, config_name):
    token = yaml.load(open(config_name).read())['telegraph']['token']
    telegraph = Telegraph(token)
    content_list = []
    for number, post in enumerate(posts.values()):
        title = post['self'].title
        url = post['img_data']['url']
        content_list.extend([
            {
                'tag': 'p',
                'children': ['%d. %s' % (number + 1, title)]
            },
            {
                'tag': 'img',
                'attrs': {'src': url}
            },
            {
                'tag': 'br'
            }
        ])
    if (not content_list)
        content_list = [ {
                    'tag': 'p',
                    'children': "no boobs here :(("
                }
            ]
    response = telegraph.create_page(
        'Boobs',
        content_list,
        author_name='Boobs Digest Bot',
        author_url='https://t.me/boobs_digest_bot'
    )
    return response['url']
