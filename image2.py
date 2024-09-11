import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os

# 全局变量保存图片路径
current_image_path = None

# 提取 n 种主色调
def get_dominant_colors(infile, num_colors):
    image = Image.open(infile)
    small_image = image.resize((80, 80))  # 缩小图片以减少计算量
    result = small_image.convert("P", palette=Image.ADAPTIVE, colors=num_colors)  # 提取指定数量的颜色
    palette = result.getpalette()
    color_counts = sorted(result.getcolors(), reverse=True)
    colors = []

    for i in range(num_colors):
        palette_index = color_counts[i][1]
        dominant_color = palette[palette_index * 3:palette_index * 3 + 3]
        colors.append(tuple(dominant_color))

    return colors

# 处理加载图片
def load_image(file_path=None):
    global current_image_path
    if file_path is None:
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg;*.png;*.jpeg;*.bmp;*.gif")]
        )
    if file_path:
        try:
            image = Image.open(file_path)
            image.thumbnail((600, 300))  # 调整大小以适应显示区域
            photo = ImageTk.PhotoImage(image)
            label_image.config(image=photo)
            label_image.image = photo  # 保存引用，避免被垃圾回收

            # 保存当前图片路径
            current_image_path = file_path

            # 获取用户指定的颜色数量
            num_colors = int(color_num_entry.get())

            # 提取主色调并在 GUI 中预览
            dominant_colors = get_dominant_colors(file_path, num_colors)
            display_colors(dominant_colors)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

# 处理拖拽文件进入指定区域的事件
def drop(event):
    file_path = event.data.strip("{}")  # 获取拖放的文件路径并去掉大括号
    load_image(file_path)

# 处理点击加载图片
def click_to_load(event):
    load_image()

# 按RGB值进行排序
def sort_colors_by_rgb(colors):
    return sorted(colors, key=lambda color: (color[0], color[1], color[2]))  # 根据RGB值排序

# 显示颜色预览
def display_colors(colors):
    global current_colors
    current_colors = sort_colors_by_rgb(colors)  # 保存并按RGB排序

    # 清除之前的颜色标签
    for widget in frame_colors_inner.winfo_children():
        widget.destroy()

    # 固定每行显示10个色块
    blocks_per_row = 10

    # 计算需要的行数
    total_colors = len(current_colors)
    rows = (total_colors + blocks_per_row - 1) // blocks_per_row

    for row in range(rows):
        for col in range(blocks_per_row):
            color_index = row * blocks_per_row + col
            if color_index >= total_colors:
                continue

            color = current_colors[color_index]
            color_hex = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"

            # 创建包含色块和色值的Frame
            color_frame = tk.Frame(frame_colors_inner)

            # 创建颜色块
            color_label = tk.Label(color_frame, width=10, height=2, bg=color_hex)
            color_label.pack(side=tk.TOP, padx=5, pady=5)

            # 显示颜色的十六进制值
            color_value_label = tk.Label(color_frame, text=color_hex)
            color_value_label.pack(side=tk.BOTTOM, padx=5, pady=5)

            color_frame.grid(row=row, column=col, padx=5, pady=5)

    # 更新Canvas的scrollregion，以便能够滚动
    frame_colors_canvas.update_idletasks()
    frame_colors_canvas.config(scrollregion=frame_colors_canvas.bbox("all"))

# 刷新颜色显示
def refresh_colors():
    if current_image_path:
        # 获取用户输入的颜色数量
        num_colors = int(color_num_entry.get())
        # 提取主色调并在 GUI 中预览
        dominant_colors = get_dominant_colors(current_image_path, num_colors)
        display_colors(dominant_colors)
    else:
        messagebox.showwarning("Warning", "Please load an image first.")

# 保存颜色块及色值为PNG图片
def save_colors_image():
    if not current_colors:
        messagebox.showwarning("Warning", "No colors to save.")
        return

    # 获取用户自定义保存路径
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png")],
        initialdir=os.path.expanduser("~/Downloads"),
        initialfile="colors.png"
    )

    if file_path:
        try:
            # 创建图片对象
            block_width = 76
            block_height = 40
            padding = 10
            image_width = 10 * (block_width + padding)
            image_height = (len(current_colors) // 10 + 1) * (block_height + padding + 20)
            image = Image.new("RGB", (image_width, image_height), "white")
            draw = ImageDraw.Draw(image)

            # 设置字体
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except IOError:
                font = ImageFont.load_default()

            for i, color in enumerate(current_colors):
                color_hex = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
                x = (i % 10) * (block_width + padding)
                y = (i // 10) * (block_height + padding + 20)
                draw.rectangle([x, y, x + block_width, y + block_height], fill=color)
                draw.text((x + 5, y + block_height + 5), color_hex, fill="black", font=font)

            image.save(file_path)
            messagebox.showinfo("Success", f"Colors saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save colors: {e}")

# 创建 GUI 界面
root = TkinterDnD.Tk()  # 使用 TkinterDnD 创建根窗口
root.title("Dominant Color Extractor")

# 设置默认窗口大小为宽1350，高700
root.geometry("1350x700")

# 创建拖拽区域
drag_area_frame = tk.Frame(root, width=600, height=300, bg="lightgrey")
drag_area_frame.pack(pady=20)
drag_area_frame.pack_propagate(False)

# 在拖拽区域显示图片
label_image = tk.Label(drag_area_frame, text="拖动图片文件 或 单击加载图片文件", bg="lightgrey")
label_image.pack(fill="both", expand=True)

# 绑定拖拽和点击事件
label_image.bind("<Button-1>", click_to_load)  # 单击事件绑定
root.drop_target_register(DND_FILES)  # 注册根窗口为拖放目标
label_image.dnd_bind('<<Drop>>', drop)  # 拖拽事件绑定

# 颜色数量输入框、刷新按钮和保存按钮
frame_num_colors = tk.Frame(root)
frame_num_colors.pack(pady=10)

color_num_label = tk.Label(frame_num_colors, text="当前显示颜色数量:")
color_num_label.pack(side=tk.LEFT)

color_num_entry = tk.Entry(frame_num_colors, width=5)
color_num_entry.insert(0, "10")  # 默认提取 10 种颜色
color_num_entry.pack(side=tk.LEFT)

refresh_button = tk.Button(frame_num_colors, text="刷新颜色种类", command=refresh_colors)
refresh_button.pack(side=tk.LEFT, padx=10)

save_button = tk.Button(frame_num_colors, text="保存颜色png文件", command=save_colors_image)
save_button.pack(side=tk.LEFT, padx=10)

# 颜色预览区
frame_colors_outer = tk.Frame(root)  # 外部框架，用于居中显示颜色块
frame_colors_outer.pack(fill=tk.BOTH, expand=True)

frame_colors_canvas = tk.Canvas(frame_colors_outer)
frame_colors_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# 添加滚动条
scrollbar = tk.Scrollbar(frame_colors_outer, orient="vertical", command=frame_colors_canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill="y")

frame_colors_canvas.configure(yscrollcommand=scrollbar.set)

# 用来放置颜色标签的frame，绑定到Canvas上
frame_colors_inner = tk.Frame(frame_colors_canvas)
frame_colors_canvas.create_window((0, 0), window=frame_colors_inner, anchor="nw")

# 记录当前颜色
current_colors = []

# 运行 GUI
root.mainloop()
