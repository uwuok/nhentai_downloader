import tkinter as tk
from PIL import Image, ImageTk

def on_resize(event):
    # 取得目前視窗大小
    new_width = event.width
    new_height = event.height

    # 使用原始圖片縮放，避免多次縮放後畫質變差
    resized = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    tk_resized = ImageTk.PhotoImage(resized)

    # 更新 Canvas 背景
    canvas.background = tk_resized  # 需要保存參考，避免被垃圾回收
    canvas.itemconfig(bg_image_id, image=tk_resized)

# 建立主視窗
root = tk.Tk()
root.geometry("800x600")

# 讀取原始圖片（建議高解析度）
original_image = Image.open("./_bg.jpg")

# 建立 Canvas
canvas = tk.Canvas(root, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# 先放一個初始圖
initial_resized = original_image.resize((800, 600), Image.Resampling.LANCZOS)
tk_initial = ImageTk.PhotoImage(initial_resized)
bg_image_id = canvas.create_image(0, 0, image=tk_initial, anchor="nw")
canvas.background = tk_initial  # 也要先存著避免 GC

# 監聽大小變動事件
root.bind("<Configure>", on_resize)

root.mainloop()
