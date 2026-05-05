
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import os

class PhotoSketchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("照片转素描工具")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        # 存储原始图片和结果
        self.original_image = None
        self.sketch_image = None
        self.original_pil = None
        self.sketch_pil = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # 标题
        title_label = tk.Label(
            self.root, 
            text="🎨 照片转素描工具", 
            font=("Microsoft YaHei", 24, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        title_label.pack(pady=20)
        
        # 按钮区域
        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=10)
        
        # 上传按钮
        self.upload_btn = tk.Button(
            btn_frame,
            text="📁 上传图片",
            font=("Microsoft YaHei", 12),
            bg="#4CAF50",
            fg="white",
            width=15,
            height=2,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.upload_image
        )
        self.upload_btn.pack(side=tk.LEFT, padx=10)
        
        # 下载按钮
        self.download_btn = tk.Button(
            btn_frame,
            text="💾 下载素描图",
            font=("Microsoft YaHei", 12),
            bg="#2196F3",
            fg="white",
            width=15,
            height=2,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.download_image,
            state=tk.DISABLED
        )
        self.download_btn.pack(side=tk.LEFT, padx=10)
        
        # 清空按钮
        self.clear_btn = tk.Button(
            btn_frame,
            text="🗑️ 清空",
            font=("Microsoft YaHei", 12),
            bg="#f44336",
            fg="white",
            width=15,
            height=2,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.clear_all
        )
        self.clear_btn.pack(side=tk.LEFT, padx=10)
        
        # 图片显示区域
        display_frame = tk.Frame(self.root, bg="#f0f0f0")
        display_frame.pack(pady=20, expand=True, fill=tk.BOTH)
        
        # 原图预览框
        original_frame = tk.LabelFrame(
            display_frame,
            text=" 原图预览 ",
            font=("Microsoft YaHei", 12, "bold"),
            bg="white",
            fg="#333333",
            width=450,
            height=450
        )
        original_frame.pack(side=tk.LEFT, padx=20, expand=True, fill=tk.BOTH)
        original_frame.pack_propagate(False)
        
        self.original_label = tk.Label(
            original_frame,
            bg="#e0e0e0",
            text="暂无图片\n点击上方按钮上传",
            font=("Microsoft YaHei", 14),
            fg="#666666"
        )
        self.original_label.pack(expand=True, fill=tk.BOTH)
        
        # 箭头指示
        arrow_label = tk.Label(
            display_frame,
            text="➡️",
            font=("Microsoft YaHei", 30),
            bg="#f0f0f0",
            fg="#666666"
        )
        arrow_label.pack(side=tk.LEFT)
        
        # 结果预览框
        result_frame = tk.LabelFrame(
            display_frame,
            text=" 素描结果预览 ",
            font=("Microsoft YaHei", 12, "bold"),
            bg="white",
            fg="#333333",
            width=450,
            height=450
        )
        result_frame.pack(side=tk.LEFT, padx=20, expand=True, fill=tk.BOTH)
        result_frame.pack_propagate(False)
        
        self.result_label = tk.Label(
            result_frame,
            bg="#e0e0e0",
            text="处理后的素描图\n将显示在这里",
            font=("Microsoft YaHei", 14),
            fg="#666666"
        )
        self.result_label.pack(expand=True, fill=tk.BOTH)
        
        # 状态栏
        self.status_label = tk.Label(
            self.root,
            text="就绪 - 请上传图片",
            font=("Microsoft YaHei", 10),
            bg="#f0f0f0",
            fg="#666666",
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=20, pady=10)
        
        # 参数调节（可选）
        param_frame = tk.Frame(self.root, bg="#f0f0f0")
        param_frame.pack(pady=5)
        
        tk.Label(
            param_frame,
            text="模糊强度:",
            font=("Microsoft YaHei", 10),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT)
        
        self.blur_scale = tk.Scale(
            param_frame,
            from_=1,
            to=50,
            orient=tk.HORIZONTAL,
            length=200,
            bg="#f0f0f0",
            highlightthickness=0
        )
        self.blur_scale.set(19)
        self.blur_scale.pack(side=tk.LEFT, padx=10)
        
        self.apply_btn = tk.Button(
            param_frame,
            text="应用",
            font=("Microsoft YaHei", 10),
            bg="#FF9800",
            fg="white",
            width=8,
            command=self.reapply_sketch
        )
        self.apply_btn.pack(side=tk.LEFT, padx=5)
        
    def upload_image(self):
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        try:
            # 读取图片
            self.original_image = cv2.imread(file_path)
            if self.original_image is None:
                messagebox.showerror("错误", "无法读取该图片文件！")
                return
                
            # 转换为 RGB 用于显示
            self.original_pil = Image.fromarray(
                cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            )
            
            # 显示原图
            self.display_image(self.original_pil, self.original_label)
            
            # 生成素描
            self.generate_sketch()
            
            self.status_label.config(
                text=f"已加载: {os.path.basename(file_path)} | 尺寸: {self.original_image.shape[1]}x{self.original_image.shape[0]}"
            )
            
        except Exception as e:
            messagebox.showerror("错误", f"处理图片时出错:\n{str(e)}")
            
    def generate_sketch(self):
        if self.original_image is None:
            return
            
        try:
            # 获取模糊参数（必须是奇数）
            blur_val = self.blur_scale.get()
            if blur_val % 2 == 0:
                blur_val += 1
                
            # 素描算法
            gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            inverted_gray_image = 255 - gray_image
            blurred_inverted_gray_image = cv2.GaussianBlur(
                inverted_gray_image, (blur_val, blur_val), 0
            )
            inverted_blurred_image = 255 - blurred_inverted_gray_image
            sketch = cv2.divide(gray_image, inverted_blurred_image, scale=256.0)
            
            # 保存结果
            self.sketch_image = sketch
            self.sketch_pil = Image.fromarray(sketch)
            
            # 显示结果
            self.display_image(self.sketch_pil, self.result_label)
            
            # 启用下载按钮
            self.download_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("错误", f"生成素描时出错:\n{str(e)}")
            
    def reapply_sketch(self):
        if self.original_image is not None:
            self.generate_sketch()
            self.status_label.config(text="已重新应用参数")
            
    def display_image(self, pil_image, label):
        """在Label中显示图片，保持比例缩放"""
        # 获取Label尺寸
        label.update_idletasks()
        max_width = label.winfo_width() - 20
        max_height = label.winfo_height() - 20
        
        if max_width <= 1 or max_height <= 1:
            max_width = 400
            max_height = 400
            
        # 计算缩放比例
        img_width, img_height = pil_image.size
        ratio = min(max_width / img_width, max_height / img_height)
        
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        # 缩放图片
        resized = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 转换为Tkinter格式
        tk_image = ImageTk.PhotoImage(resized)
        
        # 保存引用防止被GC
        label.image = tk_image
        label.config(image=tk_image, text="", bg="white")
        
    def download_image(self):
        if self.sketch_pil is None:
            messagebox.showwarning("提示", "没有可下载的图片！")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="保存素描图",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("BMP", "*.bmp"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.sketch_pil.save(file_path)
                messagebox.showinfo("成功", f"素描图已保存到:\n{file_path}")
                self.status_label.config(text=f"已保存: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败:\n{str(e)}")
                
    def clear_all(self):
        self.original_image = None
        self.sketch_image = None
        self.original_pil = None
        self.sketch_pil = None
        
        self.original_label.config(
            image="",
            text="暂无图片\n点击上方按钮上传",
            bg="#e0e0e0"
        )
        self.original_label.image = None
        
        self.result_label.config(
            image="",
            text="处理后的素描图\n将显示在这里",
            bg="#e0e0e0"
        )
        self.result_label.image = None
        
        self.download_btn.config(state=tk.DISABLED)
        self.status_label.config(text="就绪 - 请上传图片")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoSketchApp(root)
    root.mainloop()
