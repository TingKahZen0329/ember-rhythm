# audio_player.py (或未來要整合的地方)
import pygame
import os

def play_audio(file_path):
    """播放指定的聲音檔案"""
    if not file_path or not os.path.exists(file_path):
        print(f"聲音檔案不存在或路徑為空: {file_path}")
        return

    pygame.mixer.init() # 初始化混音器
    pygame.mixer.music.load(file_path) # 載入音樂檔案
    pygame.mixer.music.play() # 播放