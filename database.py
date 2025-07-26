import sqlite3
import datetime

DB_NAME = 'ember_rhythm.db'

# ... (initialize, add_word, get_all_decks, etc. 保持不變) ...
# ... 為了確保您的檔案是最新的，我將提供完整的檔案 ...

def initialize():
    """初始化資料庫，建立 words 和 decks 資料表"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS decks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL,
        meaning TEXT NOT NULL,
        deck_id INTEGER NOT NULL,
        example_sentence TEXT,
        word_audio_path TEXT,
        example_audio_path TEXT,
        srs_level INTEGER DEFAULT 0,
        next_review_date TIMESTAMP NOT NULL,
        date_added TIMESTAMP NOT NULL,
        last_modified_date TIMESTAMP NOT NULL,
        FOREIGN KEY (deck_id) REFERENCES decks (id)
    )
    ''')

    cursor.execute("SELECT COUNT(*) FROM decks")
    if cursor.fetchone()[0] == 0:
        default_decks = [("A1",), ("A2",), ("B1",), ("B2",), ("C1",), ("C2",)]
        cursor.executemany("INSERT INTO decks (name) VALUES (?)", default_decks)

    conn.commit()
    conn.close()

def get_all_decks():
    """獲取所有卡組"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM decks ORDER BY id ASC")
    decks = cursor.fetchall()
    conn.close()
    return decks

def add_deck(name):
    """新增一個卡組"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO decks (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        return None
    except sqlite3.IntegrityError:
        return f"卡組名稱 '{name}' 已經存在！"
    except Exception as e:
        return f"新增卡組時發生錯誤: {e}"

def update_deck_name(deck_id, new_name):
    """更新卡組名稱"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE decks SET name = ? WHERE id = ?", (new_name, deck_id))
        conn.commit()
        conn.close()
        return None
    except sqlite3.IntegrityError:
        return f"卡組名稱 '{new_name}' 已經存在！"
    except Exception as e:
        return f"更新卡組時發生錯誤: {e}"

def delete_deck(deck_id):
    """刪除一個卡組 (前提是卡組內沒有單字)"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM words WHERE deck_id = ?", (deck_id,))
        if cursor.fetchone()[0] > 0:
            return "無法刪除：卡組中仍有單字。"
        
        cursor.execute("DELETE FROM decks WHERE id = ?", (deck_id,))
        conn.commit()
        conn.close()
        return None
    except Exception as e:
        return f"刪除卡組時發生錯誤: {e}"

def add_word(word_data):
    """新增一個單字到資料庫 (使用 deck_id)"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        now = datetime.datetime.now()
        cursor.execute('''
        INSERT INTO words (word, meaning, deck_id, example_sentence, word_audio_path, example_audio_path, next_review_date, date_added, last_modified_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            word_data['word'], word_data['meaning'], word_data['deck_id'],
            word_data['example'], word_data['word_audio'], word_data['example_audio'],
            now, now, now
        ))
        conn.commit()
        conn.close()
        return None
    except Exception as e:
        return f"發生未知的資料庫錯誤: {e}"

def get_all_words(search_term="", deck_filter="全部", srs_filter="全部"):
    """使用 JOIN 查詢，獲取單字以及其所屬的卡組名稱"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    base_query = "SELECT w.*, d.name as deck_name FROM words w JOIN decks d ON w.deck_id = d.id"
    conditions = []
    params = []

    if search_term:
        conditions.append("w.word LIKE ?")
        params.append(f"%{search_term}%")
    
    if deck_filter != "全部":
        conditions.append("d.name = ?")
        params.append(deck_filter)

    if srs_filter != "全部":
        conditions.append("w.srs_level = ?")
        params.append(int(srs_filter))

    if conditions:
        query = f"{base_query} WHERE {' AND '.join(conditions)} ORDER BY w.word ASC"
    else:
        query = f"{base_query} ORDER BY w.word ASC"
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def find_word_by_name(word_text):
    """根據單字名稱精確查找單字。"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = "SELECT w.*, d.name as deck_name FROM words w JOIN decks d ON w.deck_id = d.id WHERE w.word = ?"
    cursor.execute(query, (word_text,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_review_words_for_deck(deck_id):
    """獲取指定卡組ID中，所有到期需要複習的單字"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    now = datetime.datetime.now()
    
    query = "SELECT * FROM words WHERE deck_id = ? AND next_review_date <= ? ORDER BY next_review_date ASC"
    cursor.execute(query, (deck_id, now))
    
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_word(word_id, new_data):
    """根據 ID 更新一個單字 (已加入 srs_level 的更新)"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        now = datetime.datetime.now()
        query = '''UPDATE words SET 
                      word = ?, meaning = ?, deck_id = ?, 
                      example_sentence = ?, word_audio_path = ?,
                      example_audio_path = ?, srs_level = ?, 
                      last_modified_date = ? 
                   WHERE id = ?'''
        
        cursor.execute(query, (
            new_data['word'], new_data['meaning'], new_data['deck_id'],
            new_data['example'], new_data['word_audio'],
            new_data['example_audio'], new_data['srs_level'], # ★★★ 新增 srs_level ★★★
            now, word_id
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

def update_srs_data(word_id, new_srs_level, next_review_date):
    """更新單字的SRS等級和下次複習日期"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = "UPDATE words SET srs_level = ?, next_review_date = ? WHERE id = ?"
        cursor.execute(query, (new_srs_level, next_review_date, word_id))
        conn.commit()
        conn.close()
        return None
    except Exception as e:
        return f"更新SRS資料時失敗: {e}"
