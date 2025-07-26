import sqlite3
import datetime

DB_NAME = 'ember_rhythm.db'

def initialize():
    """初始化資料庫，建立 words 和 decks 資料表"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 建立新的 decks 資料表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS decks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    ''')

    # 修改 words 資料表，用 deck_id 取代 cefr_level
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL UNIQUE,
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

    # 檢查 decks 是否為空，如果為空則插入預設卡組
    cursor.execute("SELECT COUNT(*) FROM decks")
    if cursor.fetchone()[0] == 0:
        default_decks = [("A1",), ("A2",), ("B1",), ("B2",), ("C1",), ("C2",)]
        cursor.executemany("INSERT INTO decks (name) VALUES (?)", default_decks)

    conn.commit()
    conn.close()

# --- 卡組 (Decks) 相關函式 ---
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
        # 檢查卡組是否為空
        cursor.execute("SELECT COUNT(*) FROM words WHERE deck_id = ?", (deck_id,))
        if cursor.fetchone()[0] > 0:
            return "無法刪除：卡組中仍有單字。"
        
        cursor.execute("DELETE FROM decks WHERE id = ?", (deck_id,))
        conn.commit()
        conn.close()
        return None
    except Exception as e:
        return f"刪除卡組時發生錯誤: {e}"

# --- 單字 (Words) 相關函式 (已更新) ---
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
    except sqlite3.IntegrityError:
        return f"單字 '{word_data['word']}' 已經存在於資料庫中！"
    except Exception as e:
        return f"發生未知的資料庫錯誤: {e}"

def get_all_words(search_term="", deck_filter="全部", srs_filter="全部"):
    """使用 JOIN 查詢，獲取單字以及其所屬的卡組名稱"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    base_query = """
        SELECT w.*, d.name as deck_name 
        FROM words w
        JOIN decks d ON w.deck_id = d.id
    """
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
    """根據 ID 更新一個單字"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        now = datetime.datetime.now()
        query = '''UPDATE words SET 
                      word = ?, meaning = ?, deck_id = ?, 
                      example_sentence = ?, word_audio_path = ?,
                      example_audio_path = ?, last_modified_date = ? 
                   WHERE id = ?'''
        
        cursor.execute(query, (
            new_data['word'], new_data['meaning'], new_data['deck_id'],
            new_data['example'], new_data['word_audio'],
            new_data['example_audio'], now, word_id
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
