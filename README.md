# [國立中央大學微積分聯合教學網](https://united-cal.math.ncu.edu.tw/all_news/0)下載器

- [國立中央大學微積分聯合教學網下載器](#國立中央大學微積分聯合教學網下載器)
  - [前情提要](#前情提要)
  - [功能](#功能)
  - [安裝需求](#安裝需求)
  - [使用方式](#使用方式)
    - [設定環境變數](#設定環境變數)
    - [執行程式](#執行程式)
  - [檔案結構](#檔案結構)
  - [將課程大綱轉成 iCal 格式 (`.ics`) 匯入 Google Calendar](#將課程大綱轉成-ical-格式-ics-匯入-google-calendar)

> [我要 Shampoo](https://youtube.com/shorts/DGN4mt562is?si=BN91p1uyCNs9r3wv)

此專案因應網站結構修改，最後更新於 2025/02/20 ，跟 [o3‑mini‑high](https://openai.com/index/openai-o3-mini/) 嘴砲出來的。

## 前情提要

- 若下載失敗可能是因為網站結構有所變動，請檢查網站結構是否有變動，並修改程式碼。
- 為避免違反國立中央大學微積分聯合教學網相關規定，本專案不提供下載後的檔案，須請使用者運行程式自行下載。
- 需要有效的中央大學 Portal 帳號

## 功能

- 自動填入中央大學 Portal 帳號密碼，請先設定有效的中央大學 Portal 帳號，並手動通過登入驗證。
- 預設下載「**歷年所有會考題目**」，依照會考次數分類儲存，檔名格式: `<年度>年第<學期>學期第<次數>次會考.pdf`。
- 列印「**建議習題列表**」 PDF 檔案以及「**偶數題解答連結列表**」文字檔案
- 額外功能: [將課程大綱轉成 iCal 格式 (`.ics`) 匯入 Google Calendar](#將課程大綱轉成-ical-格式-ics-匯入-google-calendar)

## 安裝需求

(Optional) 若要使用虛擬環境可以下載 [Conda](https://anaconda.org/anaconda/conda) 並執行以下指令

```bash
conda create -n iwantitall python=3.11
conda activate iwantitall
```

1. 安裝所需套件

   ```bash
   pip install selenium requests beautifulsoup4 python-dotenv tqdm playwright
   ```

<!-- 2. 安裝 [ChromeDriver](https://sites.google.com/chromium.org/driver/) (需與 Chrome 版本相符)，最新穩定版可前往 [此處](https://googlechromelabs.github.io/chrome-for-testing/#stable) 下載 -->

2. 為 [Playwright](https://playwright.dev/python/docs/intro) 安裝特定瀏覽器

   ```bash
   # 只安裝 Chromium，若要列印建議習題列表請使用此指令
   playwright install chromium

   # 只安裝 Firefox
   playwright install firefox

   # 只安裝 WebKit (Safari)
   playwright install webkit
   ```

## 使用方式

### 設定環境變數

首先建立 `.env` 檔案

```bash
cp .env.example .env
```

於 `env` 設定以下環境變數

```plaintext
PORTAL_ACCOUNT=<Portal 帳號>
PORTAL_PASSWORD=<Portal 密碼>
RESOURCE_TYPE=管理學院 # 理地工電生
BROWSER=chromium　# chromium, firefox, webkit
```

例如

```plaintext
PORTAL_ACCOUNT=fakeaccount
PORTAL_PASSWORD=fakepassword
RESOURCE_TYPE=管理學院
BROWSER=chromium
```

### 執行程式

```bash
python iwantitall.py
```

> [!TIP]
> 此專案未處理 [reCAPTCHA 驗證](https://www.google.com/recaptcha/about/)，系統自動填入帳號密碼後請手動登入，若遇到驗證請手動勾選「**我不是機器人**」並通過驗證登入，登入後系統於運行腳本之 Console 按 Enter 繼續。

系統會開啟瀏覽器並自動填入帳號密碼，請手動提交登入表單

```bash
$ python iwantitall.py
2025-02-20 23:25:39,350 - INFO - 下載目錄: 管理學院\exams
2025-02-20 23:25:39,351 - INFO - 最大重試次數: 3
2025-02-20 23:25:39,351 - INFO - 逾時時間: 30 秒
2025-02-20 23:25:39,351 - INFO - 建議習題頁面: https://united-cal.math.ncu.edu.tw/files/science/advice/管理學院/0
2025-02-20 23:25:39,351 - INFO - 試題頁面: https://united-cal.math.ncu.edu.tw/files/science/history/管理學院
2025-02-20 23:26:02,564 - INFO - 已自動填入帳號與密碼，請在瀏覽器中手動提交登入表單...
請按 Enter 鍵繼續，確認已完成登入：
```

**完成登入後於 Console 按 Enter 鍵繼續，便會開始下載**

```bash
2025-02-20 23:26:09,068 - INFO - 造訪建議習題頁面: https://united-cal.math.ncu.edu.tw/files/science/advice/管理學院/0
2025-02-20 23:26:10,881 - INFO - 已儲存建議習題列表 PDF 至: 管理學院\suggested-exercises\question_list.pdf
2025-02-20 23:26:10,971 - INFO - 找到 13 筆建議習題資料。
2025-02-20 23:26:10,972 - INFO - 已輸出建議習題連結表格至: 管理學院\suggested-exercises\answers_links.txt
下載頁面 0 的檔案:   0%|                                                                                                                                                                                     | 0/24 [00:00<?, ?it/s]2025-02-20 23:26:11,095 - INFO - 已下載: 管理學院\exams\1\questions\113年第1學期第1次會考.pdf
2025-02-20 23:26:11,209 - INFO - 已下載: 管理學院\exams\3\answers\113年第1學期第3次會考解答.pdf
2025-02-20 23:26:11,230 - INFO - 已下載: 管理學院\exams\2\questions\113年第1學期第2次會考.pdf
2025-02-20 23:26:11,234 - INFO - 已下載: 管理學院\exams\1\answers\113年第1學期第1次會考解答.pdf
下載頁面 0 的檔案:   8%|██████████████▍                                                                                                                                                              | 2/24 [00:00<00:02, 10.92it/s]2025-02-20 23:26:11,247 - INFO - 已下載: 管理學院\exams\1\questions\112年第1學期第1次會考.pdf
2025-02-20 23:26:11,255 - INFO - 已下載: 管理學院\exams\3\questions\113年第1學期第3次會考.pdf
2025-02-20 23:26:11,297 - INFO - 已下載: 管理學院\exams\2\questions\112年第1學期第2次會考.pdf
2025-02-20 23:26:11,320 - INFO - 已下載: 管理學院\exams\2\answers\112年第1學期第2次會考解答.pdf
2025-02-20 23:26:11,384 - INFO - 已下載: 管理學院\exams\2\answers\113年第1學期第2次會考解答.pdf
下載頁面 0 的檔案:  17%|
```

## 檔案結構

```bash
.
|-- LICENSE
|-- README.md
|-- download.log                                   # 下載紀錄
|-- iwantitall.py                                  # 主程式
|-- .env.example
|-- .env                                           # 環境變數
`-- 理地工電生
    |-- exams
    |   |-- 1                                      # 第 1 次會考
    |   |   |-- answers                            # 解答
    |   |   |   |-- 104年第1學期第1次會考.pdf   
    |   |   |   `-- ...
    |   |   `-- questions                          # 題目
    |   |       |-- 104年第1學期第1次會考解答.pdf
    |   |       `-- ...
    |   |-- 2                                      # 第 2 次會考
    |   |   |-- answers
    |   |   `-- questions
    |   |-- ...                                    # 第 3, 4, 5 次會考
    |   `-- 6                                      # 第 6 次會考
    |       |-- answers
    |       `-- questions
    `-- suggested-exercises                        # 建議習題
        |-- answers_links.txt                      # 解答連結
        `-- question_list.pdf                      # 題目列表
```

## 將課程大綱轉成 iCal 格式 (`.ics`) 匯入 Google Calendar

將「以下內容」、「授課大綱 PDF」，並指定「一三」或「二四」貼給 LLM。測試過 gpt-4o 可正確輸出。

```python
You are given the following semester schedule, which includes quiz dates and three “會考” exam dates. The user will specify whether the class is 「一三」 (meeting on Monday and Wednesday) or 「二四」 (meeting on Tuesday and Thursday).  
 
1. If the user says 「一三」, list all quiz dates that fall on Monday or Wednesday.  
2. If the user says 「二四」, list all quiz dates that fall on Tuesday or Thursday.  
3. For each quiz, output the line as Quiz#: MM/DD.  
4. Also list the three “會考” dates (midterm/final exams) as 會考: MM/DD.  
5. Make sure each quiz and 會考 is on its own line in the exact format Quiz#: MM/DD or 會考: MM/DD.  
 
Here is the schedule excerpt (example):  
- **Quiz1**: 03/05 (Mon)  
- **Quiz2**: 03/12 (Mon)  
- **Quiz3**: 03/19 (Mon)  
- **Quiz4**: 03/26 (Mon)  
- **Quiz5**: 04/02 (Mon)  
- **Quiz6**: 04/09 (Mon)  
- “會考” dates: 03/25, 04/29, 05/27  
 
Based on the user’s choice of 「一三」 or 「二四」, produce your final output **only** in lines of the form: 

Quiz1: 03/05
Quiz2: 03/12
會考: 03/25
Quiz3: 03/19
Quiz4: 03/26
會考: 04/29
Quiz5: 04/02
Quiz6: 04/09
會考: 05/27

No extra explanations. No additional formatting.  
```

將 LLM 輸出取代 [llm_output.txt](./llm_output.txt) 內容，並執行以下指令

```bash
python ics_converter.py
```

將會產生 `schedule.ics` 檔案，可匯入 Google Calendar，可參考 [calendar_examples](./calendar_examples/) 裡面的檔案。

> [!TIP] 注意
> 匯入後無法一鍵撤銷，請事先檢查日期是否正確，或是新建日曆確認。其他日曆 → 新建日曆 → 匯入。
