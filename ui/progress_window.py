import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class ProgressWindow:
    def __init__(self, parent, title="處理中..."):
        self.window = ttk.Toplevel(parent)
        self.window.title(title)
        self.window.transient(parent)
        self.window.geometry("400x150")
        self.window.resizable(False, False)
        # 讓視窗無法被手動關閉
        self.window.protocol("WM_DELETE_WINDOW", lambda: None) 

        self.progress_label = ttk.Label(self.window, text="準備開始...", font=("Arial", 12))
        self.progress_label.pack(pady=20)

        self.progressbar = ttk.Progressbar(self.window, mode='determinate', length=350)
        self.progressbar.pack(pady=10)

    def update_progress(self, value, max_value, text):
        """更新進度條和狀態文字"""
        self.progressbar['maximum'] = max_value
        self.progressbar['value'] = value
        self.progress_label.config(text=text)
        self.window.update_idletasks() # 強制更新介面

    def close(self):
        """關閉視窗"""
        self.window.destroy()
