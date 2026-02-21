import telepot
import yaml

from article_creator import create_article
from digest import load_posts


def send_boobs_to_chat(chat_id):
    config_name = 'prod.yml'
    token = yaml.safe_load(open(config_name).read())['telegram']['token']
    bot = telepot.Bot(token)
    result = load_posts(config_name, None)
    posts = result['posts']
    analyzed = result['analyzed']
    repeats = result['repeats']
    if not posts:
        print('No new posts to publish')
        return
    url = create_article(posts, config_name, stats={'analyzed': analyzed, 'repeats': repeats})
    bot.sendMessage(chat_id, url)


if __name__ == '__main__':
    send_boobs_to_chat('-1001052042617')
