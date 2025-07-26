import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import database
from . import edit_word_window
import config

def create(parent):
    all_words_window = ttk.Toplevel(parent)
    all_words_window.transient(parent)
    all_words_window.title("字典")
    all_words_window.geometry("2000x800")

    style = ttk.Style()
    style.configure("TLabel", font=("Arial", 12))
    style.configure("TButton", font=("Arial", 12))
    style.configure("TCombobox", font=("Arial", 12))
    style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
    style.configure("Treeview", rowheight=30, font=("Arial", 12))

    filter_frame = ttk.Frame(all_words_window, padding="10")
    filter_frame.pack(fill=X, padx=10, pady=5)
    
    ttk.Label(filter_frame, text="搜索單字:").pack(side=LEFT, padx=(0, 5))
    search_entry = ttk.Entry(filter_frame, width=30, font=("Arial", 12))
    search_entry.pack(side=LEFT, padx=5)

    # --- 卡組篩選 (原等級篩選) ---
    ttk.Label(filter_frame, text="卡組:").pack(side=LEFT, padx=(10, 5))
    decks = database.get_all_decks()
    deck_names = ["全部"] + [deck['name'] for deck in decks]
    deck_filter_var = tk.StringVar(value=deck_names[0])
    deck_combobox = ttk.Combobox(filter_frame, textvariable=deck_filter_var, values=deck_names, state="readonly", width=15)
    deck_combobox.pack(side=LEFT, padx=5)

    ttk.Label(filter_frame, text="熟練度:").pack(side=LEFT, padx=(10, 5))
    srs_levels = ["全部"] + list(range(7))
    srs_filter_var = tk.StringVar(value=srs_levels[0])
    srs_combobox = ttk.Combobox(filter_frame, textvariable=srs_filter_var, values=srs_levels, state="readonly", width=10)
    srs_combobox.pack(side=LEFT, padx=5)

    tree_frame = ttk.Frame(all_words_window, padding="10")
    tree_frame.pack(expand=YES, fill=BOTH)

    columns = ('id', 'word', 'meaning', 'deck_name', 'srs_level', 'date_added', 'last_modified')
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings', bootstyle="primary")

    headings = [('id', 'ID', 50), ('word', '單字', 180), ('meaning', '意思', 300), 
                ('deck_name', '卡組', 100), ('srs_level', '熟練度', 80), 
                ('date_added', '建立日期', 180), ('last_modified', '最後修改', 180)]
    
    for col, text, width in headings:
        tree.heading(col, text=text)
        tree.column(col, width=width, anchor=CENTER if col in ['id', 'deck_name', 'srs_level'] else W)

    for level, (bg, fg) in config.SRS_COLORS.items():
        tree.tag_configure(f"srs_{level}", background=bg, foreground=fg)

    def populate_tree():
        for i in tree.get_children():
            tree.delete(i)
        
        all_words = database.get_all_words(
            search_term=search_entry.get(),
            deck_filter=deck_filter_var.get(),
            srs_filter=srs_filter_var.get()
        )
        
        for word in all_words:
            srs_level = word['srs_level']
            tag_name = f"srs_{srs_level}"
            date_added = word['date_added'].split('.')[0] if word['date_added'] else ''
            last_modified = word['last_modified_date'].split('.')[0] if word['last_modified_date'] else ''
            
            tree.insert('', END, values=(
                word['id'], word['word'], word['meaning'],
                word['deck_name'], srs_level, date_added, last_modified
            ), tags=(tag_name,))

    def on_item_double_click(event):
        if not tree.selection(): return
        item_id_str = tree.selection()[0]
        item_values = tree.item(item_id_str, 'values')
        if not item_values: return
        word_id_to_edit = item_values[0]
        
        # 獲取的是完整的 word 物件，包含 deck_name
        all_words_data = database.get_all_words()
        word_data = next((word for word in all_words_data if word['id'] == int(word_id_to_edit)), None)
        if word_data:
            edit_word_window.create(all_words_window, word_data, populate_tree)

    tree.bind("<Double-1>", on_item_double_click)
    
    search_button = ttk.Button(filter_frame, text="篩選", command=populate_tree, bootstyle="info")
    search_button.pack(side=LEFT, padx=(10, 0))

    scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side=LEFT, expand=YES, fill=BOTH)
    scrollbar.pack(side=RIGHT, fill=Y)

    populate_tree()
