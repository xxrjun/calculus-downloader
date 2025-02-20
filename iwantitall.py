# pip install selenium requests beautifulsoup4 python-dotenv tqdm playwright
# (並執行 "playwright install" 安裝瀏覽器執行檔)
import os
import re
import time
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Optional
from playwright.sync_api import sync_playwright

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('download.log')
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

@dataclass
class ExamFile:
    year: str
    semester: str
    exam_num: str
    is_answer: bool
    url: str

    @property
    def filename(self) -> str:
        return f"{self.year}年第{self.semester}學期第{self.exam_num}次會考{'解答' if self.is_answer else ''}.pdf"

    @property
    def subdir(self) -> str:
        return "answers" if self.is_answer else "questions"

class ExamDownloader:
    def __init__(self, exam_base_url: str, suggested_exercises_url: str, max_retries: int = 3, timeout: int = 30):
        self.exam_base_url = exam_base_url
        self.suggested_exercises_url = suggested_exercises_url
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = self._init_session()
        # 建立目錄結構：<RESOURCE_TYPE>/exams 與 <RESOURCE_TYPE>/suggested-exercises
        self.base_dir = self._create_directory_structure()
        self.auth_cookies = []  # 用於儲存 Playwright 登入後的完整 cookie 資訊
        
        # 顯示下載資訊
        logger.info(f"下載目錄: {self.base_dir}")
        logger.info(f"最大重試次數: {self.max_retries}")
        logger.info(f"逾時時間: {self.timeout} 秒")
        logger.info(f"建議習題頁面: {self.suggested_exercises_url}")
        logger.info(f"試題頁面: {self.exam_base_url}")

    def _launch_browser(self, p, headless: bool):
        """
        根據環境變數 BROWSER (chromium / firefox / webkit) 來選擇瀏覽器引擎
        """
        browser_type = os.getenv("BROWSER", "chromium").lower()
        if browser_type == "chromium":
            return p.chromium.launch(headless=headless)
        elif browser_type == "firefox":
            return p.firefox.launch(headless=headless)
        elif browser_type == "webkit":
            return p.webkit.launch(headless=headless)
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")

    def _login(self) -> None:
        """使用 Playwright 進行登入 (自動填入帳號密碼後等待使用者自行提交表單)"""
        with sync_playwright() as p:
            browser = self._launch_browser(p, headless=False)
            page = browser.new_page()
            try:
                page.goto("https://united-cal.math.ncu.edu.tw/login")
                page.click("text=中央Portal登入")
                # 自動填入帳號與密碼
                page.fill("input[name='username']", os.getenv("PORTAL_ACCOUNT"))
                page.fill("input[name='password']", os.getenv("PORTAL_PASSWORD"))
                logger.info("已自動填入帳號與密碼，請在瀏覽器中手動提交登入表單...")
                input("請按 Enter 鍵繼續，確認已完成登入：")
                page.wait_for_load_state("networkidle")
                # 取得完整的 cookie 資訊，供後續 Playwright 使用
                self.auth_cookies = page.context.cookies()
                # 同時設定 requests session 的 cookie (只設定 name 與 value)
                for cookie in self.auth_cookies:
                    self.session.cookies.set(cookie["name"], cookie["value"])
            finally:
                browser.close()

    @staticmethod
    def _init_session() -> requests.Session:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })
        return session

    def _create_directory_structure(self) -> Path:
        resource = os.getenv("RESOURCE_TYPE", "理地工電生")
        exam_base_dir = Path(resource) / "exams"
        for exam_num in range(1, 7):
            for subdir in ["questions", "answers"]:
                (exam_base_dir / str(exam_num) / subdir).mkdir(parents=True, exist_ok=True)
        suggested_dir = Path(resource) / "suggested-exercises"
        suggested_dir.mkdir(parents=True, exist_ok=True)
        self.suggested_dir = suggested_dir
        return exam_base_dir

    def _parse_exam_file(self, filename: str, url: str, force_answer: Optional[bool] = None) -> Optional[ExamFile]:
        """
        解析歷屆試題檔案資訊
        若 force_answer 非 None，則覆蓋是否為解答檔的判斷
        """
        pattern = r"(\d+)年第(\d+)學期第(\d+)次會考"
        match = re.match(pattern, filename)
        if match and "會考" in filename:
            year, semester, exam_num = match.groups()
            is_answer = force_answer if force_answer is not None else ("解答" in filename)
            full_url = f"https://united-cal.math.ncu.edu.tw{url}" if not url.startswith("http") else url
            return ExamFile(year, semester, exam_num, is_answer, full_url.split('#')[0])
        return None

    def _download_file(self, exam_file: ExamFile) -> None:
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
                time.sleep(2 ** attempt)

    def process_page(self, page_num: int) -> None:
        url = f"{self.exam_base_url}/{page_num}"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            exam_files = []
            # 根據新版 HTML 格式，從 tbody.row-hover 中的每個 tr 解析資料
            for row in soup.select("tbody.row-hover tr"):
                cells = row.find_all("td")
                if len(cells) < 3:
                    continue
                exam_title = cells[0].text.strip()
                question_link_tag = cells[1].find('a')
                answer_link_tag = cells[2].find('a')
                if question_link_tag and answer_link_tag and "會考" in exam_title:
                    exam_file_q = self._parse_exam_file(exam_title, question_link_tag.get('href'), force_answer=False)
                    exam_file_a = self._parse_exam_file(exam_title, answer_link_tag.get('href'), force_answer=True)
                    if exam_file_q:
                        exam_files.append(exam_file_q)
                    if exam_file_a:
                        exam_files.append(exam_file_a)
            with ThreadPoolExecutor(max_workers=5) as executor:
                list(tqdm(
                    executor.map(self._download_file, exam_files),
                    total=len(exam_files),
                    desc=f"下載頁面 {page_num} 的檔案"
                ))
        except Exception as e:
            logger.error(f"處理頁面失敗 {url}: {str(e)}")

    def download_suggested_exercises(self) -> None:
        """
        1. 使用 Playwright 造訪需登入的建議習題頁面，列印成 PDF 存至 <RESOURCE_TYPE>/suggested-exercises/question_list.pdf。
        2. 解析頁面，找出標題為「建議習題偶數題解答」下的 table，
           並依該 table 的「章節」與「檔案」欄位輸出對應的連結表格至
           <RESOURCE_TYPE>/suggested-exercises/answers_links.txt
        """
        resource = os.getenv("RESOURCE_TYPE", "理地工電生")
        pdf_path = Path(resource) / "suggested-exercises" / "question_list.pdf"

        with sync_playwright() as p:
            browser = self._launch_browser(p, headless=True)
            # 將 auth_cookies 轉換成 Playwright 格式後加入 context
            cookies_list = []
            for cookie in self.auth_cookies:
                cookies_list.append({
                    "name": cookie["name"],
                    "value": cookie["value"],
                    "domain": cookie["domain"],
                    "path": cookie["path"],
                    "expires": cookie.get("expires", -1),
                    "httpOnly": cookie.get("httpOnly", False),
                    "secure": cookie.get("secure", False),
                    "sameSite": cookie.get("sameSite", "Lax"),
                })
            context = browser.new_context()
            context.add_cookies(cookies_list)
            page = context.new_page()
            logger.info(f"造訪建議習題頁面: {self.suggested_exercises_url}")
            page.goto(self.suggested_exercises_url)
            page.wait_for_load_state("networkidle")
            page.pdf(path=str(pdf_path))
            logger.info(f"已儲存建議習題列表 PDF 至: {pdf_path}")
            content = page.content()
            browser.close()

        # 解析 HTML 中「建議習題偶數題解答」的 table
        soup = BeautifulSoup(content, 'html.parser')
        heading = soup.find('h4', string=lambda t: t and "建議習題偶數題解答" in t)
        rows = []
        if heading:
            table = heading.find_next('table')
            if table:
                rows = table.select("tbody tr")
        logger.info(f"找到 {len(rows)} 筆建議習題資料。")

        answers_links_file = Path(resource) / "suggested-exercises" / "answers_links.txt"
        with open(answers_links_file, 'w', encoding='utf-8') as f:
            f.write("章節\t檔案\n")
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    chapter = cells[0].get_text(strip=True)
                    link_tag = cells[1].find('a')
                    if link_tag and link_tag.has_attr('href'):
                        link = link_tag['href']
                        f.write(f"{chapter}\t{link}\n")
        logger.info(f"已輸出建議習題連結表格至: {answers_links_file}")

    def run(self) -> None:
        """
        整合執行流程：
        1. 登入
        2. (選擇性) 下載建議習題（或輸出建議習題連結表格）
        3. 處理試題頁面下載
        """
        try:
            self._login()
            try:
                self.download_suggested_exercises()
            except Exception as e:
                logger.error(f"下載建議習題失敗: {str(e)}，將繼續處理試題頁面。")
            for page in range(6):
                self.process_page(page)
        except Exception as e:
            logger.error(f"程式執行失敗: {str(e)}")

def main():
    resource = os.getenv("RESOURCE_TYPE", "理地工電生")
    if resource == "管理學院":
        exam_base_url = "https://united-cal.math.ncu.edu.tw/files/science/history/管理學院"
        suggested_exercises_url = "https://united-cal.math.ncu.edu.tw/files/science/advice/管理學院/0"
    else:
        exam_base_url = "https://united-cal.math.ncu.edu.tw/files/science/history/理地工電生"
        suggested_exercises_url = "https://united-cal.math.ncu.edu.tw/files/science/advice/理地工電生/0"
    downloader = ExamDownloader(exam_base_url=exam_base_url, suggested_exercises_url=suggested_exercises_url)
    downloader.run()

if __name__ == "__main__":
    main()
