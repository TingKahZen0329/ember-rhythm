import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
import database
import audio_player
import datetime
import config # 匯入新的設定檔

class FlashcardApp:
    def __init__(self, parent, deck_data, on_close_callback):
        self.window = ttk.Toplevel(parent)
        self.window.transient(parent)
        self.window.title(f"{deck_data['name']} - 複習卡片")
        
        self.on_close_callback = on_close_callback
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

        self.deck = database.get_review_words_for_deck(deck_data['id'])
        self.current_card_index = 0
        self.current_card_data = None

        self.setup_ui()
        self.load_next_card()

    def setup_ui(self):
        self.main_frame = ttk.Frame(self.window, padding=20)
        self.main_frame.pack(expand=True, fill="both")
        
        self.word_label = ttk.Label(self.main_frame, text="", font=("Arial", 48, "bold"), anchor="center")
        self.word_label.pack(pady=(30, 50))

        self.details_frame = ttk.Frame(self.main_frame)
        
        self.meaning_label = ttk.Label(self.details_frame, text="", font=("Arial", 20), wraplength=700, justify="center")
        self.meaning_label.pack(pady=10)
        
        self.example_label = ttk.Label(self.details_frame, text="", font=("Arial", 18, "italic"), wraplength=700, justify="center")
        self.example_label.pack(pady=10)

        self.audio_frame = ttk.Frame(self.details_frame)
        self.word_audio_button = ttk.Button(self.audio_frame, text="🔊 單字發音", command=self.play_word_audio, bootstyle="light")
        self.example_audio_button = ttk.Button(self.audio_frame, text="🔊 例句發音", command=self.play_example_audio, bootstyle="light")

        button_frame = ttk.Frame(self.window, padding=20)
        button_frame.pack(side="bottom", fill="x")

        self.show_answer_button = ttk.Button(button_frame, text="顯示答案", command=self.show_answer, bootstyle="primary")
        
        self.forgot_button = ttk.Button(button_frame, text="忘記了 (1分鐘後)", command=self.process_forgot, bootstyle="warning")
        self.remember_button = ttk.Button(button_frame, text="記得了", command=self.process_remember, bootstyle="success")

    def load_next_card(self):
        if self.current_card_index >= len(self.deck):
            messagebox.showinfo("完成！", "您已複習完此卡組所有到期的卡片！", parent=self.window)
            self.close_window()
            return
        
        self.current_card_data = self.deck[self.current_card_index]
        self.hide_answer()

        self.word_label.config(text=self.current_card_data['word'])
        self.meaning_label.config(text=f"{self.current_card_data['meaning']}")
        self.example_label.config(text=f"\"{self.current_card_data['example_sentence'] or ''}\"")

        srs_level = self.current_card_data['srs_level']
        bg_color, fg_color = config.SRS_COLORS.get(srs_level, ("#FFFFFF", "black"))
        
        style = ttk.Style.get_instance()
        style.configure('Toplevel', background=bg_color)
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        
        for widget in [self.word_label, self.meaning_label, self.example_label]:
            widget.config(background=bg_color, foreground=fg_color)

    def show_answer(self):
        self.details_frame.pack(pady=20, expand=True, fill="x")
        
        has_word_audio = self.current_card_data['word_audio_path']
        has_example_audio = self.current_card_data['example_audio_path']

        # 只有在至少存在一個聲音檔時，才顯示聲音按鈕的容器
        if has_word_audio or has_example_audio:
            self.audio_frame.pack(pady=10)
            if has_word_audio:
                self.word_audio_button.pack(side="left", padx=10, expand=True)
            if has_example_audio:
                self.example_audio_button.pack(side="left", padx=10, expand=True)
        
        self.show_answer_button.pack_forget()
        self.forgot_button.pack(side="left", expand=True, fill="x", padx=10, ipady=10)
        self.remember_button.pack(side="right", expand=True, fill="x", padx=10, ipady=10)

    def hide_answer(self):
        self.details_frame.pack_forget()
        # ★★★ 關鍵修正：確保聲音按鈕的容器也被隱藏 ★★★
        self.audio_frame.pack_forget() 
        self.word_audio_button.pack_forget()
        self.example_audio_button.pack_forget()
        self.forgot_button.pack_forget()
        self.remember_button.pack_forget()
        self.show_answer_button.pack(expand=True, fill="x", ipady=10)

    def process_remember(self):
        current_level = self.current_card_data['srs_level']
        new_level = current_level + 1
        
        interval_minutes = config.SRS_INTERVALS.get(new_level, config.SRS_DEFAULT_INTERVAL)
        delta = datetime.timedelta(minutes=interval_minutes)
        next_review = datetime.datetime.now() + delta
        
        database.update_srs_data(self.current_card_data['id'], new_level, next_review)
        self.current_card_index += 1
        self.load_next_card()

    def process_forgot(self):
        new_level = 0
        delta = datetime.timedelta(minutes=1)
        next_review = datetime.datetime.now() + delta
        
        database.update_srs_data(self.current_card_data['id'], new_level, next_review)
        self.deck.append(self.current_card_data)
        self.current_card_index += 1
        self.load_next_card()
        
    def play_word_audio(self):
        audio_player.play_audio(self.current_card_data['word_audio_path'])

    def play_example_audio(self):
        audio_player.play_audio(self.current_card_data['example_audio_path'])

    def close_window(self):
        audio_player.stop_audio()
        self.on_close_callback()
        self.window.destroy()

def create(parent, deck_data, on_close_callback):
    """建立複習卡片應用程式視窗的進入點。"""
    FlashcardApp(parent, deck_data, on_close_callback)
