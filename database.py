import sqlite3

DB_PATH = "cache.db"

def init_db():
    sql = sqlite3.connect(DB_PATH)
    db = sql.cursor()
    db.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            feed_entry_id TEXT,
            toot_id TEXT,
            rss_feed_url TEXT,
            mastodon_username TEXT,
            mastodon_instance TEXT)''')

    sql.commit()
    return sql, db

def get_last_entry_posted(db, entry_id, username, instance):
    db.execute(
        'SELECT * FROM entries WHERE feed_entry_id = ? AND mastodon_username = ? AND mastodon_instance = ?',
        (entry_id, username, instance))
    return db.fetchone()

def save_posted_entry(sql, db, feed_entry_id, toot_id, feed_url, username, instance):
    db.execute("INSERT INTO entries VALUES ( ? , ? , ? , ? , ? )",
            (feed_entry_id, toot_id, feed_url, username, instance))
    sql.commit()
