# nhentai_downloader

## 作業說明：

### 學習的目標

本次作業以知名紳士網站 nhentai 為爬蟲的對象，將課堂上所學到的相關知識為基礎完成此程式，包括但不限於 BeautifulSoup, tkinter, sqlite3, unicodedata, regular expression, requests 等 Python 模組，希望能夠藉此來加深對 Python、網路爬蟲、資料庫操作以及對文件管理的理解。在這個作業中，我們撰寫了一個 GUI 介面供使用者操作，並能將 nhentai 上的圖片透過爬蟲的方式下載到使用者指定的資料夾。


### 預期效益

透過讓使用者在瀏覽網站時，看到自己滿意的作品不需要再手動一個一個右鍵下載。只需要透過此程式輸入該作品的神之六位數或是該作品的網址即可完成一鍵下載之操作，讓使用者解放雙手，讓雙手用於更重要的事情上。


## 背景資料：

### 問題的介紹


### 環境介紹：
包括硬體、周邊、作業系統與使用工具…等。

硬體：筆記型電腦
周邊：網路
作業系統：Windows 11
使用工具：
- Vistual studio code
- Chrome 
- https://online.visual-paradigm.com/
- python             3.11.6
- beautifulsoup4     4.12.3
- bs4                0.0.2
- certifi            2024.12.14
- charset-normalizer 3.4.1
- idna               3.10
- pip                23.2.1
- requests           2.32.3
- setuptools         65.5.0
- soupsieve          2.6
- urllib3            2.3.0

## 實作方法：

### 環境檢查

首先需要確保 Python 已經安裝，為了避免版本不匹配的問題，這邊建議以 Python 3.11.6 作安裝：
https://www.python.org/downloads/release/python-3116/

### 安裝與設定

1.下載 github 上的檔案
```bash
git clone https://github.com/uwuok/nhentai_downloader.git
```

2.建立虛擬環境
```bash 
python -m venv venv
```

3.進入建立好的虛擬環境
```bash 
.\venv\Scripts\activate
```

4.安裝本程式所需的庫
```bash
pip install -r .\requirements.txt
```

5.執行程式
```bash
python .\app.py
```

### 解決方案步驟

步驟1：初始化資料庫，創建資料表來儲存每個所下載的畫廊的名稱、下載日期以及下載狀態。
步驟2：初始化使用的介面，介面分別有"單檔下載"、"批量下載"以及"下載紀錄"，預設介面為"單檔下載"。
步驟3：在使用者填入 nhentai 的六位數字或是網址時，解析所填入的數字或網址，透過 requests 發送 HTTP 請求，解析並獲取該畫廊的資訊以及該畫廊所有頁面的網址，並插入一個新的 record 其狀態為"下載中"。
步驟4：將圖片下載至指定的資料夾。
步驟5：根據下載結果更新 record 的狀態。
步驟6：透過 messagebox 顯示顯示下載結果。

操作示範

1.執行程式後會顯示 GUI 介面，預設為單檔下載的介面
![image](https://hackmd.io/_uploads/ryiPRbtIJl.png)

2.在單檔下載的介面中，輸入神的六位數或是網址以及欲下載的頁面範圍；若無輸入葉面範圍的數值，則預設為第一頁到最後一頁。
![image](https://hackmd.io/_uploads/rkjuWXtI1x.png)


3.按下"抓取"按鈕後，讓使用者選擇下載檔案欲存放的位置
![image](https://hackmd.io/_uploads/HJEaJMFLyg.png)

3-1.若在未選擇下載位置則會出現以下錯誤
![image](https://hackmd.io/_uploads/Byp2AWF8kg.png)

4.下載完成後會有出現視窗提示下載完成
![image](https://hackmd.io/_uploads/rkoi0-FLJl.png)

4-1.若下載失敗則會出現以下錯誤提示
![image](https://hackmd.io/_uploads/Sy8cVGYLyl.png)


5.在資料夾裡會有一個以作品名稱為資料夾名稱的檔案點進去後是以下畫面
![image](https://hackmd.io/_uploads/HJdQBzK8ye.png)
![image](https://hackmd.io/_uploads/S1nR0btU1e.png)

6.批量下載則範例
![image](https://hackmd.io/_uploads/SkYZQMF8kl.png)


7.查看下載紀錄
![image](https://hackmd.io/_uploads/SyQ0DztUkg.png)
![image](https://hackmd.io/_uploads/SyeU_GYIkg.png)

### 流程圖

![image](https://hackmd.io/_uploads/SJ9iAlO8yl.png)


### 解決方案中所運用之技巧

#### 下載的畫廊可能存在不合法的字元
由於程式的邏輯是根據爬蟲結果獲取指定畫廊標題，並以該標題作為保存的資料夾之名稱。而畫廊的標題中可能會出現不合法的資料夾字元(如`<>:"/\|?`，這些字元會導致資料夾命名失敗。因此會先將標題中的這些字元替換成`_`後，才將其作為資料夾的名稱作保存。

#### 在執行下載操作時，介面無法切換
由於下載的操作耗時且會占用當前的主執行緒，導致介面卡住。因此利用新增執行緒的方式，將下載的操作移至子執行緒，以解決在下載時無法切換 GUI 介面的問題。

#### 下載畫廊時，解析出來的網址可能會有重複副檔名的問題
這邊在嘗試下載[此畫廊(18禁)](https://nhentai.net/g/539127/)時，有一個頁面解析出來會出現`.webp.webp`的後綴，這邊簡單使用正規表達式將重複的`.webp`去除。

#### 批量下載
一開始程式的功能只有"單檔下載"，而為了提高程式的重用性，因此將下載的邏輯獨立出一個"下載方法"(由於邏輯問題，無法直接讓批量下載套用原先單檔下載的邏輯)，並且再區分成"單檔下載"以及"批量下載方法，這兩個方法透過調用"下載方法"的方式實現不同的下載邏輯。

## 附註

### 參考文獻

[流程圖 (Flowchart) 的基本圖示介紹、範例與實際應用](https://useme.medium.com/%E6%B5%81%E7%A8%8B%E5%9C%96%E7%9A%84%E5%9F%BA%E6%9C%AC%E5%9C%96%E7%A4%BA%E4%BB%8B%E7%B4%B9-%E7%AF%84%E4%BE%8B%E8%88%87%E5%AF%A6%E9%9A%9B%E6%87%89%E7%94%A8-e08be3ed8ae2)

[【流程圖製作教學】流程圖符號規範+圖示說明 | Flow Chart範例](https://projectmanager.com.tw/%E5%B0%88%E6%A1%88%E7%AE%A1%E7%90%86/%E6%B5%81%E7%A8%8B%E5%9C%96-%E6%B5%81%E7%A8%8B%E5%9C%96%E8%A3%BD%E4%BD%9C-flow-chart/)

[09.SQL語法簡介](https://hackmd.io/@peterju/B1LJp5WOh)

[12.正規表示式](https://hackmd.io/@peterju/Hycfbj-O3)

[Tkinter 套件](https://hackmd.io/@peterju/SJoPn4_HT)

[虛擬環境](https://hackmd.io/@peterju/rJah0QLra)

[request 模組](https://hackmd.io/@peterju/SkLpQ3-D6)

[BeautifulSoup4 套件](https://hackmd.io/@peterju/HJUIRhLva)

https://github.com/uwuok/hw3

[chatGPT](https://chatgpt.com/)

