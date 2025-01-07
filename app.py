import requests
from bs4 import BeautifulSoup
import os
import tkinter as tk
import re
import sqlite3
import unicodedata
import threading
from tkinter import filedialog
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk

def sanitize_folder_name(folder_name: str) -> str:
    """
    清理文件名稱，替換不合法的字元為下劃線(_)
	跟改不合適的檔案名稱
    Args:
        folder_name (str): 原始文件名稱

    Returns:
        str: 替換後文件名稱
    """
    # 由於 gallery 的標題如(539127)有可能出現一些不合法的 folder 名稱，因此需要將其作替換。
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        # 將不合法的 char 替換成 "-"
        folder_name = folder_name.replace(char, '_')
    return folder_name


def batch_download_thread():
    """
    在背景中執行序中執行批量下載
    """
    threading.Thread(target=batch_download, daemon=True).start()

def single_download_thread():
    """
    在背景執行序中執行單檔下載
    """
    threading.Thread(target=single_download, daemon=True).start()

def single_download_thread_LINE():
    """
    在背景執行序中發放LINE將h漫圖片方放給用戶
    """
    threading.Thread(target=single_download_LINE, daemon=True).start()

def batch_download():
    '''batch_input:
    https://nhentai.net/g/539127/
    https://nhentai.net/g/546088/
    546321
    '''

    """
    批量下載功能，允許輸入多個神的六位數或是網址下載對應的畫廊
    彈出選擇下載資料夾的視窗，供使用者指定下載的位置。
    """
    try:
        batch_input = batch_text.get('1.0', tk.END).strip().splitlines()
        six_digits_list = [re.search(r'\d+', line).group() for line in batch_input if re.search(r'\d+', line)]

        # 讓讀者選擇保存圖片的資料夾
        # root = tk.Tk()
        # root.withdraw()
        base_download_folder = filedialog.askdirectory(title='選擇保存圖片的資料夾')
        if not base_download_folder:
            # print('未選擇資料夾，下載中止。')
            messagebox.showinfo('未選擇下載資料夾，下載中止。')
            return

        # 批次處理每個神秘六位數
        for six_digits in six_digits_list:
            download_gallery(six_digits, base_download_folder, is_batch=True)
    except Exception as e:
        messagebox.showerror(f'進行批量下載時發生錯誤：{e}')
        return

    messagebox.showinfo('完成', '下載已完成！')


def single_download():
    """
    單檔下載功能，允許使用者輸入一個神的六位數或是網址並下載對應的畫廊

    彈出選擇下載資料夾之視窗，下載單個畫廊。
    """

    try:
        base_download_folder = filedialog.askdirectory(title='選擇保存圖片的資料夾')
        six_digits = re.search(r'\d+', input_str.get()).group()
        if not base_download_folder:
            # print('未選擇資料夾，下載中止。')
            messagebox.showerror('錯誤', '未選擇下載資料夾，下載中止。')
            return
        download_gallery(six_digits, base_download_folder, is_batch=False)
    except Exception as e:
        messagebox.showerror('錯誤', f'進行單檔下載時發生錯誤：{e}')
        return

    messagebox.showinfo('完成', '下載已完成！')




def single_download_LINE():
    """
    單檔下載LINE訊息發放功能，允許使用者輸入一個神的六位數或是網址並下載對應的畫廊

    將找到的URL圖片發送給用戶的LINE
    """

    try:
        six_digits = re.search(r'\d+', input_str.get()).group() #六位數變數
        # 目標 URL
        url = f"https://nhentai.net/g/{six_digits}/"

        # 下載網頁內容
        response = requests.get(url)
        response.raise_for_status()  # 若請求失敗，會引發異常

        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        # 找到所有 <div class="thumb-container"> 標籤
        thumb_containers = soup.find_all('div', class_='thumb-container')

        # 提取每個 <div class="thumb-container"> 中 <noscript> 標籤內的圖片 URL
        image_urls = []
        for container in thumb_containers:
            noscript_tag = container.find('noscript')
            if noscript_tag:
                img_tag = noscript_tag.find('img')
                if img_tag and img_tag.has_attr('src'):
                    img_url = img_tag['src']

                    # 提取 ID 部分並構造新的 URL
                    base_url = "https://i2.nhentai.net/galleries/"
                    img_id = img_url.split("/")[-2]  # 假設 ID 在 URL 中的第四個部分
                    page = img_url.split("/")[-1].replace("t", "")  # 頁碼
                    # 檢查後綴格式，避免重複拼接
                    new_url = f"{base_url}{img_id}/{page}"  # 構建新的 URL
                    # 使用 re 移除重複的 .webp
                    new_url = re.sub(r'\.webp(\.webp)+$', '.webp', new_url)
                    print(f'constructed url: {new_url}')
                    image_urls.append(new_url)
        # 以圖片 URL 傳送 LINE 訊息
        htpp_get_img = 'https://script.google.com/macros/s/AKfycbwgqrIGx0QfwpmWz2MUp-LL8RAmVb5QK7G4uAhIPXA9u3IdZxACXJplRpH2G14t9N4/exec?to= U9de18aa02a082d52b9c8c1df420213d4&img='
        htpp_get_txt = 'https://script.google.com/macros/s/AKfycbwgqrIGx0QfwpmWz2MUp-LL8RAmVb5QK7G4uAhIPXA9u3IdZxACXJplRpH2G14t9N4/exec?to= U9de18aa02a082d52b9c8c1df420213d4&t='
        for out_url in image_urls:
            LINE_response = requests.get(htpp_get_img+out_url)
            LINE_response.close()
        LINE_response = requests.get(htpp_get_txt+"LINE 訊息以全部發放完成")
        LINE_response.close()
        messagebox.showinfo('完成', 'LINE 訊息以全部發放完成')
        return
    except Exception as e:
        messagebox.showerror('錯誤', f'LINE 訊息發放錯誤：{e}')
        return


