import tkinter as tk
from tkinter import messagebox

# --- 主應用程式類別 ---
class EmberRhythmApp:
    def __init__(self, root):
        self.root = root
        self.root.title("我的 EmberRhythm 應用程式")
        self.root.geometry("600x500") # 設定視窗大小

        # --- 建立主畫面的框架 ---
        main_frame = tk.Frame(self.root, padx=20, pady=30)
        main_frame.pack(expand=True)

        # --- 建立並放置按鈕 ---
        # command=self.add_word_placeholder 代表點擊按鈕時，要執行 self.add_word_placeholder 這個函式
        # 我們先用 placeholder (佔位符) 函式來代表未來要實現的功能
        
        # 添加單詞按鈕
        btn_add = tk.Button(main_frame, text="添加單詞", command=self.add_word_placeholder, font=("Arial", 14), width=20, height=2)
        btn_add.pack(pady=5) # pady=5 讓按鈕之間有點垂直距離

        # 字典分類按鈕
        btn_decks = tk.Button(main_frame, text="字典分類", command=self.view_decks_placeholder, font=("Arial", 14), width=20, height=2)
        btn_decks.pack(pady=5)

        # 總字典按鈕
        btn_all_words = tk.Button(main_frame, text="總字典", command=self.view_all_words_placeholder, font=("Arial", 14), width=20, height=2)
        btn_all_words.pack(pady=5)
        
        # 退出程式按鈕
        # command=self.root.quit 是 tkinter 內建的關閉視窗指令
        btn_exit = tk.Button(main_frame, text="退出程式", command=self.quit_app, font=("Arial", 14), width=20, height=2)
        btn_exit.pack(pady=5)

    # --- 按鈕對應的函式 ---
    
    def add_word_placeholder(self):
        # 彈出一個提示視窗，告訴我們這個功能還沒做
        messagebox.showinfo("提示", "「添加單詞」功能待開發！")

    def view_decks_placeholder(self):
        messagebox.showinfo("提示", "「字典分類」功能待開發！")
        
    def view_all_words_placeholder(self):
        messagebox.showinfo("提示", "「總字典」功能待開發！")

    def quit_app(self):
        # 彈出確認對話框
        if messagebox.askokcancel("退出", "你確定要退出程式嗎？"):
            self.root.destroy() # destroy 會徹底關閉視窗

# --- 程式的進入點 ---
if __name__ == "__main__":
    # 建立主視窗
    root = tk.Tk()
    # 建立應用程式實例
    app = EmberRhythmApp(root)
    # 啟動 tkinter 的事件迴圈，這樣視窗才能顯示和互動
    root.mainloop()