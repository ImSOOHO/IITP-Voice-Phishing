import os, time, glob
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CHROMEDRIVER_PATH = r'C:\Users\ben76\Desktop\HLI 연구실\보이스피싱 연구\크롤링 코드\chromedriver.exe'
BASE_URL = "https://www.fss.or.kr"
LIST_URL_TMPL = BASE_URL + "/fss/bbs/B0000059/list.do?menuNo=200359&pageIndex={}&searchCnd=1&searchWrd="
DOWNLOAD_DIR = os.path.abspath("./attachments")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

opts = Options()
prefs = {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True,
}
opts.add_experimental_option("prefs", prefs)
opts.add_argument("--window-size=1920,1080")

def create_driver():
    return webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=opts)

def wait_for_downloads(folder):
    while any(f.endswith(".crdownload") for f in os.listdir(folder)):
        time.sleep(0.2)

def scrape_attachments():
    driver = create_driver()
    wait = WebDriverWait(driver, 10)
    try:
        for page in range(1, 10):
            driver.get(LIST_URL_TMPL.format(page))
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr")))
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

            for row in rows:
                cell5 = row.find_element(By.CSS_SELECTOR, "td:nth-child(5)")

                # 첨부파일 한개
                singles = cell5.find_elements(By.CSS_SELECTOR, "a.file-single[href*='fileDown.do']")
                singles = [a for a in singles if a.find_elements(By.CSS_SELECTOR, "i.ico-pdf, i.ico-hwp, i.ico-etc")]
                if singles:
                    for a in singles:
                        a.click()
                        wait_for_downloads(DOWNLOAD_DIR)
                    continue

                # 첨부파일 두개 이상
                try:
                    group_btn = cell5.find_element(By.CSS_SELECTOR, "button.file-group__ctrl")
                except:
                    continue

                group_btn.click()
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.file-group__set.active")))

                group_anchors = driver.find_elements(
                    By.CSS_SELECTOR,
                    "div.file-group__set.active a.file-group__set__item[href*='fileDown.do']"
                )
                for a in group_anchors:
                    if not a.find_elements(By.CSS_SELECTOR, "i.ico-pdf, i.ico-hwp, i.ico-etc"):
                        continue
                    a.click()
                    wait_for_downloads(DOWNLOAD_DIR)

                driver.find_element(By.CSS_SELECTOR, "div.file-group__set.active button.close").click()
                time.sleep(0.2)

    finally:
        driver.quit()
        print("크롤링 완료", DOWNLOAD_DIR)

if __name__ == "__main__":
    scrape_attachments()
