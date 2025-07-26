import sqlite3
import zipfile
import os
import shutil
import tempfile
import time
import datetime # 匯入 datetime
import database
import audio_manager

def export_decks(target_zip_path, reset_srs=False):
    """
    將整個資料庫和媒體資料夾打包成一個 .erf 檔案 (zip)
    可選擇是否在匯出前將熟練度歸零。
    """
    db_to_export = database.DB_NAME
    temp_dir = None
    
    try:
        if reset_srs:
            # ★★★ 關鍵修正：建立臨時資料庫並重設熟練度 ★★★
            temp_dir = tempfile.TemporaryDirectory()
            temp_db_path = os.path.join(temp_dir.name, "temp_export.db")
            shutil.copy(database.DB_NAME, temp_db_path)
            
            conn_temp = sqlite3.connect(temp_db_path)
            cursor_temp = conn_temp.cursor()
            now = datetime.datetime.now()
            cursor_temp.execute("UPDATE words SET srs_level = 0, next_review_date = ?", (now,))
            conn_temp.commit()
            conn_temp.close()
            
            db_to_export = temp_db_path # 將要打包的資料庫指向這個臨時副本

        with zipfile.ZipFile(target_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.exists(db_to_export):
                # 在 zip 檔中，名字依然是標準的 ember_rhythm.db
                zipf.write(db_to_export, arcname=os.path.basename(database.DB_NAME))

            media_folder = "user_media"
            if os.path.exists(media_folder):
                for root, _, files in os.walk(media_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=os.path.dirname(media_folder))
                        zipf.write(file_path, arcname=arcname)
        return None
    except Exception as e:
        return f"匯出時發生錯誤: {e}"
    finally:
        # 確保臨時資料夾被清理
        if temp_dir:
            temp_dir.cleanup()

def import_decks(source_zip_path, progress_queue):
    """從 .erf 檔案匯入並合併資料 (最終穩定版)"""
    conn_local = None
    conn_imported = None
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            progress_queue.put(('update', 1, 5, "正在解壓縮檔案..."))
            with zipfile.ZipFile(source_zip_path, 'r') as zipf:
                zipf.extractall(temp_dir)

            imported_db_path = os.path.join(temp_dir, database.DB_NAME)
            imported_media_folder = os.path.join(temp_dir, "user_media")
            if not os.path.exists(imported_db_path):
                raise ValueError("錯誤：匯入的檔案中找不到資料庫。")

            progress_queue.put(('update', 2, 5, "讀取匯入資料..."))
            conn_imported = sqlite3.connect(imported_db_path)
            conn_imported.row_factory = sqlite3.Row
            cursor_imported = conn_imported.cursor()
            cursor_imported.execute("SELECT * FROM decks")
            imported_decks = cursor_imported.fetchall()
            cursor_imported.execute("SELECT * FROM words")
            imported_words = cursor_imported.fetchall()
            conn_imported.close()
            conn_imported = None

            conn_local = sqlite3.connect(database.DB_NAME)
            cursor_local = conn_local.cursor()
            cursor_local.execute("SELECT name FROM decks")
            local_deck_names = {row[0] for row in cursor_local.fetchall()}
            
            progress_queue.put(('update', 3, 5, f"正在準備 {len(imported_decks)} 個卡組..."))
            new_decks_to_insert = []
            deck_id_map = {}
            for deck in imported_decks:
                original_name = deck['name']
                new_name = original_name
                count = 1
                while new_name in local_deck_names:
                    new_name = f"{original_name}({count})"
                    count += 1
                new_decks_to_insert.append((new_name,))
                deck_id_map[deck['id']] = new_name
                local_deck_names.add(new_name)
            
            progress_queue.put(('update', 4, 5, f"正在準備 {len(imported_words)} 個單字..."))
            new_words_to_insert = []
            for word in imported_words:
                word_text_to_insert = word['word']
                new_deck_id_name = deck_id_map.get(word['deck_id'])
                if not new_deck_id_name: continue
                
                new_word_audio_path = None
                if word['word_audio_path']:
                    source_audio_path = os.path.join(temp_dir, word['word_audio_path'])
                    if os.path.exists(source_audio_path):
                        new_word_audio_path = audio_manager.copy_audio_file(source_audio_path, word_text_to_insert)
                
                new_example_audio_path = None
                if word['example_audio_path']:
                    source_audio_path = os.path.join(temp_dir, word['example_audio_path'])
                    if os.path.exists(source_audio_path):
                        new_example_audio_path = audio_manager.copy_audio_file(source_audio_path, word_text_to_insert)

                new_words_to_insert.append((
                    word_text_to_insert, word['meaning'], new_deck_id_name, word['example_sentence'],
                    new_word_audio_path, new_example_audio_path, word['srs_level'],
                    word['next_review_date'], word['date_added'], word['last_modified_date']
                ))

            progress_queue.put(('update', 5, 5, "正在寫入資料庫..."))
            if new_decks_to_insert:
                cursor_local.executemany("INSERT INTO decks (name) VALUES (?)", new_decks_to_insert)
            
            cursor_local.execute("SELECT id, name FROM decks")
            all_local_decks_map = {name: id for id, name in cursor_local.fetchall()}
            
            final_words_to_insert = []
            for word_tuple in new_words_to_insert:
                deck_name = word_tuple[2]
                deck_id = all_local_decks_map.get(deck_name)
                if deck_id:
                    final_words_to_insert.append(word_tuple[:2] + (deck_id,) + word_tuple[3:])

            if final_words_to_insert:
                cursor_local.executemany('''
                    INSERT INTO words (word, meaning, deck_id, example_sentence, word_audio_path, example_audio_path, srs_level, next_review_date, date_added, last_modified_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', final_words_to_insert)

            conn_local.commit()
            result_message = f"成功匯入 {len(new_decks_to_insert)} 個卡組和 {len(final_words_to_insert)} 個單字！"
            progress_queue.put(('done', result_message))

    except Exception as e:
        progress_queue.put(('error', f"匯入時發生錯誤: {e}"))
    finally:
        if conn_local:
            conn_local.close()
        if conn_imported:
            conn_imported.close()
