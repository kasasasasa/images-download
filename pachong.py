import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
from PIL import Image, ImageTk
import io


class BingImageDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片下载器")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")

        # 创建主框架
        self.main_frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = tk.Label(
            self.main_frame,
            text="必应图片下载器",
            font=("Helvetica", 24, "bold"),
            fg="#333333",
            bg="#f0f0f0"
        )
        title_label.pack(pady=(0, 20))

        # 设置区域
        settings_frame = tk.LabelFrame(
            self.main_frame,
            text="下载设置",
            bg="#f0f0f0",
            font=("Helvetica", 10, "bold"),
            padx=10,
            pady=10
        )
        settings_frame.pack(fill=tk.X, pady=10)

        # 关键词输入
        keyword_frame = tk.Frame(settings_frame, bg="#f0f0f0")
        keyword_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            keyword_frame,
            text="搜索关键词:",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.keyword_entry = tk.Entry(
            keyword_frame,
            width=40,
            font=("Helvetica", 12),
            relief=tk.SOLID,
            bd=1
        )
        self.keyword_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.keyword_entry.insert(0, "葡萄花鸟纹银香囊")  # 默认关键词

        # 下载数量
        count_frame = tk.Frame(settings_frame, bg="#f0f0f0")
        count_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            count_frame,
            text="下载数量:",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.count_var = tk.StringVar(value="20")
        self.count_spinbox = tk.Spinbox(
            count_frame,
            from_=1,
            to=100,
            width=5,
            textvariable=self.count_var,
            font=("Helvetica", 12),
            relief=tk.SOLID,
            bd=1
        )
        self.count_spinbox.pack(side=tk.LEFT)

        # 保存目录
        dir_frame = tk.Frame(settings_frame, bg="#f0f0f0")
        dir_frame.pack(fill=tk.X, pady=5)

        tk.Label(
            dir_frame,
            text="保存目录:",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.dir_var = tk.StringVar(value="D:\py\pachong\images")
        self.dir_entry = tk.Entry(
            dir_frame,
            textvariable=self.dir_var,
            width=40,
            font=("Helvetica", 12),
            relief=tk.SOLID,
            bd=1
        )
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.browse_button = tk.Button(
            dir_frame,
            text="浏览...",
            command=self.browse_directory,
            bg="#3498db",
            fg="white",
            font=("Helvetica", 10),
            relief=tk.FLAT,
            padx=10
        )
        self.browse_button.pack(side=tk.LEFT, padx=(10, 0))

        # 下载按钮
        self.download_button = tk.Button(
            self.main_frame,
            text="开始下载",
            command=self.start_download,
            bg="#27ae60",
            fg="white",
            font=("Helvetica", 14, "bold"),
            relief=tk.FLAT,
            padx=30,
            pady=10
        )
        self.download_button.pack(pady=20)

        # 进度条和状态
        self.progress_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.progress_frame.pack(fill=tk.X, pady=10)

        self.progress_label = tk.Label(
            self.progress_frame,
            text="就绪",
            font=("Helvetica", 10),
            bg="#f0f0f0",
            fg="#666666"
        )
        self.progress_label.pack(anchor=tk.W)

        self.progress = ttk.Progressbar(
            self.progress_frame,
            orient=tk.HORIZONTAL,
            length=400,
            mode='determinate'
        )
        self.progress.pack(fill=tk.X, pady=5)

        # 图片预览区域
        preview_frame = tk.LabelFrame(
            self.main_frame,
            text="图片预览",
            bg="#f0f0f0",
            font=("Helvetica", 10, "bold")
        )
        preview_frame.pack(fill=tk.X, pady=10)

        self.preview_canvas = tk.Canvas(
            preview_frame,
            bg="#ffffff",
            height=150,
            highlightthickness=0
        )
        self.preview_canvas.pack(fill=tk.X, padx=5, pady=5)

        # 添加滚动条
        scrollbar = tk.Scrollbar(
            preview_frame,
            orient=tk.HORIZONTAL,
            command=self.preview_canvas.xview
        )
        scrollbar.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.preview_canvas.configure(xscrollcommand=scrollbar.set)

        # 预览图片框架
        self.preview_images_frame = tk.Frame(self.preview_canvas, bg="#ffffff")
        self.preview_window = self.preview_canvas.create_window(
            (0, 0),
            window=self.preview_images_frame,
            anchor="nw"
        )

        # 日志区域
        log_frame = tk.LabelFrame(
            self.main_frame,
            text="下载日志",
            bg="#f0f0f0",
            font=("Helvetica", 10, "bold")
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            font=("Consolas", 10),
            bg="#ffffff",
            fg="#333333"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)

        # 状态栏
        self.status_bar = tk.Label(
            root,
            text="就绪 | 输入关键词并点击'开始下载'按钮",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Helvetica", 9),
            bg="#e0e0e0",
            fg="#333333"
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 下载计数器
        self.downloaded_count = 0
        self.total_images = 0
        self.preview_images = []

        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 绑定事件
        self.preview_images_frame.bind("<Configure>", self.on_frame_configure)

    def on_frame_configure(self, event):
        """更新画布滚动区域"""
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))

    def log_message(self, message):
        """向日志区域添加消息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # 滚动到底部
        self.log_text.config(state=tk.DISABLED)
        self.status_bar.config(text=message)

    def browse_directory(self):
        """浏览并选择保存目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_var.set(directory)

    def start_download(self):
        """开始下载过程"""
        keyword = self.keyword_entry.get().strip()
        count = self.count_var.get().strip()
        save_dir = self.dir_var.get().strip()

        # 验证输入
        if not keyword:
            messagebox.showerror("错误", "请输入搜索关键词")
            return

        try:
            count = int(count)
            if count <= 0:
                messagebox.showerror("错误", "下载数量必须大于0")
                return
        except ValueError:
            messagebox.showerror("错误", "下载数量必须是整数")
            return

        # 创建保存目录
        try:
            os.makedirs(save_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("错误", f"无法创建目录: {str(e)}")
            return

        # 禁用下载按钮
        self.download_button.config(state=tk.DISABLED, bg="#95a5a6", text="下载中...")
        self.log_message(f"开始下载: {keyword} (数量: {count})")
        self.progress["value"] = 0
        self.downloaded_count = 0
        self.total_images = count

        # 清除预览区域
        for widget in self.preview_images_frame.winfo_children():
            widget.destroy()
        self.preview_images = []

        # 在新线程中运行下载
        threading.Thread(
            target=self.download_bing_images,
            args=(keyword, count, save_dir),
            daemon=True
        ).start()

    def download_bing_images(self, keyword, count, save_dir):
        """下载必应图片的主函数"""
        # 必应图片搜索URL
        base_url = 'https://cn.bing.com/images/async?'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        downloaded = 0
        page_size = 30  # 每页图片数量
        offset = 0

        while downloaded < count:
            # 构造请求参数
            params = {
                'q': keyword,
                'first': offset,
                'count': page_size,
                'mmasync': '1'
            }

            try:
                # 发送请求
                response = requests.get(base_url, params=params, headers=headers, timeout=15)
                response.raise_for_status()

                # 解析HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                images = soup.find_all('a', class_='iusc')

                if not images:
                    self.log_message("没有找到更多图片")
                    break

                for img in images:
                    if downloaded >= count:
                        break

                    # 从JSON数据中提取图片URL
                    img_data = img.get('m')
                    if not img_data:
                        continue

                    try:
                        img_info = json.loads(img_data)
                        img_url = img_info.get('murl')

                        if not img_url:
                            continue

                        # 下载图片
                        try:
                            img_response = requests.get(img_url, headers=headers, timeout=15)
                            img_response.raise_for_status()
                            img_data = img_response.content

                            # 生成文件名
                            filename = f"{keyword}_{downloaded + 1}.jpg"
                            filepath = os.path.join(save_dir, filename)

                            # 保存图片
                            with open(filepath, 'wb') as f:
                                f.write(img_data)

                            downloaded += 1
                            self.downloaded_count = downloaded

                            # 更新UI
                            self.root.after(0, self.update_progress, downloaded, filename, img_data)

                            # 添加预览
                            if downloaded <= 10:  # 最多显示10个预览
                                self.root.after(0, self.add_image_preview, img_data, downloaded)

                        except Exception as e:
                            self.log_message(f"下载图片失败: {img_url}, 错误: {e}")

                    except json.JSONDecodeError:
                        continue

                offset += page_size
                time.sleep(1)  # 防止请求过于频繁

            except requests.exceptions.RequestException as e:
                self.log_message(f"请求失败: {e}")
                break

        # 下载完成
        self.root.after(0, self.download_complete, downloaded)

    def update_progress(self, downloaded, filename, img_data):
        """更新进度条和日志"""
        progress_value = (downloaded / self.total_images) * 100
        self.progress["value"] = progress_value
        self.progress_label.config(text=f"进度: {downloaded}/{self.total_images} ({progress_value:.1f}%)")
        self.log_message(f"已下载 {downloaded}/{self.total_images}: {filename}")

    def add_image_preview(self, img_data, index):
        """添加图片预览"""
        try:
            # 从字节数据创建图像
            image = Image.open(io.BytesIO(img_data))

            # 调整大小
            image.thumbnail((80, 80))

            # 转换为Tkinter兼容的格式
            photo = ImageTk.PhotoImage(image)

            # 创建标签显示图片
            label = tk.Label(
                self.preview_images_frame,
                image=photo,
                bg="#ffffff",
                bd=1,
                relief=tk.SOLID
            )
            label.image = photo  # 保持引用
            label.grid(row=0, column=index - 1, padx=5, pady=5)

            # 添加序号
            num_label = tk.Label(
                self.preview_images_frame,
                text=str(index),
                bg="#3498db",
                fg="white",
                font=("Helvetica", 8, "bold")
            )
            num_label.place(in_=label, x=0, y=0)

            # 保存引用
            self.preview_images.append((label, num_label))

        except Exception as e:
            self.log_message(f"创建预览失败: {str(e)}")

    def download_complete(self, downloaded):
        """下载完成后的处理"""
        self.log_message(f"下载完成，共下载 {downloaded} 张图片")
        self.progress_label.config(text="下载完成")
        self.download_button.config(state=tk.NORMAL, bg="#27ae60", text="开始下载")
        messagebox.showinfo("完成", f"下载完成! 共下载 {downloaded} 张图片")

    def on_closing(self):
        """关闭窗口时触发"""
        if messagebox.askokcancel("退出", "确定要退出程序吗?"):
            self.root.destroy()


# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = BingImageDownloaderApp(root)
    root.mainloop()
