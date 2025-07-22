import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import StringVar, OptionMenu
import database

def create(parent, word_data, refresh_callback):
    """打開「編輯/刪除單字」的視窗"""
    edit_window = tk.Toplevel(parent)
    edit_window.transient(parent)
    edit_window.title(f"編輯單字: {word_data['word']}")
    edit_window.geometry("550x600")

    form_frame = tk.Frame(edit_window, padx=20, pady=20)
    form_frame.pack(expand=True, fill="both")
    
    # --- 文字和等級 (預填資料) ---
    tk.Label(form_frame, text="單字 (Word):", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
    word_entry = tk.Entry(form_frame, font=("Arial", 12), width=40)
    word_entry.insert(0, word_data['word'])
    word_entry.grid(row=0, column=1, columnspan=2, pady=5)

    tk.Label(form_frame, text="意思 (Meaning):", font=("Arial", 12)).grid(row=1, column=0, sticky="nw", pady=5)
    meaning_text = tk.Text(form_frame, font=("Arial", 12), width=40, height=4, wrap=tk.WORD)
    meaning_text.insert("1.0", word_data['meaning'])
    meaning_text.grid(row=1, column=1, columnspan=2, pady=5)

    tk.Label(form_frame, text="等級 (CEFR):", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
    cefr_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    cefr_variable = StringVar(edit_window)
    cefr_variable.set(word_data['cefr_level'])
    cefr_menu = OptionMenu(form_frame, cefr_variable, *cefr_levels)
    cefr_menu.config(width=5)
    cefr_menu.grid(row=2, column=1, sticky="w", pady=5)

    tk.Label(form_frame, text="例句 (Example):", font=("Arial", 12)).grid(row=3, column=0, sticky="nw", pady=5)
    example_text = tk.Text(form_frame, font=("Arial", 12), width=40, height=5, wrap=tk.WORD)
    example_text.insert("1.0", word_data['example_sentence'])
    example_text.grid(row=3, column=1, columnspan=2, pady=5)

    # --- 聲音檔案 (預填資料) ---
    def select_audio_file(entry_widget):
        filepath = filedialog.askopenfilename(title="選擇聲音檔案", filetypes=(("聲音檔案", "*.mp3 *.wav"), ("所有檔案", "*.*")))
        if filepath:
            entry_widget.config(state='normal')
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filepath)
            entry_widget.config(state='readonly')
            
    tk.Label(form_frame, text="單字聲音:", font=("Arial", 12)).grid(row=4, column=0, sticky="w", pady=10)
    word_audio_entry = tk.Entry(form_frame, font=("Arial", 10), width=30, state='readonly')
    
    word_audio_entry.insert(0, word_data['word_audio_path'] or '')
    word_audio_entry.grid(row=4, column=1, pady=10)
    tk.Button(form_frame, text="瀏覽...", command=lambda: select_audio_file(word_audio_entry)).grid(row=4, column=2, sticky="w", padx=5)

    tk.Label(form_frame, text="例句聲音:", font=("Arial", 12)).grid(row=5, column=0, sticky="w", pady=5)
    example_audio_entry = tk.Entry(form_frame, font=("Arial", 10), width=30, state='readonly')
    
    example_audio_entry.insert(0, word_data['example_audio_path'] or '')
    example_audio_entry.grid(row=5, column=1, pady=5)
    tk.Button(form_frame, text="瀏覽...", command=lambda: select_audio_file(example_audio_entry)).grid(row=5, column=2, sticky="w", padx=5)

    # --- 更新與刪除按鈕 ---
    def update_action():
        updated_data = {
            'word': word_entry.get(),
            'meaning': meaning_text.get("1.0", tk.END).strip(),
            'cefr_level': cefr_variable.get(),
            'example': example_text.get("1.0", tk.END).strip(),
            'word_audio': word_audio_entry.get(),
            'example_audio': example_audio_entry.get()
        }
        error = database.update_word(word_data['id'], updated_data)
        if error:
            messagebox.showerror("更新失敗", error, parent=edit_window)
        else:
            messagebox.showinfo("成功", "單字已更新！", parent=edit_window)
            refresh_callback()
            edit_window.destroy()

    def delete_action():
        if messagebox.askyesno("確認刪除", f"你確定要刪除單字 '{word_data['word']}' 嗎？此操作無法復原。", parent=edit_window):
            error = database.delete_word(word_data['id'])
            if error:
                messagebox.showerror("刪除失敗", error, parent=edit_window)
            else:
                messagebox.showinfo("成功", "單字已刪除！", parent=edit_window)
                refresh_callback()
                edit_window.destroy()
    
    
    button_frame = tk.Frame(form_frame)
    button_frame.grid(row=6, column=1, columnspan=2, pady=20, sticky='e')
    
    update_button = tk.Button(button_frame, text="更新", font=("Arial", 12), command=update_action)
    update_button.pack(side='left', padx=10)
    
    delete_button = tk.Button(button_frame, text="刪除", font=("Arial", 12), command=delete_action, bg="#C41E3A", fg="white")
    delete_button.pack(side='left')