import requests
from bs4 import BeautifulSoup
import os
import tkinter as tk
import re
from tkinter import filedialog
from tkinter import ttk
from tkinter import scrolledtext


def sanitize_folder_name(folder_name):
    # 由於 gallery 的標題有可能出現一些不合法的 folder 名稱，因此需要將其作替換。
    # 以 539127 為例
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        # 將不合法的 char 替換成 "-"
        folder_name = folder_name.replace(char, '_')
    return folder_name


def batch_download():
    '''batch_input:
    https://nhentai.net/g/539127/
    https://nhentai.net/g/546088/
    546321
    '''
    batch_input = scrolled_text.get('1.0', tk.END).strip().splitlines()
    six_digits_list = []
    print(batch_input)
    for line in batch_input:
        six_digits_list.append(re.search(r'\d+', line).group())
        print(line)
    
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
        else:
            print(f'未選擇資料夾，下載中止。')
            root.destroy()
            return
    
    for six_digits in six_digits_list:
        # 目標 url
        url = f"https://nhentai.net/g/{six_digits}/"
        
        # 下載網頁內容
        response = requests.get(url)
        response.raise_for_status()
        
        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 找到標題
        title_tag = soup.find('h1', class_='title')
        if title_tag:
            before = title_tag.find('span', class_='before').text if title_tag.find('span', class_='before') else ''
            pretty = title_tag.find('span', class_='pretty').text if title_tag.find('span', class_='pretty') else ''
            after = title_tag.find('span', class_='after').text if title_tag.find('span', class_='after') else ''
            folder_name = f"{before}{pretty}{after}"  # 拼接三個字串作為資料夾名稱
        else:
            print("無法找到標題，無法建立資料夾。")
            continue
        
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
                    
        # 下載並保存圖片
        for idx, img_url in enumerate(image_urls, start=1):
            try:
                # 下載圖片
                img_data = requests.get(img_url)
                img_data.raise_for_status()
                
                # 生成圖片的檔案名稱
                img_name = f'image_{idx}.jpg'
                
                # 保存圖片到新資料夾
                with open(os.path.join(download_folder, img_name), 'wb') as img_file:
                    img_file.write(img_data.content)
                print(f'成功下載：{img_name}')
            except Exception as e:
                print(f'下載 {img_url} 失敗：{e}')
                
    root.destroy()


def download_gallery():
    """
    下載指定 nhentai 畫廊
    """
    # os.chdir(os.path.abspath(os.path.dirname(__file__)))
    # 六位數 = input('請輸入神的六位數：')
    
    six_digits = re.search(r'\d+', input_str.get()).group()
    # 目標 URL
    url = f"https://nhentai.net/g/{six_digits}/"
    
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
    form.title('nhentai downloader')
    # 視窗寬高
    form.geometry('640x480')
    # 寬、高可改變
    form.resizable(True, True)
    
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

    # Label 元件 (改用 ttk.Label)
    url_label = ttk.Label(page1, text='神的六位數字或網址：')
    url_label.grid(row=0, column=0, padx=(5, 10), pady=10, sticky='e')

    # Entry 元件 (改用 ttk.Entry)
    # 支持 nhentai 的 url 或是六位數字
    input_str = ttk.Entry(page1)  # 單行輸入框
    input_str.grid(row=0, column=1, padx=10, pady=10, sticky='we')

    # Button 元件 (改用 ttk.Button)
    button = ttk.Button(page1, text='抓取', command=download_gallery)
    button.grid(row=0, column=2, padx=10, pady=10, sticky='w')
    
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
    
    batch_button = ttk.Button(page2, text='批量下載', command=batch_download)
    batch_button.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    # ScrolledText 元件
    scrolled_text = scrolledtext.ScrolledText(page2, wrap='word')
    scrolled_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

    
    # third page: log 紀錄
    # page3 = ttk.Frame(notebook)
    # notebook.add(page3, text='Log')
    
    
    # 主循環
    form.mainloop()
    