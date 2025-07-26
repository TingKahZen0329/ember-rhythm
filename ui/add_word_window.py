import tkinter as tk
from tkinter import messagebox, filedialog, StringVar
import ttkbootstrap as ttk
import database
import audio_manager

def create(parent):
    """建立並顯示「添加新單詞」的視窗 (最終修正版)"""
    add_window = ttk.Toplevel(parent)
    add_window.transient(parent)
    add_window.title("添加新單詞")
    add_window.geometry("700x700")

    form_frame = ttk.Frame(add_window, padding=20)
    form_frame.pack(expand=True, fill="both")
    
    label_font = ("Arial", 14)
    entry_font = ("Arial", 12)

    # 用於暫存使用者選擇的原始檔案路徑
    audio_source_paths = {'word': '', 'example': ''}

    # --- 文字和卡組元件 ---
    ttk.Label(form_frame, text="單字 (Word):", font=label_font).grid(row=0, column=0, sticky="w", pady=8)
    word_entry = ttk.Entry(form_frame, font=entry_font, width=50)
    word_entry.grid(row=0, column=1, columnspan=3, pady=8)
    # ... (其他元件與之前相同) ...
    ttk.Label(form_frame, text="意思 (Meaning):", font=label_font).grid(row=1, column=0, sticky="nw", pady=8)
    meaning_text = tk.Text(form_frame, font=entry_font, width=50, height=5, wrap=tk.WORD)
    meaning_text.grid(row=1, column=1, columnspan=3, pady=8)
    ttk.Label(form_frame, text="卡組 (Deck):", font=label_font).grid(row=2, column=0, sticky="w", pady=8)
    decks = database.get_all_decks()
    deck_names = [deck['name'] for deck in decks]
    deck_map = {deck['name']: deck['id'] for deck in decks}
    deck_variable = StringVar(value=deck_names[0] if deck_names else "")
    deck_combobox = ttk.Combobox(form_frame, textvariable=deck_variable, values=deck_names, state="readonly", width=15, font=entry_font)
    deck_combobox.grid(row=2, column=1, sticky="w", pady=8)
    ttk.Label(form_frame, text="例句 (Example):", font=label_font).grid(row=3, column=0, sticky="nw", pady=8)
    example_text = tk.Text(form_frame, font=entry_font, width=50, height=6, wrap=tk.WORD)
    example_text.grid(row=3, column=1, columnspan=3, pady=8)

    # --- 聲音檔案輔助函式 (新邏輯) ---
    def select_audio_file(entry_widget, audio_type):
        source_path = filedialog.askopenfilename(title="選擇聲音檔案", filetypes=(("聲音檔案", "*.mp3 *.wav"), ("所有檔案", "*.*")))
        if source_path:
            audio_source_paths[audio_type] = source_path
            entry_widget.config(state='normal')
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, source_path) # 顯示原始路徑
            entry_widget.config(state='readonly')

    def clear_audio_file(entry_widget, audio_type):
        audio_source_paths[audio_type] = ""
        entry_widget.config(state='normal')
        entry_widget.delete(0, tk.END)
        entry_widget.config(state='readonly')

    # --- 聲音檔案介面 ---
    ttk.Label(form_frame, text="單字聲音:", font=label_font).grid(row=4, column=0, sticky="w", pady=10)
    word_audio_entry = ttk.Entry(form_frame, font=("Arial", 10), width=40, state='readonly')
    word_audio_entry.grid(row=4, column=1, pady=10)
    ttk.Button(form_frame, text="瀏覽...", command=lambda: select_audio_file(word_audio_entry, 'word'), bootstyle="info-outline").grid(row=4, column=2, sticky="w")
    ttk.Button(form_frame, text="清除", command=lambda: clear_audio_file(word_audio_entry, 'word'), bootstyle="danger-outline").grid(row=4, column=3, sticky="w", padx=5)

    ttk.Label(form_frame, text="例句聲音:", font=label_font).grid(row=5, column=0, sticky="w", pady=5)
    example_audio_entry = ttk.Entry(form_frame, font=("Arial", 10), width=40, state='readonly')
    example_audio_entry.grid(row=5, column=1, pady=5)
    ttk.Button(form_frame, text="瀏覽...", command=lambda: select_audio_file(example_audio_entry, 'example'), bootstyle="info-outline").grid(row=5, column=2, sticky="w")
    ttk.Button(form_frame, text="清除", command=lambda: clear_audio_file(example_audio_entry, 'example'), bootstyle="danger-outline").grid(row=5, column=3, sticky="w", padx=5)

    # --- 儲存按鈕邏輯 (新邏輯) ---
    def save_word_action():
        word_text = word_entry.get().strip()
        if not word_text or not meaning_text.get("1.0", tk.END).strip():
            messagebox.showerror("錯誤", "「單字」和「意思」為必填欄位！", parent=add_window)
            return
        
        selected_deck_name = deck_variable.get()
        if not selected_deck_name:
            messagebox.showerror("錯誤", "沒有可用的卡組。請先在『卡組分類』中建立一個卡組！", parent=add_window)
            return

        # ★★★ 只有在儲存時才執行檔案複製 ★★★
        word_audio_path = audio_manager.copy_audio_file(audio_source_paths['word'], word_text) if audio_source_paths['word'] else ""
        example_audio_path = audio_manager.copy_audio_file(audio_source_paths['example'], word_text) if audio_source_paths['example'] else ""

        word_data = {
            'word': word_text,
            'meaning': meaning_text.get("1.0", tk.END).strip(),
            'deck_id': deck_map[selected_deck_name],
            'example': example_text.get("1.0", tk.END).strip(),
            'word_audio': word_audio_path,
            'example_audio': example_audio_path
        }
            
        error = database.add_word(word_data)
        
        if error:
            messagebox.showerror("錯誤", error, parent=add_window)
        else:
            messagebox.showinfo("成功", f"單字 '{word_data['word']}' 已成功添加！", parent=add_window)
            add_window.destroy()

    save_button = ttk.Button(form_frame, text="儲存", command=save_word_action, bootstyle="success")
    save_button.grid(row=6, column=1, columnspan=3, sticky="e", pady=20)
