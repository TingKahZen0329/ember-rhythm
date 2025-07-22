import tkinter as tk
from app import EmberRhythmApp # 從 app.py 匯入主應用程式
import database # 從 database.py 匯入資料庫函式

# --- 程式的進入點 ---
if __name__ == "__main__":
    database.initialize() # 確保資料庫已準備就緒
    
    root = tk.Tk()
    app = EmberRhythmApp(root)
    root.mainloop()