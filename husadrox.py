from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# --- Setup Chrome ---
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # run in background
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get("http://swcadastre.env.am/WaterIntakeDischarge.aspx")

wait = WebDriverWait(driver, 10)

# --- Initialize storage ---
all_rows = []
headers = []

MAX_PAGES = 99
page = 1

# --- Scraping loop ---
while page <= MAX_PAGES:
    print(f"Scraping page {page}...")

    # Wait for table
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "#RadGrid1 table.rgMasterTable")
    ))
    table = driver.find_element(By.CSS_SELECTOR, "#RadGrid1 table.rgMasterTable")

    # Get headers only once
    if not headers:
        headers = [th.text.strip() for th in table.find_elements(By.CSS_SELECTOR, "thead th")]

    # Get rows
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    for row in rows:
        cells = [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, "td")]
        # Pad missing cells if row is shorter than header
        while len(cells) < len(headers):
            cells.append("")
        if any(cells):
            all_rows.append(cells)

    # Try to click "Next" button
    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, "input.rgPageNext")
        # Check if button is disabled (last page)
        if "disabled" in next_btn.get_attribute("class").lower():
            break
        next_btn.click()
        page += 1
        time.sleep(2)  # wait for table to load
    except Exception as e:
        print("Reached last page or error:", e)
        break

driver.quit()

# --- Save CSV ---
df = pd.DataFrame(all_rows, columns=headers)
df.to_csv("Armenia_Water_Discharge.csv", index=False, encoding="utf-8-sig")
print(f"Scraped {len(df)} rows and {len(headers)} columns. CSV saved!")
