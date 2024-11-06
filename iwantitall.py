# pip install selenium requests beautifulsoup4 python-dotenv tqdm
import os
import re
import time
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Optional, Tuple

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('download.log')
    ]
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

@dataclass
class ExamFile:
    """考試檔案資料結構"""
    year: str
    semester: str
    exam_num: str
    is_answer: bool
    url: str

    @property
    def filename(self) -> str:
        """生成檔案名稱"""
        return f"{self.year}年第{self.semester}學期第{self.exam_num}次會考{'解答' if self.is_answer else ''}.pdf"

    @property
    def subdir(self) -> str:
        """取得子目錄名稱"""
        return "answer" if self.is_answer else "question"

class ExamDownloader:
    """考試檔案下載器"""
    def __init__(self, base_url: str, max_retries: int = 3, timeout: int = 30):
        self.base_url = base_url
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = self._init_session()
        self.base_dir = self._create_directory_structure()

    @staticmethod
    def _init_session() -> requests.Session:
        """初始化 session"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })
        return session

    @staticmethod
    def _create_directory_structure() -> Path:
        """創建目錄結構"""
        base_dir = Path("exams")
        for exam_num in range(1, 7):
            for subdir in ["question", "answer"]:
                (base_dir / str(exam_num) / subdir).mkdir(parents=True, exist_ok=True)
        return base_dir

    def _login(self) -> None:
        """使用 Selenium 進行登入"""
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=options)

        try:
            driver.get("https://united-cal.math.ncu.edu.tw/login")
            
            # 點擊中央Portal登入按鈕
            portal_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '中央Portal登入')]"))
            )
            portal_btn.click()

            try:
                # 嘗試點擊確認按鈕
                proceed_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-danger[type='submit']"))
                )
                proceed_btn.click()
            except:
                # 需要登入
                self._handle_login(driver)

            # 獲取並設定 cookies
            for cookie in driver.get_cookies():
                self.session.cookies.set(cookie['name'], cookie['value'])

        finally:
            driver.quit()

    def _handle_login(self, driver: webdriver.Chrome) -> None:
        """處理登入流程"""
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_input = driver.find_element(By.NAME, "password")

        username_input.send_keys(os.getenv("PORTAL_ACCOUNT"))
        password_input.send_keys(os.getenv("PORTAL_PASSWORD"))
        password_input.submit()

        # 點擊確認按鈕
        proceed_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-danger[type='submit']"))
        )
        proceed_btn.click()
        time.sleep(5)

    def _parse_exam_file(self, filename: str, url: str) -> Optional[ExamFile]:
        """解析考試檔案資訊"""
        pattern = r"(\d+)年第(\d+)學期第(\d+)次會考"
        match = re.match(pattern, filename)
        if match and '會考' in filename:
            year, semester, exam_num = match.groups()
            is_answer = "解答" in filename
            full_url = f"https://united-cal.math.ncu.edu.tw{url}" if not url.startswith('http') else url
            return ExamFile(year, semester, exam_num, is_answer, full_url.split('#')[0])
        return None

    def _download_file(self, exam_file: ExamFile) -> None:
        """下載檔案"""
        filepath = self.base_dir / exam_file.exam_num / exam_file.subdir / exam_file.filename

        if filepath.exists():
            logger.info(f"檔案已存在: {filepath}")
            return

        for attempt in range(self.max_retries):
            try:
                response = self.session.get(exam_file.url, timeout=self.timeout)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                logger.info(f"已下載: {filepath}")
                return
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"下載失敗 {filepath}: {str(e)}")
                time.sleep(2 ** attempt)  # 指數退避

    def process_page(self, page_num: int) -> None:
        """處理單一頁面"""
        url = f"{self.base_url}/{page_num}"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            exam_files = []

            for row in soup.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    filename_cell = cells[0].text.strip()
                    link_cell = cells[1].find('a')
                    
                    if link_cell and '會考' in filename_cell:
                        exam_file = self._parse_exam_file(filename_cell, link_cell['href'])
                        if exam_file:
                            exam_files.append(exam_file)

            # 使用線程池同時下載檔案
            with ThreadPoolExecutor(max_workers=5) as executor:
                list(tqdm(
                    executor.map(self._download_file, exam_files),
                    total=len(exam_files),
                    desc=f"下載頁面 {page_num} 的檔案"
                ))

        except Exception as e:
            logger.error(f"處理頁面失敗 {url}: {str(e)}")

    def run(self) -> None:
        """執行下載任務"""
        try:
            self._login()
            for page in range(6):
                self.process_page(page)
        except Exception as e:
            logger.error(f"程式執行失敗: {str(e)}")

def main():
    downloader = ExamDownloader(
        base_url="https://united-cal.math.ncu.edu.tw/files/science/history/理地工電生"
    )
    downloader.run()

if __name__ == "__main__":
    main()