import os.path
import sys
import re

import sqlite3
from datetime import datetime, timedelta
import base64

import feedparser
from mastodon import Mastodon
import requests


sql = sqlite3.connect('cache.db')
db = sql.cursor()
db.execute('''CREATE TABLE IF NOT EXISTS tweets (tweet text, toot text,
           twitter text, mastodon text, instance text)''')

include_author = False
use_privacy_frontends = True

rss_feed_url = sys.argv[1]
mastodon_instance = sys.argv[2]
mastodon_username = sys.argv[3]
mastodon_email_address = sys.argv[4].lower()
mastodon_password = base64.b64decode(sys.argv[5]).decode("utf-8")
tags_to_add = sys.argv[6]
days_to_check = int(sys.argv[7])

rss_feed_domain = re.sub('^[a-z]*://', '', rss_feed_url)
rss_feed_domain = re.sub('/.*$', '', rss_feed_domain)

if not os.path.isfile(mastodon_instance + '.secret'):
    if Mastodon.create_app(
        rss_feed_domain,
        api_base_url = 'https://' + mastodon_instance,
        to_file = mastodon_instance+'.secret'
    ):
        print('Successfully created the application on instance ' + mastodon_instance)
    else:
        print('Failed to create the application on instance ' + mastodon_instance)
        sys.exit(1)

try:
    mastodon_api = Mastodon(
        client_id = mastodon_instance + '.secret',
        api_base_url = 'https://' + mastodon_instance
    )
    mastodon_api.log_in(
        mastodon_email_address,
        password = mastodon_password,
        scopes = ['read', 'write'],
        to_file = mastodon_username + ".secret"
    )
except:
    print("ERROR: Failed to log " + mastodon_username + " into " + mastodon_instance)
    sys.exit(1)

feed = feedparser.parse(rss_feed_url)
print('Retrieved ' + str(len(feed.entries)) + ' feed entries!')

for feed_entry in reversed(feed.entries):
    if id in feed_entry:
        id = feed_entry.id
    else:
        if len(feed_entry.title) > 0:
            id = feed_entry.title
        else:
            id = feed_entry.published_parsed

    print('Processing entry: ' + id)

    db.execute('SELECT * FROM tweets WHERE tweet = ? AND twitter = ?  and mastodon = ? and instance = ?', (id, rss_feed_domain, mastodon_username, mastodon_instance))  # noqa
    last = db.fetchone()

    feed_entry_age = datetime.now() - datetime(
        feed_entry.published_parsed.tm_year, feed_entry.published_parsed.tm_mon, feed_entry.published_parsed.tm_mday,
        feed_entry.published_parsed.tm_hour, feed_entry.published_parsed.tm_min, feed_entry.published_parsed.tm_sec)

    if last is None and feed_entry_age < timedelta(days = days_to_check):
        toot_body = feed_entry.title
        toot_media = []

        if 'summary' in feed_entry:
            for p in re.finditer(r"https://pbs.twimg.com/[^ \xa0\"]*", feed_entry.summary):
                media_url = p.group(0)
                print(' > Found Twitter media: ' + media_url)
                try:
                    media = requests.get(media_url)
                    media_posted = mastodon_api.media_post(
                        media.content,
                        mime_type = media.headers.get('content-type'))
                    toot_media.append(media_posted['id'])
                except:
                    print(' > Could not upload to Mastodon!')

            for p in re.finditer(r"https://i.redd.it/[a-zA-Z0-9]*.(gif|jpg|mp4|png|webp)", feed_entry.summary):
                media_url = p.group(0)
                print(' > Found Reddit media: ' + media_url)
                try:
                    media = requests.get(media_url)
                    media_posted = mastodon_api.media_post(
                        media.content, mime_type=media.headers.get('content-type'))
                    toot_media.append(media_posted['id'])
                except:
                    print('   > Could not upload to Mastodon!')

        if include_author and 'authors' in feed_entry:
            toot_body += '\nSource: ' + feed_entry.authors[0].name

        feed_entry_link = feed_entry.link

        if use_privacy_frontends:
            feed_entry_link = feed_entry_link.replace('old.reddit.com', 'libreddit.net')
            feed_entry_link = feed_entry_link.replace('reddit.com', 'libreddit.net')
            feed_entry_link = feed_entry_link.replace('twitter.com', 'nitter.net')

        toot_body += '\n\n' + feed_entry_link

        # TODO: Don't readd them if they are already contained in the body
        if tags_to_add:
            toot_body += '\n\n' + tags_to_add

        if toot_media is not None:
            toot = mastodon_api.status_post(
                toot_body,
                in_reply_to_id = None,
                media_ids = toot_media,
                sensitive = False,
                visibility = 'public',
                spoiler_text = None)

            if "id" in toot:
                db.execute("INSERT INTO tweets VALUES ( ? , ? , ? , ? , ? )",
                        (id, toot["id"], rss_feed_url, mastodon_username, mastodon_instance))
                sql.commit()
    sys.exit(1)