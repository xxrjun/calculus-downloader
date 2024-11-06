# 我要全部

> [!TIP]
> 目前未處理 [reCAPTCHA 驗證](https://www.google.com/recaptcha/about/)，若遇到請手動勾選"我不是機器人"，系統會自動繼續執行。

## 功能

- 自動登入中央大學 Portal
- 下載所有會考題目與解答之 PDF 檔案
- 依照會考次數分類儲存

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
   # 只安裝 Chromium
   playwright install chromium

   # 只安裝 Firefox
   playwright install firefox

   # 只安裝 WebKit (Safari)
   playwright install webkit
   ```

## 使用方式

首先建立 `.env` 檔案

```bash
cp .env.example .env
```

於 `env` 設定以下環境變數

```plaintext
PORTAL_ACCOUNT=你的Portal帳號
PORTAL_PASSWORD=你的Portal密碼
```

執行程式:

```bash
python iwantitall.py
```

範例輸出

```bash
2024-11-06 14:30:16,689 - INFO - 已下載: exams\3\answer\111年第1學期第3次會考解答.pdf
2024-11-06 14:30:16,713 - INFO - 已下載: exams\6\answer\110年第2學期第6次會考解答.pdf
2024-11-06 14:30:16,717 - INFO - 已下載: exams\4\answer\111年第2學期第4次會考解答.pdf
2024-11-06 14:30:16,731 - INFO - 已下載: exams\5\answer\111年第2學期第5次會考解答.pdf
2024-11-06 14:30:16,744 - INFO - 已下載: exams\5\answer\110年第2學期第5次會考解答.pdf
下載頁面 4 的檔案:  55%|███████████████████████████████████▊                             | 11/20 [00:00<00:00, 63.19it/s]2024-11-06 14:30:16,749 - INFO - 已下載: exams\1\answer\112年第1學期第1次會考解答.pdf
2024-11-06 14:30:16,749 - INFO - 已下載: exams\6\answer\111年第2學期第6次會考解答.pdf
2024-11-06 14:30:16,752 - INFO - 已下載: exams\2\answer\111年第1學期第2次會考解答.pdf
2024-11-06 14:30:16,775 - INFO - 已下載: exams\2\answer\112年第1學期第2次會考解答.pdf
2024-11-06 14:30:19,633 - ERROR - 下載失敗 exams\1\answer\111年第1學期第1次會考解答.pdf: 404 Client Error: Not Found for url: https://united-cal.math.ncu.edu.tw/media/store/pdfs/1111exam1sol_tRnaXY5_fKKx0ls.pdf
下載頁面 4 的檔案: 100%|█████████████████████████████████████████████████████████████████| 20/20 [00:07<00:00,  2.83it/s] 
下載頁面 5 的檔案:   0%|                                                                           | 0/4 [00:00<?, ?it/s]2024-11-06 14:30:23,738 - INFO - 已下載: exams\3\answer\112年第1學期第3次會考解答.pdf
2024-11-06 14:30:23,769 - INFO - 已下載: exams\4\answer\112年第2學期第4次會考解答.pdf
2024-11-06 14:30:23,855 - INFO - 已下載: exams\4\question\112年第2學期第4次會考.pdf
下載頁面 5 的檔案:  25%|████████████████▊                                                  | 1/4 [00:00<00:00,  5.35it/s]2024-11-06 14:30:24,034 - INFO - 已下載: exams\1\answer\111年第1學期第1次會考解答.pdf
下載頁面 5 的檔案: 100%|███████████████████████████████████████████████████████████████████| 4/4 [00:00<00:00, 10.92it/s] 
```

## 檔案結構

```
exams/
├── 1/                              # 第1次會考
│   ├── question/                   # 題目
│   │   └── 104年第1學期第1次會考.pdf
│   └── answer/                     # 解答
│       └── 104年第1學期第1次會考解答.pdf
├── 2/                              # 第2次會考
│   ├── question/
│   └── answer/
...
└── 6/                              # 第6次會考
    ├── question/
    └── answer/
```

## 注意事項

- 需要有效的中央大學 Portal 帳號
- 預設下載歷年所有會考題目
- 檔名格式: `<年度>年第<學期>學期第<次數>次會考.pdf`
