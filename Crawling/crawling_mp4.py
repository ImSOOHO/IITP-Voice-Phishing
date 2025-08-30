import os
import time
import requests
import hashlib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 환경 설정
CHROME_PATH = '크롬드라이버 경로'
BASE_URL    = "https://www.fss.or.kr"
LIST_URL    = (
    BASE_URL +
    "/fss/bbs/B0000203/list.do?"
    "menuNo=200686&bbsId=&cl1Cd=&pageIndex={}&"
    "sdate=&edate=&searchCnd=1&searchWrd="
)
VIDEO_DIR   = './videos'
os.makedirs(VIDEO_DIR, exist_ok=True)

# 드라이버
def create_driver():
    opts = Options()
    opts.add_argument('--window-size=1920,1080')
    return webdriver.Chrome(service=Service(CHROME_PATH), options=opts)

# 파일 다운로드 헬퍼 
def download_file(url, out_path):
    if os.path.exists(out_path):
        print(f"이미 존재: {out_path}")
        return
    print(f" 다운로드: {url}")
    resp = requests.get(url, stream=True)
    with open(out_path, 'wb') as f:
        for chunk in resp.iter_content(1024*1024):
            f.write(chunk)
    print(f"저장: {out_path}")

# 단일 페이지 크롤링 함수
def crawl_page(driver, wait, page_index, counter):
    page_url = LIST_URL.format(page_index)
    driver.get(page_url)
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "div.bd-list-thumb-a ul li a")))
    time.sleep(1)

    print(f"\크롤링 페이지: {page_index}")
    elems = driver.find_elements(By.CSS_SELECTOR, "div.bd-list-thumb-a ul li a")
    hrefs = [e.get_attribute("href") for e in elems]

    for href in hrefs:
        counter += 1
        seq = f"{counter:02d}"

        # 상세페이지 로드
        driver.get(href)
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "dl.inline")))

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 등록일 추출
        date = 'unknown'
        dl = soup.select_one("dl.inline")
        if dl:
            for dt, dd in zip(dl.select("dt"), dl.select("dd")):
                if dt.text.strip() == '등록일':
                    date = dd.text.strip().replace('-', '')
                    break

        # MP4 링크 추출
        mp4 = None
        span = soup.select_one("span.file-name")
        if span:
            a_tag = span.find_parent("a", href=True)
            if a_tag:
                mp4 = BASE_URL + a_tag['href']

        if not mp4:
            print(f"[{page_index}-{seq}] MP4 링크 없음")
            continue

        # 다운로드
        filename = f"{date}_{seq}.mp4"
        out_path = os.path.join(VIDEO_DIR, filename)
        print(f"[{page_index}-{seq}] {date} → {mp4}")
        download_file(mp4, out_path)

        time.sleep(0.3)

    return counter

# 실행
def main():
    driver = create_driver()
    wait = WebDriverWait(driver, 10)

    counter = 0
    for page in range(1, 13):
        counter = crawl_page(driver, wait, page, counter)

    driver.quit()
    print(f"\n 전체 {counter}개 MP4 다운로드 완료")

if __name__ == "__main__":
    main()

