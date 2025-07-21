import tkinter as tk
from tkinter import messagebox, OptionMenu, StringVar
import sqlite3
import datetime

# --- 資料庫設定函式 ---
def initialize_database():
    """初始化資料庫，如果 words 表不存在，則建立它"""
    conn = sqlite3.connect('ember_rhythm.db') # 建立或連接到資料庫檔案
    cursor = conn.cursor()
    
    # 建立 words 表，srs_level 預設為0, next_review_date 預設為當前時間
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL UNIQUE,
        meaning TEXT NOT NULL,
        cefr_level TEXT NOT NULL,
        example_sentence TEXT,
        srs_level INTEGER DEFAULT 0,
        next_review_date TIMESTAMP NOT NULL,
        date_added TIMESTAMP NOT NULL
    )
    ''')
    
    conn.commit() # 儲存變更
    conn.close() # 關閉連線


# --- 主應用程式類別 ---
class EmberRhythmApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EmberRhythm")
        self.root.geometry("600x500")

        main_frame = tk.Frame(self.root, padx=20, pady=30)
        main_frame.pack(expand=True)
        
        # ... 原本的按鈕們 ...
        btn_add = tk.Button(main_frame, text="添加單詞", command=self.open_add_word_window, font=("Arial", 14), width=20, height=2)
        btn_add.pack(pady=5)
        # 其他按鈕保持不變...
        btn_decks = tk.Button(main_frame, text="字典分類", command=self.view_decks_placeholder, font=("Arial", 14), width=20, height=2)
        btn_decks.pack(pady=5)
        btn_all_words = tk.Button(main_frame, text="總字典", command=self.view_all_words_placeholder, font=("Arial", 14), width=20, height=2)
        btn_all_words.pack(pady=5)
        btn_exit = tk.Button(main_frame, text="退出程式", command=self.quit_app, font=("Arial", 14), width=20, height=2)
        btn_exit.pack(pady=5)

    # --- 按鈕對應的函式 ---
    
    def open_add_word_window(self):
        """打開「添加單詞」的新視窗"""
        add_window = tk.Toplevel(self.root)
        add_window.title("添加新單詞")
        add_window.geometry("600x500") # 稍微把視窗調大一點以容納Text元件

        form_frame = tk.Frame(add_window, padx=20, pady=20)
        form_frame.pack(expand=True, fill="both")

        # --- 表單元件 ---
        # 1. 單字 Label 和 Entry (這個不變)
        tk.Label(form_frame, text="單字 (Word):", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        word_entry = tk.Entry(form_frame, font=("Arial", 12), width=35) # 稍微加寬
        word_entry.grid(row=0, column=1, pady=5)

        # 2. 意思 Label 和 Text (★★★ 這裡被修改了 ★★★)
        tk.Label(form_frame, text="意思 (Meaning):", font=("Arial", 12)).grid(row=1, column=0, sticky="nw", pady=5) # sticky='nw' 讓標籤跟Text頂部對齊
        # 使用 Text 元件，設定高度為 4 行
        meaning_text = tk.Text(form_frame, font=("Arial", 12), width=35, height=4, wrap=tk.WORD)
        meaning_text.grid(row=1, column=1, pady=5)

        # 3. CEFR 等級 Label 和下拉選單 (這個不變)
        tk.Label(form_frame, text="等級 (CEFR):", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
        cefr_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        cefr_variable = tk.StringVar(add_window)
        cefr_variable.set(cefr_levels[0]) 
        cefr_menu = tk.OptionMenu(form_frame, cefr_variable, *cefr_levels)
        cefr_menu.config(width=5) # 稍微調整下拉選單寬度
        cefr_menu.grid(row=2, column=1, sticky="w", pady=5)

        # 4. 例句 Label 和 Text (★★★ 這裡被修改了 ★★★)
        tk.Label(form_frame, text="例句 (Example):", font=("Arial", 12)).grid(row=3, column=0, sticky="nw", pady=5) # sticky='nw' 讓標籤跟Text頂部對齊
        # 使用 Text 元件，設定高度為 5 行
        example_text = tk.Text(form_frame, font=("Arial", 12), width=35, height=5, wrap=tk.WORD)
        example_text.grid(row=3, column=1, pady=5)
        
        # --- 儲存按鈕 (★★★ 這裡的 .get() 方法也被修改了 ★★★) ---
        save_button = tk.Button(form_frame, text="儲存", font=("Arial", 12), 
                              command=lambda: self.save_word(
                                  add_window,
                                  word_entry.get(), 
                                  # 對 Text 元件使用 .get("1.0", tk.END).strip() 來取得內容
                                  meaning_text.get("1.0", tk.END).strip(),
                                  cefr_variable.get(),
                                  example_text.get("1.0", tk.END).strip()
                              ))
        save_button.grid(row=4, column=1, sticky="e", pady=20)
    
    def save_word(self, window, word, meaning, cefr_level, example):
        """將單字儲存到資料庫"""
        # 簡單的驗證，確保必填欄位不為空
        if not word or not meaning:
            messagebox.showerror("錯誤", "「單字」和「意思」為必填欄位！", parent=window)
            return

        try:
            conn = sqlite3.connect('ember_rhythm.db')
            cursor = conn.cursor()
            
            now = datetime.datetime.now()
            
            # 使用 ? 作為佔位符，可以防止 SQL 注入攻擊，更安全
            cursor.execute('''
            INSERT INTO words (word, meaning, cefr_level, example_sentence, next_review_date, date_added)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (word, meaning, cefr_level, example, now, now))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("成功", f"單字 '{word}' 已成功添加！", parent=window)
            window.destroy() # 儲存成功後關閉視窗

        except sqlite3.IntegrityError:
            # UNIQUE 限制會在這裡觸發錯誤
            messagebox.showerror("錯誤", f"單字 '{word}' 已經存在於資料庫中！", parent=window)
        except Exception as e:
            messagebox.showerror("資料庫錯誤", f"發生錯誤: {e}", parent=window)


    def view_decks_placeholder(self):
        messagebox.showinfo("提示", "「字典分類」功能待開發！")
        
    def view_all_words_placeholder(self):
        messagebox.showinfo("提示", "「總字典」功能待開發！")

    def quit_app(self):
        if messagebox.askokcancel("退出", "你確定要退出程式嗎？"):
            self.root.destroy()

# --- 程式的進入點 ---
if __name__ == "__main__":
    initialize_database() # 在啟動 App 前，先確保資料庫和表已建立
    root = tk.Tk()
    app = EmberRhythmApp(root)
    root.mainloop()