import tkinter as tk
# 匯入 ttkbootstrap 並給它 ttk 的小名，這樣我們就可以無縫替換
import ttkbootstrap as ttk 
from app import EmberRhythmApp
import database
import audio_manager
import audio_player

# --- 程式的進入點 ---
if __name__ == "__main__":
    database.initialize()
    audio_manager.setup_media_folder()
    audio_player.initialize_player()
    
    # 使用 ttkbootstrap 的 Window，並選擇一個主題
    # 其他可選主題: "litera", "flatly", "journal", "darkly", "superhero", "cyborg"
    root = ttk.Window(themename="superhero") 
    
    app = EmberRhythmApp(root)
    root.mainloop()
