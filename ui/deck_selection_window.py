import tkinter as tk
from tkinter import simpledialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from . import flashcard_window
import database

class DeckSelectionApp:
    def __init__(self, parent):
        self.parent = parent
        self.window = ttk.Toplevel(parent)
        self.window.transient(parent)
        self.window.title("選擇卡組分類")
        self.window.geometry("450x600")

        self.setup_ui()
        self.refresh_decks() # 第一次載入時刷新

    def setup_ui(self):
        top_frame = ttk.Frame(self.window, padding=(20, 20, 20, 10))
        top_frame.pack(fill="x")
        ttk.Label(top_frame, text="請選擇要複習的卡組", font=("Arial", 18, "bold"), bootstyle="primary").pack()

        self.scroll_frame = ScrolledFrame(self.window, autohide=True)
        self.scroll_frame.pack(expand=True, fill="both", padx=20, pady=10)
        
        bottom_frame = ttk.Frame(self.window, padding=(20, 10, 20, 20))
        bottom_frame.pack(fill="x")

        add_btn = ttk.Button(bottom_frame, text="添加卡組", command=self.add_new_deck, bootstyle="success")
        add_btn.pack(side="left", expand=True, padx=5)
        
        manage_btn = ttk.Button(bottom_frame, text="管理卡組", command=self.manage_decks, bootstyle="secondary")
        manage_btn.pack(side="left", expand=True, padx=5)

    def refresh_decks(self):
        """
        刷新卡組列表。
        這個函式現在只會在需要的時候被明確呼叫。
        """
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.decks = database.get_all_decks()
        for deck in self.decks:
            due_cards = database.get_review_words_for_deck(deck['id'])
            button_text = f"{deck['name']} ({len(due_cards)} 個待複習)"
            
            btn = ttk.Button(self.scroll_frame, text=button_text, 
                             command=lambda d=deck: self.start_review(d), 
                             bootstyle="info", padding=15)
            btn.pack(pady=5, fill='x', padx=10)

    def add_new_deck(self):
        new_name = simpledialog.askstring("添加新卡組", "請輸入新卡組的名稱:", parent=self.window)
        if new_name and new_name.strip():
            error = database.add_deck(new_name.strip())
            if error:
                messagebox.showerror("錯誤", error, parent=self.window)
            else:
                self.refresh_decks()

    def manage_decks(self):
        """
        管理卡組，提供重新命名與刪除功能。
        """
        self.decks = database.get_all_decks()
        deck_names = [d['name'] for d in self.decks]
        if not deck_names:
            messagebox.showinfo("提示", "沒有可管理的卡組。", parent=self.window)
            return
        
        selected_deck_name = simpledialog.askstring("管理卡組", 
                                                    f"請輸入您想管理的卡組名稱:\n\n({', '.join(deck_names)})", 
                                                    parent=self.window)
        
        if selected_deck_name and selected_deck_name in deck_names:
            deck_to_manage = next(d for d in self.decks if d['name'] == selected_deck_name)
            
            action = simpledialog.askstring("選擇操作", 
                                            f"您想對卡組 '{selected_deck_name}' 做什麼？\n\n- 輸入新名稱來「重新命名」\n- 輸入大寫的 'DELETE' 來「刪除」", 
                                            parent=self.window)
            
            if action:
                action = action.strip()
                if action.upper() == 'DELETE':
                    if messagebox.askyesno("確認刪除", 
                                           f"您確定要刪除卡組 '{selected_deck_name}' 嗎？\n\n注意：只有空的卡組才能被刪除。", 
                                           parent=self.window):
                        error = database.delete_deck(deck_to_manage['id'])
                        if error:
                            messagebox.showerror("刪除失敗", error, parent=self.window)
                        else:
                            messagebox.showinfo("成功", f"卡組 '{selected_deck_name}' 已被刪除。", parent=self.window)
                            self.refresh_decks()
                elif action:
                    new_name = action
                    error = database.update_deck_name(deck_to_manage['id'], new_name)
                    if error:
                        messagebox.showerror("錯誤", error, parent=self.window)
                    else:
                        messagebox.showinfo("成功", f"卡組已更名為 '{new_name}'。", parent=self.window)
                        self.refresh_decks()

    def start_review(self, deck_data):
        self.window.withdraw()
        
        def on_review_close():
            """當複習視窗關閉時，執行此函式。"""
            self.refresh_decks()
            self.window.deiconify()

        flashcard_window.create(self.parent, deck_data, on_review_close)

def create(parent):
    DeckSelectionApp(parent)
