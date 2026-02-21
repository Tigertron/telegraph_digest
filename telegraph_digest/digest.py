# -*- coding: utf-8 -*-

from pprint import pprint

import yaml
import praw
import pymongo

import utils


HOT_LIMIT = 10


def normalization_coef(data):
    return 1 / (sum(data) / len(data))


def get_old_content_collection(config):
    mongo_cfg = config.get('mongo', {})
    client = pymongo.MongoClient(
        host=mongo_cfg.get('host', 'localhost'),
        port=mongo_cfg.get('port', 27017),
        username=mongo_cfg.get('username'),
        password=mongo_cfg.get('password'),
        authSource=mongo_cfg.get('auth_source', 'admin')
    )
    db_name = mongo_cfg.get('db', 'telegraph_digest')
    collection_name = mongo_cfg.get('collection', 'content')
    return client[db_name][collection_name]


def was_before(url, old_content):
    doc = {
        'digest': 'boobs',
        'url': url
    }

    if old_content.find_one(doc) is None:
        old_content.insert_one(doc)
        return False

    return True


def good_stufff(subs, reddit, old_content):
    # Returns: dict with keys 'posts', 'analyzed', 'repeats'

    submissons_with_cross_scores = dict()
    analyzed = 0
    repeats = 0
    for submission in reddit.subreddit(subs).top('month'):
        analyzed += 1
        sub_obj = {
            'self': submission,
            'cross_score': submission.score,
            'img_data': utils.do_magic(submission)
        }

        if sub_obj['img_data']['type'] in [utils.TYPE_GIF, utils.TYPE_IMG]:
            if was_before(sub_obj['img_data']['url'], old_content):
                repeats += 1
            else:
                submissons_with_cross_scores[submission.id] = sub_obj
                # print submission.score, sub_obj['img_data']['url']
        else:
            print(f"Skipping url '{sub_obj['img_data']['url']}' because type is '{sub_obj['img_data']['type']}'")
        if len(submissons_with_cross_scores) == HOT_LIMIT:
            break

    return {
        'posts': submissons_with_cross_scores,
        'analyzed': analyzed,
        'repeats': repeats,
    }


def supply(sub, config, old_content):
    # Returns: dict with keys 'posts', 'analyzed', 'repeats'

    reddit = praw.Reddit(user_agent=config['reddit']['user_agent'],
                        client_id=config['reddit']['client_id'],
                        client_secret=config['reddit']['client_secret'])
    subs = 'boobs+Boobies+Stacked+BustyPetite+TittyDrop'
    return good_stufff(subs, reddit, old_content)


def load_posts(config_filename, sub):
    # Returns: dict with keys 'posts', 'analyzed', 'repeats'

    with open(config_filename) as config_file:
        config = yaml.safe_load(config_file.read())
    old_content = get_old_content_collection(config)
    return supply(sub, config, old_content)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='prod.yml')
    # parser.add_argument('--sub')
    args = parser.parse_args()
    pprint(main(args.config, 'boobs'))