def download_gallery(six_digits: str, base_download_folder: str, is_batch=False):
    """
    下載指定的畫廊，為每個畫廊獨立創建一個資料夾存放

    Args:
        six_digits (str): 神的六位數
        base_download_folder (str): 使用者選擇存放的位置
        is_batch (bool, optional): 判斷是否為批量下載. 預設為 False
    """

    # 目標 URL
    url = f"https://nhentai.net/g/{six_digits}/"

    # 下載網頁內容
    response = requests.get(url)
    response.raise_for_status()  # 若請求失敗，會引發異常

    # 解析 HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到標題部分
    title_tag = soup.find('h1', class_='title')
    # 如果未找到 title_tag 則以 six_digits 作為 folder_name
    folder_name = sanitize_folder_name(title_tag.text if title_tag else six_digits)
    # 在 DB 中新增紀錄(狀態為"下載中")
    record_id = add_record(folder_name, '下載中')
    if title_tag:
        before = title_tag.find('span', class_='before').text if title_tag.find('span', class_='before') else ''
        pretty = title_tag.find('span', class_='pretty').text if title_tag.find('span', class_='pretty') else ''
        after = title_tag.find('span', class_='after').text if title_tag.find('span', class_='after') else ''
        folder_name = f"{before}{pretty}{after}"  # 拼接三個字串作為資料夾名稱
    else:
        print("無法找到標題，無法建立資料夾。")
        update_record(record_id, '下載失敗')
        return
        # raise ValueError

    # 創建新資料夾
    download_folder = os.path.join(base_download_folder, sanitize_folder_name(folder_name))
    os.makedirs(download_folder, exist_ok=True)
    print(f'創建資料夾：{download_folder}')

    # 找到所有 <div class="thumb-container"> 標籤
    thumb_containers = soup.find_all('div', class_='thumb-container')

    # 提取每個 <div class="thumb-container"> 中 <noscript> 標籤內的圖片 URL
    image_urls = []
    for container in thumb_containers:
        noscript_tag = container.find('noscript')
        if noscript_tag:
            img_tag = noscript_tag.find('img')
            if img_tag and img_tag.has_attr('src'):
                img_url = img_tag['src']

                # 提取 ID 部分並構造新的 URL
                base_url = "https://i2.nhentai.net/galleries/"
                img_id = img_url.split("/")[-2]  # 假設 ID 在 URL 中的第四個部分
                page = img_url.split("/")[-1].replace("t", "")  # 頁碼
                # 檢查後綴格式，避免重複拼接
                new_url = f"{base_url}{img_id}/{page}"  # 構建新的 URL
                # 使用 re 移除重複的 .webp
                new_url = re.sub(r'\.webp(\.webp)+$', '.webp', new_url)
                print(f'constructed url: {new_url}')
                image_urls.append(new_url)

    # 下載指定範圍的頁面
    start = 1
    if not is_batch:
        tags = str(soup.findAll('span', class_='tags'))
        # tags = str(soup.findAll('a', class_="tag"))
        total_pages = int(re.findall(r'<span class="name">(\d+)<\/span>', tags)[0])

        print(total_pages)

        # 頁碼整數輸入驗證
        try:
            start = int(start_page.get()) if start_page.get() != '' else 1
            end = int(end_page.get()) if end_page.get() != '' else total_pages
        except ValueError:
            # print('頁碼必須為整數。')
            messagebox.showwarning('警告', '頁碼必須為整數')
            update_record(record_id, '下載失敗')
            raise ValueError

        # 驗證頁碼範圍
        if start < 1 or end > len(image_urls) or start > end:
            # print('頁碼範圍不正確，請重新檢查。')
            messagebox.showwarning('警告', '頁碼範圍不正確，請重新檢查。')
            update_record(record_id, '下載失敗')
            raise ValueError
            # return
        selected_image_urls = image_urls[start - 1: end]
    else:
        selected_image_urls = image_urls

    # 下載並保存圖片
    for idx, img_url in enumerate(selected_image_urls, start=start):
        try:
            # 下載圖片
            img_data = requests.get(img_url)
            img_data.raise_for_status()  # 若請求失敗，會引發異常
            # 生成圖片的檔名
            img_name = f"image_{idx}.jpg"

            # 保存圖片到新資料夾
            with open(os.path.join(download_folder, img_name), 'wb') as img_file:
                img_file.write(img_data.content)
                print(f"成功下載: {img_name}")
        except Exception as e:
            print(f"下載 {img_url} 失敗: {e}")
            update_record(record_id, '下載失敗')
            return
    print(f'{folder_name}: 下載完成。')
    update_record(record_id, '下載完成')


