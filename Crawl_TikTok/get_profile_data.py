from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time

starttime = time.time()

# Read links from file
with open("links.txt", "r", encoding="utf-8") as file:
    links = [line.strip() for line in file.readlines()]

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

data_file_name = "profile_data.json"
datas = []

# Initialize WebDriver once
driver = webdriver.Chrome(options=chrome_options)


def get_information(url):
    try:
        driver.get(url)

        # Use explicit wait instead of fixed sleep
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "script"))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        script_tag = soup.find('script', id='__UNIVERSAL_DATA_FOR_REHYDRATION__')

        if script_tag:
            json_data = json.loads(script_tag.string)
            user_info = json_data.get('__DEFAULT_SCOPE__', {}).get('webapp.user-detail', {}).get('userInfo', {})

            if user_info:
                # videos = []
                # for video_div in soup.select("div[data-e2e='user-post-item']"):
                #     video = {
                #         "video_id": video_div.get("data-video-id"),
                #         "caption": video_div.select_one(
                #             "div[data-e2e='video-title']").text.strip() if video_div.select_one(
                #             "div[data-e2e='video-title']") else None,
                #         "likes": video_div.select_one(
                #             "strong[data-e2e='video-views']").text.strip() if video_div.select_one(
                #             "strong[data-e2e='video-views']") else None,
                #         "url": f"https://www.tiktok.com/@{user_info['user']['uniqueId']}/video/{video_div.get('data-video-id')}"
                #     }
                #     videos.append(video)
                # user_info["videos"] = videos
                # print(user_info['user']['nickname'])
                datas.append(user_info)
                return
        print(f"No data found: {url}")

    except Exception as e:
        print(f"Error processing {url}: {str(e)}")


# Process all URLs
for url in links:
    get_information(url)

# Close driver after processing all URLs
driver.quit()

# Write all data to JSON file once
if datas:
    with open(data_file_name, "w", encoding="utf-8") as file:
        json.dump(datas, file, indent=4, ensure_ascii=False)
    print(f"Data saved to {data_file_name}")
else:
    print("No data collected")

endtime = time.time()
print(f"Execution time: {endtime - starttime:.2f} seconds")
