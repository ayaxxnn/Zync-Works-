import sqlite3
from datetime import datetime, timedelta
import random
import string

conn = sqlite3.connect('bot.db', check_same_thread=False)
c = conn.cursor()

def db_init():
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                   user_id INTEGER PRIMARY KEY,
                   redeemed INTEGER DEFAULT 0,
                   premium_until DATETIME,
                   banned INTEGER DEFAULT 0
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS premium_keys (
                   key TEXT PRIMARY KEY,
                   days INTEGER,
                   used INTEGER DEFAULT 0
                 )''')
    conn.commit()

def add_user(user_id):
    c.execute('INSERT OR IGNORE INTO users(user_id) VALUES (?)', (user_id,))
    conn.commit()

def is_user_banned(user_id):
    c.execute('SELECT banned FROM users WHERE user_id=?', (user_id,))
    result = c.fetchone()
    return result and result[0] == 1

def redeem_key(user_id):
    # check if user already redeemed free once
    c.execute('SELECT redeemed FROM users WHERE user_id=?', (user_id,))
    res = c.fetchone()
    if res and res[0] == 1:
        return True
    else:
        # mark redeemed
        c.execute('UPDATE users SET redeemed=1 WHERE user_id=?', (user_id,))
        conn.commit()
        return False

def generate_key(days):
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    c.execute('INSERT INTO premium_keys (key, days) VALUES (?, ?)', (key, days))
    conn.commit()
    return key

def is_key_valid(key):
    c.execute('SELECT used FROM premium_keys WHERE key=?', (key,))
    row = c.fetchone()
    return row and row[0] == 0

def use_premium_key(user_id, key):
    c.execute('SELECT days, used FROM premium_keys WHERE key=?', (key,))
    row = c.fetchone()
    if not row or row[1] == 1:
        return False

    days = row[0]
    # extend user's premium_until date
    c.execute('SELECT premium_until FROM users WHERE user_id=?', (user_id,))
    current = c.fetchone()
    now = datetime.utcnow()
    if current and current[0]:
        premium_until = datetime.strptime(current[0], '%Y-%m-%d %H:%M:%S')
        if premium_until < now:
            premium_until = now
    else:
        premium_until = now

    new_premium_until = premium_until + timedelta(days=days)
    c.execute('UPDATE users SET premium_until=?, redeemed=1 WHERE user_id=?', (new_premium_until.strftime('%Y-%m-%d %H:%M:%S'), user_id))
    c.execute('UPDATE premium_keys SET used=1 WHERE key=?', (key,))
    conn.commit()
    return True

def notify_admin_premium(user_id):
    # This function will be called after premium is activated,
    # Send a message to admin externally via bot instance (pass bot instance if needed)
    pass  # integrate this with bot.send_message externally
