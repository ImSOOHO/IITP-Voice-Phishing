import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_driver():
    opts = Options()
    # opts.add_argument("--headless")
    opts.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=opts)

def get_no_attach_urls(driver, wait, max_pages=9):
    urls = []
    for page in range(1, max_pages+1):
        driver.get(LIST_URL_TMPL.format(page))
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr")))
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        for row in rows:
            # 그룹 첨부 스킵
            if row.find_elements(By.CSS_SELECTOR, "td:nth-child(5) button.file-group__ctrl"):
                continue
            # pdf/hwp 아이콘 스킵
            skip = False
            for a in row.find_elements(By.CSS_SELECTOR, "td:nth-child(5) a.file-single"):
                if any(ic in a.find_element(By.TAG_NAME,"i").get_attribute("class")
                       for ic in ("ico-pdf","ico-hwp")):
                    skip = True; break
            if skip: continue

            a = row.find_element(By.CSS_SELECTOR, "td.title > a")
            href = a.get_attribute("href")
            full_url = href if href.startswith("http") else BASE_URL + href
            urls.append(full_url)
    return urls

def scrape_body(driver, wait, url):
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.bd-view")))
    body = driver.find_element(By.CSS_SELECTOR, "div.bd-view > div.dbdata").text.strip()
    date_el = driver.find_element(By.CSS_SELECTOR,
        "dl.type-dt-length-3 > dt:nth-of-type(2) + dd")
    dept_el = driver.find_element(By.CSS_SELECTOR,
        "div.bd-view > dl:nth-of-type(3) > dt + dd")
    return body, {
        "date":   int(date_el.text.strip().replace("-", "")),
        "source": dept_el.text.strip()
    }

def main():
    driver = create_driver()
    wait = WebDriverWait(driver, 10)

    print("no-attachment 텍스트 게시글 URL 수집 중...")
    urls = get_no_attach_urls(driver, wait)
    print(f"수집된 게시글 수: {len(urls)}")

    merged = []
    for idx, url in enumerate(urls, start=1):
        text, meta = scrape_body(driver, wait, url)
        uid = f"text_{idx:03d}_{meta['date']}"
        merged.append({
            "id":        uid,
            "text":      text,
            "type":      "scenario",
            "meta":      meta,
            "embedding": []
        })
        print(f"[{idx:03d}] {uid} 준비 완료")
        time.sleep(0.3)

    driver.quit()

    with open(MERGED_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print("모든 게시글 저장 완료 →", MERGED_JSON_PATH)

if __name__ == "__main__":
    main()

