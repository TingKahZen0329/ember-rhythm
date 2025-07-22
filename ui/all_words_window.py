import tkinter as tk
from tkinter import ttk
import database
from . import edit_word_window # 從同一個資料夾匯入 edit_word_window

def create(parent):
    all_words_window = tk.Toplevel(parent)
    all_words_window.transient(parent)
    all_words_window.title("總字典")
    all_words_window.geometry("1000x700")
    # ... (此處程式碼與上一版 open_all_words_window 基本相同) ...
    # ... 只是將 on_item_double_click 中呼叫的函式改為 edit_word_window.create ...
    search_frame = ttk.Frame(all_words_window, padding="10")
    search_frame.pack(fill='x')
    ttk.Label(search_frame, text="搜索單字:").pack(side='left', padx=(0, 5))
    search_entry = ttk.Entry(search_frame, width=40)
    search_entry.pack(side='left', expand=True, fill='x')
    tree_frame = ttk.Frame(all_words_window, padding="10")
    tree_frame.pack(expand=True, fill='both')
    columns = ('id', 'word', 'meaning', 'cefr_level', 'date_added', 'last_modified')
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
    tree.heading('id', text='ID')
    tree.heading('word', text='單字')
    tree.heading('meaning', text='意思')
    tree.heading('cefr_level', text='等級')
    tree.heading('date_added', text='建立日期')
    tree.heading('last_modified', text='最後修改')
    tree.column('id', width=50, anchor='center')
    tree.column('word', width=150)
    tree.column('meaning', width=250)
    tree.column('cefr_level', width=80, anchor='center')
    tree.column('date_added', width=150)
    tree.column('last_modified', width=150)
    def populate_tree(search_term=""):
        for i in tree.get_children():
            tree.delete(i)
        all_words = database.get_all_words(search_term)
        for word in all_words:
            date_added = word['date_added'].split('.')[0] if word['date_added'] else ''
            last_modified = word['last_modified_date'].split('.')[0] if word['last_modified_date'] else ''
            tree.insert('', tk.END, values=(word['id'], word['word'], word['meaning'], word['cefr_level'], date_added, last_modified))
    def on_item_double_click(event):
        if not tree.selection(): return
        item_id_str = tree.selection()[0]
        item_values = tree.item(item_id_str, 'values')
        if not item_values: return
        word_id_to_edit = item_values[0]
        all_words_data = database.get_all_words()
        word_data = next((word for word in all_words_data if word['id'] == int(word_id_to_edit)), None)
        if word_data:
            # 呼叫新的 edit_word_window 模組裡的 create 函式
            edit_word_window.create(all_words_window, word_data, lambda: populate_tree(search_entry.get()))
    tree.bind("<Double-1>", on_item_double_click)
    search_button = ttk.Button(search_frame, text="搜索", command=lambda: populate_tree(search_entry.get()))
    search_button.pack(side='left', padx=(5, 0))
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.grid(row=0, column=0, sticky='nsew')
    scrollbar.grid(row=0, column=1, sticky='ns')
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)
    populate_tree()