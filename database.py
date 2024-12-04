import sqlite3
from datetime import datetime

def migrate_db():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    
    # 检查 tokens_used 列是否存在
    c.execute("PRAGMA table_info(conversation_tags)")
    columns = [column[1] for column in c.fetchall()]
    
    # 如果需要，添加新的列
    if 'tokens_used' not in columns:
        c.execute('''ALTER TABLE conversation_tags 
                     ADD COLUMN tokens_used INTEGER DEFAULT 0''')
    
    if 'cost' not in columns:
        c.execute('''ALTER TABLE conversation_tags 
                     ADD COLUMN cost REAL DEFAULT 0.0''')
    
    conn.commit()
    conn.close()

def init_db():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    
    # 创建对话标签表
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversation_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tokens_used INTEGER DEFAULT 0,
            cost REAL DEFAULT 0.0
        )
    ''')
    
    # 创建消息历史表
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_id INTEGER,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tag_id) REFERENCES conversation_tags (id)
        )
    ''')
    
    # 添加设置表
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    
    conn.commit()
    conn.close()
    
    # 运行数据库迁移
    migrate_db()

def create_tag(name):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('INSERT INTO conversation_tags (name) VALUES (?)', (name,))
    tag_id = c.lastrowid
    conn.commit()
    conn.close()
    return tag_id

def get_all_tags():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('SELECT id, name, created_at FROM conversation_tags ORDER BY created_at DESC')
    tags = c.fetchall()
    conn.close()
    return tags

def add_message(tag_id, role, content):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (tag_id, role, content) VALUES (?, ?, ?)',
              (tag_id, role, content))
    conn.commit()
    conn.close()

def get_conversation_history(tag_id, limit=30):
    """
    获取指定标签的对话历史记录，默认返回最近30条消息（15轮对话）
    """
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT role, content 
        FROM messages 
        WHERE tag_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (tag_id, limit))
    
    messages = c.fetchall()
    conn.close()
    
    # 因为我们是倒序获取的，需要反转顺序
    messages.reverse()
    
    return [{"role": msg[0], "content": msg[1]} for msg in messages]

def delete_tag(tag_id):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('DELETE FROM messages WHERE tag_id = ?', (tag_id,))
    c.execute('DELETE FROM conversation_tags WHERE id = ?', (tag_id,))
    conn.commit()
    conn.close()

def update_tag_usage(tag_id, tokens, cost):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''UPDATE conversation_tags 
                 SET tokens_used = tokens_used + ?,
                     cost = cost + ?
                 WHERE id = ?''', (tokens, cost, tag_id))
    conn.commit()
    conn.close()

def get_tag_usage(tag_id):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''SELECT tokens_used, cost FROM conversation_tags WHERE id = ?''', (tag_id,))
    result = c.fetchone()
    conn.close()
    return {
        'tokens': result[0] if result else 0,
        'cost': result[1] if result else 0.0
    }

def get_total_usage():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''SELECT SUM(tokens_used), SUM(cost) FROM conversation_tags''')
    result = c.fetchone()
    conn.close()
    return {
        'tokens': result[0] if result[0] else 0,
        'cost': result[1] if result[1] else 0.0
    }

def update_api_key(api_key):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
              ('api_key', api_key))
    conn.commit()
    conn.close()

def get_api_key():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('SELECT value FROM settings WHERE key = ?', ('api_key',))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None 