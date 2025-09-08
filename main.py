import tkinter as tk
from tkinter import messagebox
import threading
import time
import pyautogui
from pynput import mouse, keyboard

class AutoClickerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("自动点击器")
        self.master.geometry("320x250")
        self.master.resizable(False, False)

        self.click_position = None
        self.clicking = False
        self.click_thread = None
        self.interval = 3  # 默认点击间隔秒

        self.position_label = tk.Label(master, text="点击位置: 未设置", font=("Arial", 12))
        self.position_label.pack(pady=5)

        self.status_label = tk.Label(master, text="状态: 未启动", fg="red", font=("Arial", 12))
        self.status_label.pack(pady=5)

        # 设置点击位置按钮
        self.set_button = tk.Button(master, text="设置点击位置", command=self.set_click_position)
        self.set_button.pack(pady=5)

        # 延迟输入框
        delay_frame = tk.Frame(master)
        delay_frame.pack(pady=5)
        tk.Label(delay_frame, text="点击间隔 (秒): ", font=("Arial", 10)).pack(side=tk.LEFT)
        self.delay_entry = tk.Entry(delay_frame, width=5)
        self.delay_entry.insert(0, "3")
        self.delay_entry.pack(side=tk.LEFT)

        self.hint_label = tk.Label(master, text="按 F1 启动/停止", font=("Arial", 10))
        self.hint_label.pack(pady=5)

        # 启动键盘监听器
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def set_click_position(self):
        self.status_label.config(text="状态: 等待点击...", fg="orange")
        threading.Thread(target=self._record_position).start()

    def _record_position(self):
        def on_click(x, y, button, pressed):
            if pressed:
                self.click_position = (x, y)
                self.position_label.config(text=f"点击位置: {self.click_position}")
                self.status_label.config(text="状态: 已设置点击位置", fg="green")
                return False
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

    def on_key_press(self, key):
        if key == keyboard.Key.f1:
            if self.clicking:
                self.stop_clicking()
            else:
                self.start_clicking()

    def start_clicking(self):
        if self.click_position is None:
            messagebox.showwarning("未设置位置", "请先设置点击位置！")
            return
        try:
            self.interval = float(self.delay_entry.get())
            if self.interval <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "请输入大于0的数字作为点击间隔")
            return

        self.clicking = True
        self.status_label.config(text="状态: 点击中", fg="blue")
        self.click_thread = threading.Thread(target=self._auto_click)
        self.click_thread.daemon = True
        self.click_thread.start()

    def stop_clicking(self):
        self.clicking = False
        self.status_label.config(text="状态: 已停止", fg="red")

    def _auto_click(self):
        while self.clicking:
            pyautogui.click(self.click_position)
            time.sleep(self.interval)

    def on_close(self):
        self.stop_clicking()
        self.listener.stop()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerGUI(root)
    root.mainloop()
