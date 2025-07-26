import pygame
import os

# 一個全域旗標，確保混音器只被初始化一次
mixer_initialized = False

def initialize_player():
    """如果 pygame 混音器尚未初始化，則進行初始化。"""
    global mixer_initialized
    if not mixer_initialized:
        try:
            pygame.mixer.init()
            mixer_initialized = True
            print("音訊播放器初始化成功。")
        except pygame.error as e:
            print(f"無法初始化音訊播放器: {e}")
            mixer_initialized = False

def play_audio(file_path):
    """播放指定的聲音檔案。"""
    if not mixer_initialized:
        print("播放器未初始化，無法播放。")
        return

    if not file_path or not os.path.exists(file_path):
        print(f"聲音檔案不存在或路徑為空: {file_path}")
        return

    try:
        # 使用 stop() 來停止任何可能正在播放的音樂，避免重疊
        pygame.mixer.music.stop()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
    except pygame.error as e:
        print(f"播放檔案時發生錯誤 ({file_path}): {e}")

def stop_audio():
    """停止任何目前正在播放的聲音。"""
    if not mixer_initialized:
        return
    pygame.mixer.music.stop()