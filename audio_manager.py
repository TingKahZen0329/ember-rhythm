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
    檔名將會是 '單字_時間戳.副檔名'，並確保檔名唯一。
    """
    if not source_path or not os.path.exists(source_path):
        return None

    try:
        # 從原始路徑獲取檔名和副檔名
        base_name = word_text.strip().replace(' ', '_')
        file_extension = os.path.splitext(source_path)[1]
        
        # 產生一個初始的時間戳
        timestamp = int(time.time())
        
        # ★★★ 解決方案：遞迴檢查檔名唯一性 ★★★
        # 1. 先組合出一個候選檔名和路徑
        new_filename = f"{base_name}_{timestamp}{file_extension}"
        destination_path = os.path.join(MEDIA_FOLDER, new_filename)
        
        # 2. 用 while 迴圈檢查路徑是否存在
        while os.path.exists(destination_path):
            # 3. 如果存在，就將時間戳加 1，產生一個新的候選路徑
            print(f"[警告] 檔案名稱衝突: {new_filename}，正在嘗試新名稱...")
            timestamp += 1 
            new_filename = f"{base_name}_{timestamp}{file_extension}"
            destination_path = os.path.join(MEDIA_FOLDER, new_filename)
        
        # 4. 迴圈結束時，destination_path 一定是一個獨一無二的路徑
        
        # 執行複製
        shutil.copy(source_path, destination_path)
        
        # 回傳這個保證唯一的相對路徑
        return destination_path
    except Exception as e:
        print(f"複製檔案時發生錯誤: {e}")
        return None

def delete_audio_file(relative_path):
    """從媒體資料夾中刪除指定的聲音檔案"""
    if not relative_path or not os.path.exists(relative_path):
        return

    try:
        os.remove(relative_path)
        print(f"已刪除檔案: {relative_path}")
    except Exception as e:
        print(f"刪除檔案時發生錯誤: {e}")
