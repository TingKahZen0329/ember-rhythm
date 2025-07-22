# database.py

import sqlite3
import datetime

DB_NAME = 'ember_rhythm.db'

def initialize():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL UNIQUE,
        meaning TEXT NOT NULL,
        cefr_level TEXT NOT NULL,
        example_sentence TEXT,
        word_audio_path TEXT,
        example_audio_path TEXT,
        srs_level INTEGER DEFAULT 0,
        next_review_date TIMESTAMP NOT NULL,
        date_added TIMESTAMP NOT NULL,
        last_modified_date TIMESTAMP NOT NULL 
    )
    ''')
    conn.commit()
    conn.close()


def add_word(word_data):
    """新增一個單字到資料庫"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        now = datetime.datetime.now()
        cursor.execute('''
        INSERT INTO words (word, meaning, cefr_level, example_sentence, word_audio_path, example_audio_path, next_review_date, date_added, last_modified_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            word_data['word'], word_data['meaning'], word_data['cefr_level'],
            word_data['example'], word_data['word_audio'], word_data['example_audio'],
            now, now, now
        ))
        conn.commit()
        conn.close()
        return None
    except sqlite3.IntegrityError:
        return f"單字 '{word_data['word']}' 已經存在於資料庫中！"
    except Exception as e:
        return f"發生未知的資料庫錯誤: {e}"

def get_all_words(search_term=""):
    """從資料庫獲取所有或符合搜尋條件的單字"""
    conn = sqlite3.connect(DB_NAME)
    # 讓回傳結果可以像字典一樣用欄位名存取
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if search_term:
        # 使用 LIKE 進行模糊搜尋
        query = "SELECT * FROM words WHERE word LIKE ? ORDER BY word ASC"
        cursor.execute(query, ('%' + search_term + '%',))
    else:
        query = "SELECT * FROM words ORDER BY word ASC"
        cursor.execute(query)
        
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_word(word_id, new_data):
    """根據 ID 更新一個單字"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        now = datetime.datetime.now()
        query = '''UPDATE words SET 
                      word = ?, 
                      meaning = ?, 
                      cefr_level = ?, 
                      example_sentence = ?, 
                      word_audio_path = ?,
                      example_audio_path = ?,
                      last_modified_date = ? 
                   WHERE id = ?'''
        
        cursor.execute(query, (
            new_data['word'],
            new_data['meaning'],
            new_data['cefr_level'],
            new_data['example'],
            new_data['word_audio'],
            new_data['example_audio'],
            now,
            word_id
        ))
        conn.commit()
        conn.close()
        return None
    except Exception as e:
        return f"更新失敗: {e}"


def delete_word(word_id):
    """根據 ID 刪除一個單字"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM words WHERE id = ?", (word_id,))
        conn.commit()
        conn.close()
        return None
    except Exception as e:
        return f"刪除失敗: {e}"