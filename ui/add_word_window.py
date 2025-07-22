import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import StringVar, OptionMenu
import database

def create(parent):
    # ... (此處程式碼與上一版 open_add_word_window 完全相同) ...
    # ... 只是將函式名改為 create，並修正了呼叫 database.add_word 的方式 ...
    add_window = tk.Toplevel(parent)
    add_window.transient(parent)
    add_window.title("添加新單詞")
    add_window.geometry("550x550")
    form_frame = tk.Frame(add_window, padx=20, pady=20)
    form_frame.pack(expand=True, fill="both")
    tk.Label(form_frame, text="單字 (Word):", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
    word_entry = tk.Entry(form_frame, font=("Arial", 12), width=40)
    word_entry.grid(row=0, column=1, columnspan=2, pady=5)
    tk.Label(form_frame, text="意思 (Meaning):", font=("Arial", 12)).grid(row=1, column=0, sticky="nw", pady=5)
    meaning_text = tk.Text(form_frame, font=("Arial", 12), width=40, height=4, wrap=tk.WORD)
    meaning_text.grid(row=1, column=1, columnspan=2, pady=5)
    tk.Label(form_frame, text="等級 (CEFR):", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
    cefr_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    cefr_variable = StringVar(add_window)
    cefr_variable.set(cefr_levels[0]) 
    cefr_menu = OptionMenu(form_frame, cefr_variable, *cefr_levels)
    cefr_menu.config(width=5)
    cefr_menu.grid(row=2, column=1, sticky="w", pady=5)
    tk.Label(form_frame, text="例句 (Example):", font=("Arial", 12)).grid(row=3, column=0, sticky="nw", pady=5)
    example_text = tk.Text(form_frame, font=("Arial", 12), width=40, height=5, wrap=tk.WORD)
    example_text.grid(row=3, column=1, columnspan=2, pady=5)
    def select_audio_file(entry_widget):
        filepath = filedialog.askopenfilename(title="選擇聲音檔案", filetypes=(("聲音檔案", "*.mp3 *.wav"), ("所有檔案", "*.*")))
        if filepath:
            entry_widget.config(state='normal')
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filepath)
            entry_widget.config(state='readonly')
    tk.Label(form_frame, text="單字聲音:", font=("Arial", 12)).grid(row=4, column=0, sticky="w", pady=10)
    word_audio_entry = tk.Entry(form_frame, font=("Arial", 10), width=30, state='readonly')
    word_audio_entry.grid(row=4, column=1, pady=10)
    tk.Button(form_frame, text="瀏覽...", command=lambda: select_audio_file(word_audio_entry)).grid(row=4, column=2, sticky="w", padx=5)
    tk.Label(form_frame, text="例句聲音:", font=("Arial", 12)).grid(row=5, column=0, sticky="w", pady=5)
    example_audio_entry = tk.Entry(form_frame, font=("Arial", 10), width=30, state='readonly')
    example_audio_entry.grid(row=5, column=1, pady=5)
    tk.Button(form_frame, text="瀏覽...", command=lambda: select_audio_file(example_audio_entry)).grid(row=5, column=2, sticky="w", padx=5)
    def save_word_action():
        word_data = {
            'word': word_entry.get(),
            'meaning': meaning_text.get("1.0", tk.END).strip(),
            'cefr_level': cefr_variable.get(),
            'example': example_text.get("1.0", tk.END).strip(),
            'word_audio': word_audio_entry.get(),
            'example_audio': example_audio_entry.get()
        }
        if not word_data['word'] or not word_data['meaning']:
            messagebox.showerror("錯誤", "「單字」和「意思」為必填欄位！", parent=add_window)
            return
        error = database.add_word(word_data)
        if error:
            messagebox.showerror("錯誤", error, parent=add_window)
        else:
            messagebox.showinfo("成功", f"單字 '{word_data['word']}' 已成功添加！", parent=add_window)
            add_window.destroy()
    save_button = tk.Button(form_frame, text="儲存", font=("Arial", 12), command=save_word_action)
    save_button.grid(row=6, column=1, columnspan=2, sticky="e", pady=20)