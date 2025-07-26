import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ui import add_word_window, all_words_window, deck_selection_window

class EmberRhythmApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EmberRhythm")
        self.root.geometry("600x650")

        main_frame = ttk.Frame(self.root, padding=(40, 20))
        main_frame.pack(expand=True, fill="both")
        
        ttk.Label(main_frame, text="EmberRhythm", font=("Arial", 32, "bold"), bootstyle="primary").pack(pady=(0, 20))

        intro_text = (
            "您好，此應用軟體是參考艾賓浩斯遺忘曲線，\n"
            "並結合閃卡記憶法而創建的一個小工具。\n"
            "希望透過科學的複習節奏，幫助您更有效地學習與記憶。\n"
            "祝您學習愉快！"
        )
        # ★★★ 修正 1：新增 wraplength 來控制文字寬度，確保完美換行 ★★★
        ttk.Label(
            main_frame, 
            text=intro_text, 
            font=("Arial", 12), 
            justify=tk.CENTER, 
            bootstyle="secondary",
            wraplength=500  # 設定文字寬度上限為 500 像素
        ).pack(pady=(0, 30))

        btn_add = ttk.Button(main_frame, text="添加單詞", command=self.open_add_window, bootstyle="success-outline", padding=(20, 15))
        btn_add.pack(pady=10, fill='x')
        
        btn_all_words = ttk.Button(main_frame, text="字典", command=self.open_list_window, bootstyle="info-outline", padding=(20, 15))
        btn_all_words.pack(pady=10, fill='x')

        btn_decks = ttk.Button(main_frame, text="卡組分類", command=self.open_deck_window, bootstyle="warning-outline", padding=(20, 15))
        btn_decks.pack(pady=10, fill='x')
        
        btn_exit = ttk.Button(main_frame, text="退出程式", command=self.quit_app, bootstyle="secondary", padding=(20, 15))
        btn_exit.pack(pady=10, fill='x')

    def open_add_window(self):
        add_word_window.create(self.root)

    def open_list_window(self):
        all_words_window.create(self.root)

    def open_deck_window(self):
        deck_selection_window.create(self.root)

    def quit_app(self):
        if messagebox.askokcancel("退出", "您確定要退出程式嗎？"):
            self.root.destroy()
