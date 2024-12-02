import sqlite3

def init_db():
    conn = sqlite3.connect('chat_bot.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, partner_id INTEGER, interest TEXT)')

    # Проверка наличия колонки in_queue и добавление ее, если она отсутствует
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'in_queue' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN in_queue INTEGER DEFAULT 0')

    conn.commit()
    conn.close()

def get_partner(user_id):
    conn = sqlite3.connect('chat_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT partner_id FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def set_partner(user_id, partner_id):
    conn = sqlite3.connect('chat_bot.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET partner_id = ? WHERE id = ?', (partner_id, user_id))
    conn.commit()
    conn.close()

def set_interest(user_id, interest):
    conn = sqlite3.connect('chat_bot.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (id, interest, in_queue) VALUES (?, ?, 0)', (user_id, interest))
    conn.commit()
    conn.close()

def get_interest(user_id):
    conn = sqlite3.connect('chat_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT interest FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def set_in_queue(user_id, status):
    conn = sqlite3.connect('chat_bot.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET in_queue = ? WHERE id = ?', (status, user_id))
    conn.commit()
    conn.close()

def get_in_queue(user_id):
    conn = sqlite3.connect('chat_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT in_queue FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0