def init_db():
    """
    資料庫初始化
    """
    conn = sqlite3.connect('download_history.db')
    conn.row_factory = sqlite3.Row # 將結果轉換成字典
    cursor = conn.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gallery_name TEXT NOT NULL,
            download_date TEXT NOT NULL,
            status TEXT NOT NULL
        )
        '''
    )
    conn.commit()
    conn.close()

def add_record(gallery_name, status) -> int:
    """
    將 record 加入至 database 中，並回傳新增記錄的 id
    Args:
        gallery_name (str): 畫廊名稱
        status (str): 下載狀態
    Returns:
        int: 新增記錄的 id
    """
    conn = sqlite3.connect('download_history.db')
    cursor = conn.cursor()
    try:
        download_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''INSERT INTO history (gallery_name, download_date, status)
                          VALUES (?, ?, ?)''', (gallery_name, download_date, status))
        conn.commit()
        record_id = cursor.lastrowid  # 獲取剛新增的記錄 id
        return record_id
    except sqlite3.Error as e:
        print(f"新增記錄失敗：{e}")
        return None
    finally:
        conn.close()

def update_record(record_id, status):
    """
    更新下載紀錄（根據 id）
    Args:
        record_id (int): 唯一識別符
        status (str): 更新後的下載狀態
    """
    try:
        conn = sqlite3.connect('download_history.db')
        cursor = conn.cursor()

        # 檢查 id 是否存在
        cursor.execute('SELECT COUNT(*) FROM history WHERE id = ?', (record_id,))
        count = cursor.fetchone()[0]
        if count == 0:
            print(f"記錄未找到：id = {record_id}")
            return
        # 更新狀態
        cursor.execute('''UPDATE history SET status = ? WHERE id = ?''', (status, record_id))
        conn.commit()
        print(f"成功更新：id = {record_id} 狀態為 {status}")
    except sqlite3.Error as e:
        print(f"資料庫操作失敗：{e}")
    finally:
        conn.close()

def view_history():
    """
    將歷史紀錄內容顯示至 GUI 上
    """
    conn = sqlite3.connect('download_history.db')
    conn.row_factory = sqlite3.Row # 將結果轉換成字典
    cursor = conn.cursor()
    cursor.execute('''SELECT id, gallery_name, download_date, status FROM history''')
    records = cursor.fetchall()
    conn.close()

    # 沒有內容
    if not records:
        return

    def get_display_width(text: str) -> int:
        """
        計算字串的顯示長度，考慮全型和半型字元的情況

        Args:
            text (str): 字串

        Returns:
            int: 寬度
        """
        return sum(2 if unicodedata.east_asian_width(char) in 'WF' else 1 for char in text)

    def pad_to_width(text: str, width: int) -> str:
        """
        將字串填充到指定的寬度

        Args:
            text (str): 輸入字串
            width (int): 寬度

        Returns:
            str: 調整過後的字串
        """

        # 確保 text 是字串
        text = str(text)
        current_width = get_display_width(text)
        padding = width - current_width
        return text + ' ' * padding

    # 顯示標籤設定
    headers = ['ID', '名稱', '下載日期', '狀態']
    widths = [5, 120, 28, 8]
    header_line = ''.join(pad_to_width(header, width) for header, width in zip(headers, widths))
    history_text.insert(tk.END, header_line + '\n')
    history_text.insert(tk.END, '-' * sum(widths) + '\n')

    for record in records:
        line = ''.join(
            pad_to_width(record[key], width)
            for key, width in zip(['id', 'gallery_name', 'download_date', 'status'], widths)
        )
        print(line)
        history_text.insert(tk.END, line + '\n')
    history_text.insert(tk.END, '-' * sum(widths) + '\n')
    history_text.insert(tk.END, '\n')

    # print("\nDownload History:")
    # print("ID | Gallery Name | Download Date | Status")
    # print("-" * 50)
    # for record in records:
    #     print(f"{record[0]} | {record[1]} | {record[2]} | {record[3]}")


