import tkinter as tk
from tkinter import messagebox
from ui import add_word_window, all_words_window # 從 ui 資料夾匯入

class EmberRhythmApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EmberRhythm")
        self.root.geometry("600x500")

        main_frame = tk.Frame(self.root, padx=20, pady=30)
        main_frame.pack(expand=True)
        
        btn_add = tk.Button(main_frame, text="添加單詞", command=self.open_add_window, font=("Arial", 14), width=20, height=2)
        btn_add.pack(pady=5)
        
        btn_all_words = tk.Button(main_frame, text="總字典", command=self.open_list_window, font=("Arial", 14), width=20, height=2)
        btn_all_words.pack(pady=5)

        btn_decks = tk.Button(main_frame, text="字典分類", command=self.view_decks_placeholder, font=("Arial", 14), width=20, height=2)
        btn_decks.pack(pady=5)
        
        btn_exit = tk.Button(main_frame, text="退出程式", command=self.quit_app, font=("Arial", 14), width=20, height=2)
        btn_exit.pack(pady=5)

    def open_add_window(self):
        add_word_window.create(self.root)

    def open_list_window(self):
        all_words_window.create(self.root)

    def view_decks_placeholder(self):
        messagebox.showinfo("提示", "「字典分類」功能待開發！")

    def quit_app(self):
        if messagebox.askokcancel("退出", "你確定要退出程式嗎？"):
            self.root.destroy()