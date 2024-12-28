import requests
from bs4 import BeautifulSoup
import os
import tkinter as tk
from tkinter import filedialog


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

    六位數 = input('請輸入神的六位數：')
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
                img_id = img_url.split("/")[-2]  # 假設ID在 URL 中的第四個部分
                頁碼 = img_url.split("/")[-1].replace("t", "")  # 頁碼
                new_url = f"{base_url}{img_id}/{頁碼}"  # 構建新的 URL
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
        

        # 下載並保存圖片
        for idx, img_url in enumerate(image_urls):
            try:
                # 下載圖片
                img_data = requests.get(img_url)
                img_data.raise_for_status()  # 若請求失敗，會引發異常

                # 生成圖片的檔名
                img_name = f"image_{idx + 1}.jpg"

                # 保存圖片到新資料夾
                with open(os.path.join(download_folder, img_name), 'wb') as img_file:
                    img_file.write(img_data.content)

                print(f"成功下載: {img_name}")
            except Exception as e:
                print(f"下載 {img_url} 失敗: {e}")
    else:
        print("未選擇資料夾，下載中止。")
        
    

def view():
    return 

if __name__ == '__main__':
    view()
    download_gallery()