import sys

import tkinter as tk
from tkinter import filedialog, messagebox
from loguru import logger


def select_file_window(fps="*.*",title=""):
    '''
    弹出文件选择窗口
    调用示例：
        excel_file = select_file_window(fps="*.xlsx;*.xls;*.csv", title="请选择Excel文件")
    :param fps->filetypes: 限制可选择的文件类型，默认无限制
    :param title: 弹出窗口标题
    :return: 文件路径
    '''
    root = tk.Tk()
    root.withdraw()
    filetypes = [
        ("文件", fps),
        ("所有文件", "*.*"),
    ]
    # 文件路径
    file_path = filedialog.askopenfilename(filetypes=filetypes, title=title)
    if file_path:
        return file_path
    logger.error('用户未选择任何有效文件，系统将自动退出~')
    messagebox.showerror("致命错误", "未选择任何有效文件，系统将自动退出~")
    sys.exit(1)
