# 我要全部

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

2. [Playwright](https://playwright.dev/python/docs/intro) 安裝特定瀏覽器

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

```
PORTAL_ACCOUNT=你的Portal帳號
PORTAL_PASSWORD=你的Portal密碼
```

執行程式:

```bash
python iwantitall.py
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