if __name__ == '__main__':
    init_db()

    form = tk.Tk()
    # 視窗標題
    form.title('nhentai downloader')
    # 視窗寬高
    form.geometry('800x800')
    # 寬、高可改變
    form.resizable(True, True)

    # 圖片檔路徑
    image_path = "./真封面.jpg"  # 請換成自己的檔案路徑
    # 讀取圖片並轉成 Tkinter 能使用的 PhotoImage
    pil_image = Image.open('./真封面.jpg')  # 讀取本地檔案
    # 如需縮放，可使用 pil_image.resize((width, height), Image.ANTIALIAS)
    pil_image.resize((900, 900),  Image.Resampling.LANCZOS)
    bg_image = ImageTk.PhotoImage(pil_image)





    # 使用 Notebook 元件實現頁面切換
    notebook = ttk.Notebook(form)
    notebook.pack(fill='both', expand=True)

    # first page: 單檔下載(可選擇下載頁數)
    page1 = ttk.Frame(notebook)
    notebook.add(page1, text='單檔下載')

    # 配置列寬比例
    page1.columnconfigure(0, weight=0)  # Label 的列（小比例，固定寬度）
    page1.columnconfigure(1, weight=2)  # Entry 的列（主要佔用空間）
    page1.columnconfigure(2, weight=0)  # Button 的列（小比例，固定寬度）

    # second page: 批量下載(不可選擇下載頁數)
    # 建立一個 Label 充當背景
    bg_label = ttk.Label(page1, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Label 元件 (改用 ttk.Label)
    url_label = ttk.Label(page1, text='神的六位數字或網址：')
    url_label.grid(row=0, column=0, padx=(5, 10), pady=10, sticky='e')

    # Entry 元件 (改用 ttk.Entry)
    # 支持 nhentai 的 url 或是六位數字
    input_str = ttk.Entry(page1)  # 單行輸入框
    input_str.grid(row=0, column=1, padx=10, pady=10, sticky='we')

    # Button 元件 (改用 ttk.Button)
    button = ttk.Button(page1, text='抓取', command=single_download_thread)
    button.grid(row=0, column=2, padx=10, pady=10, sticky='w')

    # Button 元件 (改用 ttk.Button)
    button2 = ttk.Button(page1, text='LINE下載', command=single_download_LINE)
    button2.grid(row=0, column=3, padx=10, pady=10, sticky='w')

    # 下載起始頁數選擇
    start_page_label = ttk.Label(page1, text='起始頁數(預設為第一頁)：')
    start_page_label.grid(row=1, column=0, padx=0, pady=0, sticky='e')
    start_page = ttk.Entry(page1)
    start_page.grid(row=1, column=1, padx=5, pady=5, sticky='we')

    # 下載結束頁數選擇
    end_page_label = ttk.Label(page1, text='結束頁數(預設為最後一頁)：')
    end_page_label.grid(row=1, column=2, padx=(5, 10), pady=10, sticky='w')
    end_page = ttk.Entry(page1)
    end_page.grid(row=1, column=3, padx=5, pady=5, sticky='e')

    # 配置行高比例
    # page1.rowconfigure(1, weight=1)  # ScrolledText 所在行具有彈性空間


    # second page: 批量下載
    page2 = ttk.Frame(notebook)
    notebook.add(page2, text='批量下載')

    # 調整行列配置
    page2.rowconfigure(1, weight=1)
    page2.columnconfigure(0, weight=1)

    # 配置寬高比例
    batch_url_label = ttk.Label(page2, text='以行為單位填入網址或數字：')
    batch_url_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')

    batch_button = ttk.Button(page2, text='批量下載', command=batch_download_thread)
    batch_button.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    # ScrolledText 元件
    batch_text = scrolledtext.ScrolledText(page2, wrap='word')
    batch_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

    # third page: 下載紀錄
    page3 = ttk.Frame(notebook)
    notebook.add(page3, text='下載紀錄')

     # 調整行列配置
    page3.rowconfigure(1, weight=1)
    page3.columnconfigure(0, weight=1)

    # 配置寬高比例
    batch_url_label = ttk.Label(page3, text='下載紀錄')
    batch_url_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')

    batch_button = ttk.Button(page3, text='獲取下載紀錄', command=view_history)
    batch_button.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    # ScrolledText 元件
    history_text = scrolledtext.ScrolledText(page3, wrap='word')
    history_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

    # 主循環
    form.mainloop()
