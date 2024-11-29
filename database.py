import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    
    # 创建对话标签表
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversation_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    conn.commit()
    conn.close()

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

def get_conversation_history(tag_id):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('SELECT role, content FROM messages WHERE tag_id = ? ORDER BY created_at',
              (tag_id,))
    messages = c.fetchall()
    conn.close()
    return [{"role": role, "content": content} for role, content in messages]

def delete_tag(tag_id):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('DELETE FROM messages WHERE tag_id = ?', (tag_id,))
    c.execute('DELETE FROM conversation_tags WHERE id = ?', (tag_id,))
    conn.commit()
    conn.close() 