import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ui import add_word_window, all_words_window, deck_selection_window, progress_window
import import_export_manager
import audio_player
import threading
import queue

class EmberRhythmApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EmberRhythm")
        self.root.geometry("600x750")

        main_frame = ttk.Frame(self.root, padding=(40, 20))
        main_frame.pack(expand=True, fill="both")
        
        ttk.Label(main_frame, text="EmberRhythm", font=("Arial", 32, "bold"), bootstyle="primary").pack(pady=(0, 20))

        intro_text = (
            "您好，此應用軟體是參考艾賓浩斯遺忘曲線，\n"
            "並結合閃卡記憶法而創建的一個小工具。\n"
            "希望透過科學的複習節奏，幫助您更有效地學習與記憶。\n"
            "祝您學習愉快！"
        )
        ttk.Label(
            main_frame, text=intro_text, font=("Arial", 12), 
            justify=tk.CENTER, bootstyle="secondary", wraplength=500
        ).pack(pady=(0, 30))

        btn_add = ttk.Button(main_frame, text="添加單詞", command=self.open_add_window, bootstyle="success-outline", padding=(20, 15))
        btn_add.pack(pady=8, fill='x')
        
        btn_all_words = ttk.Button(main_frame, text="字典", command=self.open_list_window, bootstyle="info-outline", padding=(20, 15))
        btn_all_words.pack(pady=8, fill='x')

        btn_decks = ttk.Button(main_frame, text="卡組分類", command=self.open_deck_window, bootstyle="warning-outline", padding=(20, 15))
        btn_decks.pack(pady=8, fill='x')
        
        btn_export = ttk.Button(main_frame, text="分享卡組", command=self.export_data, bootstyle="primary-outline", padding=(20, 15))
        btn_export.pack(pady=8, fill='x')

        btn_import = ttk.Button(main_frame, text="匯入卡組", command=self.import_data, bootstyle="primary-outline", padding=(20, 15))
        btn_import.pack(pady=8, fill='x')
        
        btn_exit = ttk.Button(main_frame, text="退出程式", command=self.quit_app, bootstyle="secondary", padding=(20, 15))
        btn_exit.pack(pady=8, fill='x')

    def open_add_window(self):
        add_word_window.create(self.root)

    def open_list_window(self):
        all_words_window.create(self.root)

    def open_deck_window(self):
        deck_selection_window.create(self.root)

    def export_data(self):
        """處理匯出邏輯，增加重設熟練度的選項"""
        filepath = filedialog.asksaveasfilename(
            title="儲存您的卡組檔案",
            defaultextension=".erf",
            filetypes=[("EmberRhythm 檔案", "*.erf"), ("所有檔案", "*.*")]
        )
        if not filepath: return

        should_reset = messagebox.askyesnocancel(
            "分享選項",
            "您希望如何匯出您的卡組？\n\n"
            "選擇「是 (Yes)」：重設熟練度 (適合分享給朋友)。\n"
            "選擇「否 (No)」：保留您的學習進度 (適合個人備份)。\n"
            "選擇「取消 (Cancel)」：取消本次匯出。",
            parent=self.root
        )

        if should_reset is None:
            return

        result = import_export_manager.export_decks(filepath, reset_srs=should_reset)
        if result:
            messagebox.showerror("匯出失敗", result, parent=self.root)
        else:
            messagebox.showinfo("成功", f"所有卡組已成功匯出至:\n{filepath}", parent=self.root)
    
    def import_data(self):
        """處理匯入邏輯，使用背景執行緒和進度條"""
        filepath = filedialog.askopenfilename(
            title="選擇要匯入的卡組檔案",
            filetypes=[("EmberRhythm 檔案", "*.erf"), ("所有檔案", "*.*")]
        )
        if not filepath: return
        
        if not messagebox.askyesno("確認匯入", "匯入將會合併新的卡組和單字到您目前的資料庫中。\n您確定要繼續嗎？", parent=self.root):
            return

        audio_player.unload_current_audio()

        self.progress_win = progress_window.ProgressWindow(self.root, "正在匯入...")
        self.progress_queue = queue.Queue()
        
        self.import_thread = threading.Thread(
            target=import_export_manager.import_decks,
            args=(filepath, self.progress_queue),
            daemon=True
        )
        self.import_thread.start()

        self.root.after(100, self.check_import_progress)

    def check_import_progress(self):
        try:
            message = self.progress_queue.get_nowait()
            msg_type, data = message[0], message[1:]

            if msg_type == 'update':
                current_step, max_steps, text = data[0], data[1], data[2]
                self.progress_win.update_progress(current_step, max_steps, text)
            elif msg_type == 'done':
                self.progress_win.close()
                messagebox.showinfo("成功", data[0], parent=self.root)
                return
            elif msg_type == 'error':
                self.progress_win.close()
                messagebox.showerror("匯入失敗", data[0], parent=self.root)
                return
            
            self.root.after(100, self.check_import_progress)

        except queue.Empty:
            if self.import_thread.is_alive():
                self.root.after(100, self.check_import_progress)
            else:
                self.progress_win.close()

    def quit_app(self):
        if messagebox.askokcancel("退出", "您確定要退出程式嗎？"):
            self.root.destroy()
