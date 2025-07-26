import tkinter as tk
from tkinter import messagebox, filedialog, StringVar
import ttkbootstrap as ttk
import database
import audio_manager
import audio_player

class EditWordApp:
    def __init__(self, parent, word_data, refresh_callback):
        self.window = ttk.Toplevel(parent)
        self.window.transient(parent)
        
        self.word_data = word_data
        self.refresh_callback = refresh_callback
        
        self.audio_paths = {
            'word': self.word_data['word_audio_path'] or '',
            'example': self.word_data['example_audio_path'] or ''
        }
        self.original_audio_paths = self.audio_paths.copy()

        self.setup_ui()
        self.toggle_mode(is_edit_mode=False)

    def setup_ui(self):
        self.display_frame = ttk.Frame(self.window, padding=20)
        
        ttk.Label(self.display_frame, text=self.word_data['word'], font=("Arial", 36, "bold"), bootstyle="primary").pack(pady=10)
        ttk.Label(self.display_frame, text=f"卡組: {self.word_data['deck_name']}", font=("Arial", 14), bootstyle="secondary").pack()
        
        ttk.Label(self.display_frame, text=self.word_data['meaning'], font=("Arial", 20), wraplength=500).pack(pady=20)
        ttk.Label(self.display_frame, text=self.word_data['example_sentence'], font=("Arial", 14, "italic"), wraplength=500).pack(pady=10)

        display_audio_frame = ttk.Frame(self.display_frame)
        display_audio_frame.pack(pady=20)
        if self.original_audio_paths['word']:
            ttk.Button(display_audio_frame, text="🔊 單字發音", command=self.play_word_audio, bootstyle="light").pack(side="left", padx=10)
        if self.original_audio_paths['example']:
            ttk.Button(display_audio_frame, text="🔊 例句發音", command=self.play_example_audio, bootstyle="light").pack(side="left", padx=10)

        self.edit_frame = ttk.Frame(self.window, padding=20)
        
        label_font = ("Arial", 14)
        entry_font = ("Arial", 12)

        ttk.Label(self.edit_frame, text="單字 (Word):", font=label_font).grid(row=0, column=0, sticky="w", pady=8)
        self.word_entry = ttk.Entry(self.edit_frame, font=entry_font, width=40)
        self.word_entry.insert(0, self.word_data['word'])
        self.word_entry.grid(row=0, column=1, columnspan=3, pady=8)

        ttk.Label(self.edit_frame, text="意思 (Meaning):", font=label_font).grid(row=1, column=0, sticky="nw", pady=8)
        self.meaning_text = tk.Text(self.edit_frame, font=entry_font, width=40, height=4, wrap=tk.WORD)
        self.meaning_text.insert("1.0", self.word_data['meaning'])
        self.meaning_text.grid(row=1, column=1, columnspan=3, pady=8)

        ttk.Label(self.edit_frame, text="卡組 (Deck):", font=label_font).grid(row=2, column=0, sticky="w", pady=8)
        decks = database.get_all_decks()
        self.deck_names = [deck['name'] for deck in decks]
        self.deck_map = {deck['name']: deck['id'] for deck in decks}
        self.deck_variable = StringVar(value=self.word_data['deck_name'])
        deck_combobox = ttk.Combobox(self.edit_frame, textvariable=self.deck_variable, values=self.deck_names, state="readonly", width=15, font=entry_font)
        deck_combobox.grid(row=2, column=1, sticky="w", pady=8)

        ttk.Label(self.edit_frame, text="例句 (Example):", font=label_font).grid(row=3, column=0, sticky="nw", pady=8)
        self.example_text = tk.Text(self.edit_frame, font=entry_font, width=40, height=5, wrap=tk.WORD)
        self.example_text.insert("1.0", self.word_data['example_sentence'])
        self.example_text.grid(row=3, column=1, columnspan=3, pady=8)

        ttk.Label(self.edit_frame, text="單字聲音:", font=label_font).grid(row=4, column=0, sticky="w", pady=10)
        self.word_audio_entry = ttk.Entry(self.edit_frame, font=("Arial", 10), width=30, state='readonly')
        self.word_audio_entry.insert(0, self.audio_paths['word'])
        self.word_audio_entry.grid(row=4, column=1, pady=10)
        ttk.Button(self.edit_frame, text="瀏覽...", command=lambda: self.select_audio_file(self.word_audio_entry, 'word'), bootstyle="info-outline").grid(row=4, column=2, sticky="w")
        ttk.Button(self.edit_frame, text="清除", command=lambda: self.clear_audio_file(self.word_audio_entry, 'word'), bootstyle="danger-outline").grid(row=4, column=3, sticky="w", padx=5)

        ttk.Label(self.edit_frame, text="例句聲音:", font=label_font).grid(row=5, column=0, sticky="w", pady=5)
        self.example_audio_entry = ttk.Entry(self.edit_frame, font=("Arial", 10), width=30, state='readonly')
        self.example_audio_entry.insert(0, self.audio_paths['example'])
        self.example_audio_entry.grid(row=5, column=1, pady=5)
        ttk.Button(self.edit_frame, text="瀏覽...", command=lambda: self.select_audio_file(self.example_audio_entry, 'example'), bootstyle="info-outline").grid(row=5, column=2, sticky="w")
        ttk.Button(self.edit_frame, text="清除", command=lambda: self.clear_audio_file(self.example_audio_entry, 'example'), bootstyle="danger-outline").grid(row=5, column=3, sticky="w", padx=5)

        ttk.Label(self.edit_frame, text="熟練度 (SRS):", font=label_font).grid(row=6, column=0, sticky="w", pady=8)
        srs_levels = list(range(7))
        self.srs_variable = tk.IntVar(value=self.word_data['srs_level'])
        srs_combobox = ttk.Combobox(self.edit_frame, textvariable=self.srs_variable, values=srs_levels, state="readonly", width=5, font=entry_font)
        srs_combobox.grid(row=6, column=1, sticky="w", pady=8)

        self.button_frame = ttk.Frame(self.window, padding=(0, 10, 20, 20))
        self.button_frame.pack(side="bottom", fill="x")

        self.edit_button = ttk.Button(self.button_frame, text="編輯", command=lambda: self.toggle_mode(True), bootstyle="primary")
        self.update_button = ttk.Button(self.button_frame, text="更新", command=self.update_action, bootstyle="success")
        self.cancel_button = ttk.Button(self.button_frame, text="取消編輯", command=lambda: self.toggle_mode(False), bootstyle="secondary")
        self.delete_button = ttk.Button(self.button_frame, text="刪除", command=self.delete_action, bootstyle="danger")

    def toggle_mode(self, is_edit_mode):
        if is_edit_mode:
            self.display_frame.pack_forget()
            self.edit_frame.pack(expand=True, fill="both", padx=10, pady=10)
            self.edit_button.pack_forget()
            self.cancel_button.pack(side="left", expand=True, padx=5)
            self.update_button.pack(side="left", expand=True, padx=5)
            self.delete_button.pack(side="right", expand=True, padx=5)
            self.window.title(f"編輯單字: {self.word_data['word']}")
        else:
            self.edit_frame.pack_forget()
            self.display_frame.pack(expand=True, fill="both")
            self.cancel_button.pack_forget()
            self.update_button.pack_forget()
            self.delete_button.pack_forget()
            self.edit_button.pack(expand=True, fill="x", padx=20, ipady=5)
            self.window.title(f"檢視單字: {self.word_data['word']}")

    def select_audio_file(self, entry_widget, audio_type):
        source_path = filedialog.askopenfilename(title="選擇聲音檔案", filetypes=(("聲音檔案", "*.mp3 *.wav"), ("所有檔案", "*.*")))
        if source_path:
            self.audio_paths[audio_type] = source_path
            entry_widget.config(state='normal')
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, source_path)
            entry_widget.config(state='readonly')

    def clear_audio_file(self, entry_widget, audio_type):
        self.audio_paths[audio_type] = ""
        entry_widget.config(state='normal')
        entry_widget.delete(0, tk.END)
        entry_widget.config(state='readonly')

    def play_word_audio(self):
        audio_player.play_audio(self.original_audio_paths['word'])

    def play_example_audio(self):
        audio_player.play_audio(self.original_audio_paths['example'])
    
    def update_action(self):
        word_text = self.word_entry.get().strip()
        if not word_text:
            messagebox.showerror("錯誤", "單字不能為空！", parent=self.window)
            return

        if word_text != self.word_data['word']:
            existing_word = database.find_word_by_name(word_text)
            if existing_word:
                messagebox.showerror("更新失敗", 
                                     f"單字 '{word_text}' 已經存在於卡組 '{existing_word['deck_name']}' 中。\n請使用不同的名稱。",
                                     parent=self.window)
                return

        final_word_audio_path = self.original_audio_paths['word']
        if self.audio_paths['word'] != self.original_audio_paths['word']:
            if self.original_audio_paths['word']:
                audio_manager.delete_audio_file(self.original_audio_paths['word'])
            final_word_audio_path = audio_manager.copy_audio_file(self.audio_paths['word'], word_text) if self.audio_paths['word'] else ""

        final_example_audio_path = self.original_audio_paths['example']
        if self.audio_paths['example'] != self.original_audio_paths['example']:
            if self.original_audio_paths['example']:
                audio_manager.delete_audio_file(self.original_audio_paths['example'])
            final_example_audio_path = audio_manager.copy_audio_file(self.audio_paths['example'], word_text) if self.audio_paths['example'] else ""

        selected_deck_name = self.deck_variable.get()
        updated_data = {
            'word': word_text,
            'meaning': self.meaning_text.get("1.0", tk.END).strip(),
            'deck_id': self.deck_map[selected_deck_name],
            'example': self.example_text.get("1.0", tk.END).strip(),
            'word_audio': final_word_audio_path,
            'example_audio': final_example_audio_path,
            'srs_level': self.srs_variable.get()
        }
        error = database.update_word(self.word_data['id'], updated_data)
        if error:
            messagebox.showerror("更新失敗", error, parent=self.window)
        else:
            messagebox.showinfo("成功", "單字已更新！", parent=self.window)
            self.refresh_callback()
            self.window.destroy()

    def delete_action(self):
        if messagebox.askyesno("確認刪除", f"您確定要刪除單字 '{self.word_data['word']}' 嗎？\n這將會一併刪除關聯的聲音檔案，且操作無法復原。", parent=self.window):
            audio_manager.delete_audio_file(self.original_audio_paths['word'])
            audio_manager.delete_audio_file(self.original_audio_paths['example'])
            error = database.delete_word(self.word_data['id'])
            if error:
                messagebox.showerror("刪除失敗", error, parent=self.window)
            else:
                messagebox.showinfo("成功", "單字已刪除！", parent=self.window)
                self.refresh_callback()
                self.window.destroy()

def create(parent, word_data, refresh_callback):
    """建立編輯/檢視視窗的進入點"""
    EditWordApp(parent, word_data, refresh_callback)
