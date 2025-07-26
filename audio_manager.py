import os
import shutil
import time

MEDIA_FOLDER = "user_media"

def setup_media_folder():
    """如果媒體資料夾不存在，則建立它"""
    if not os.path.exists(MEDIA_FOLDER):
        os.makedirs(MEDIA_FOLDER)

def copy_audio_file(source_path, word_text):
    """
    複製聲音檔案到媒體資料夾，並回傳新的相對路徑。
    檔名將會是 '單字_時間戳.副檔名'
    """
    if not source_path or not os.path.exists(source_path):
        return None

    try:
        # 從原始路徑獲取副檔名 (例如 .mp3)
        file_extension = os.path.splitext(source_path)[1]
        
        # 產生一個獨一無二的時間戳
        timestamp = int(time.time())
        
        # 建立新的、安全的檔名
        new_filename = f"{word_text.strip().replace(' ', '_')}_{timestamp}{file_extension}"
        
        # 組合出完整的目標路徑
        destination_path = os.path.join(MEDIA_FOLDER, new_filename)
        
        # 執行複製
        shutil.copy(source_path, destination_path)
        
        # 回傳相對路徑，供資料庫儲存
        return destination_path
    except Exception as e:
        print(f"複製檔案時發生錯誤: {e}")
        return None

def delete_audio_file(relative_path):
    """從媒體資料夾中刪除指定的聲音檔案"""
    if not relative_path or not os.path.exists(relative_path):
        return # 如果路徑為空或檔案不存在，直接返回

    try:
        os.remove(relative_path)
        print(f"已刪除檔案: {relative_path}")
    except Exception as e:
        print(f"刪除檔案時發生錯誤: {e}")