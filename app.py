import requests
from bs4 import BeautifulSoup
import os
import tkinter as tk
import re
from tkinter import filedialog
from tkinter import ttk


def sanitize_folder_name(folder_name):
    # 由於 gallery 的標題有可能出現一些不合法的 folder 名稱，因此需要將其作替換。
    # 以 539127 為例
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        # 將不合法的 char 替換成 "-"
        folder_name = folder_name.replace(char, '_')
    return folder_name


def download_gallery():
    """
    下載指定 nhentai 畫廊
    """
    # os.chdir(os.path.abspath(os.path.dirname(__file__)))

    # 六位數 = input('請輸入神的六位數：')
    六位數 = six_digits.get()
    # 目標 URL
    url = f"https://nhentai.net/g/{六位數}/"
    
    # 下載網頁內容
    response = requests.get(url)
    response.raise_for_status()  # 若請求失敗，會引發異常

    # 解析 HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到標題部分
    title_tag = soup.find('h1', class_='title')
    if title_tag:
        before = title_tag.find('span', class_='before').text if title_tag.find('span', class_='before') else ''
        pretty = title_tag.find('span', class_='pretty').text if title_tag.find('span', class_='pretty') else ''
        after = title_tag.find('span', class_='after').text if title_tag.find('span', class_='after') else ''
        folder_name = f"{before}{pretty}{after}"  # 拼接三個字串作為資料夾名稱
    else:
        print("無法找到標題，無法建立資料夾。")
        exit()

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
                new_url = f"{base_url}{img_id}/{page}"  # 構建新的 URL
                image_urls.append(new_url)

    # 創建 Tkinter 根視窗
    root = tk.Tk()
    root.withdraw()  # 隱藏根視窗

    # 讓使用者選擇保存圖片的資料夾
    base_download_folder = filedialog.askdirectory(title="選擇保存圖片的資料夾")

    # 如果使用者選擇了資料夾，則創建新資料夾並下載圖片
    if base_download_folder:
        # 在選擇的資料夾中創建新資料夾
        download_folder = os.path.join(base_download_folder, sanitize_folder_name(folder_name))
        
        print(f'base_download_folder:{base_download_folder}')
        print(f'folder_name:{folder_name}')
        print(f'download_folder:{download_folder}')
        
        os.makedirs(download_folder, exist_ok=True)  # 創建資料夾，如果已經存在則不做改變
        
        # 根據指定的下載全部頁面
        tags = str(soup.findAll('span', class_='tags'))
        # tags = str(soup.findAll('a', class_="tag"))
        total_pages = int(re.findall(r'<span class="name">(\d+)<\/span>', tags)[0])
        
        print(total_pages)
        
        # 頁碼整數輸入驗證
        try:
            start = int(start_page.get()) if start_page.get() != '' else 1
            end = int(end_page.get()) if end_page.get() != '' else total_pages
        except ValueError:
            print('頁碼必須為整數。')
            root.destroy()
            return
        
        # 驗證頁碼範圍
        if start < 1 or end > len(image_urls) or start > end:
            print('頁碼範圍不正確，請重新檢查。')
            root.destroy()
            return
        
        selected_image_urls = image_urls[start - 1: end]
        

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
    else:
        print("未選擇資料夾，下載中止。")
        
    # 下載後必須手動關閉 root，不然會導致即使 form 關閉，程式依舊不會結束執行。
    root.destroy()
        
    
if __name__ == '__main__':
    form = tk.Tk()
    # 視窗標題
    form.title('聯絡資訊爬蟲')
    # 視窗寬高
    form.geometry('640x480')
    # 寬、高可改變
    form.resizable(True, True)

    # 配置列寬比例
    form.columnconfigure(0, weight=0)  # Label 的列（小比例，固定寬度）
    form.columnconfigure(1, weight=2)  # Entry 的列（主要佔用空間）
    form.columnconfigure(2, weight=0)  # Button 的列（小比例，固定寬度）

    # Label 元件 (改用 ttk.Label)
    url_label = ttk.Label(form, text='神的六位數字：')
    url_label.grid(row=0, column=0, padx=(5, 10), pady=10, sticky='e')

    # Entry 元件 (改用 ttk.Entry)
    six_digits = ttk.Entry(form)  # 單行輸入框
    # six_digits.insert(0, '')
    six_digits.grid(row=0, column=1, padx=10, pady=10, sticky='we')

    # Button 元件 (改用 ttk.Button)
    button = ttk.Button(form, text='抓取', command=download_gallery)
    button.grid(row=0, column=2, padx=10, pady=10, sticky='w')
    
    # 下載起始頁數選擇
    start_page_label = ttk.Label(form, text='起始頁數(預設為第一頁)：')
    start_page_label.grid(row=1, column=0, padx=0, pady=0, sticky='e')
    start_page = ttk.Entry(form)
    start_page.grid(row=1, column=1, padx=5, pady=5, sticky='we')
    
    # 下載結束頁數選擇
    end_page_label = ttk.Label(form, text='結束頁數(預設為最後一頁)：')
    end_page_label.grid(row=1, column=2, padx=(5, 10), pady=10, sticky='w')
    end_page = ttk.Entry(form)
    end_page.grid(row=1, column=3, padx=5, pady=5, sticky='e')

    # 配置行高比例
    # form.rowconfigure(1, weight=1)  # ScrolledText 所在行具有彈性空間

    # ScrolledText 元件 (保留原來的 tkinter.ScrolledText)
    # scrolled_text = ScrolledText(form, wrap='word')
    # scrolled_text.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

    # 主循環
    form.mainloop()
    