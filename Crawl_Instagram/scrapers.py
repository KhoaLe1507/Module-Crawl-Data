import json
import httpx
import jmespath
import os
import time
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Khởi tạo client dùng httpx với header mặc định
client = httpx.Client(
    headers={
        "x-ig-app-id": "936619743392459",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
    }
)

#httpx (JSON API)
def scrape_user(username: str):
    result = client.get(
        f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
    )
    data = json.loads(result.content)
    return data["data"]["user"]

#requests với JSON API
def scrape_user_requests(username: str):
    headers = {
        "x-ig-app-id": "936619743392459",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
    }
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["data"]["user"]

#BeautifulSoup
def scrape_user_html_requests(username: str):
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    data_script = soup.find("script", text=lambda t: t and "profile_pic_url_hd" in t)
    if not data_script:
        raise ValueError("Không tìm thấy dữ liệu trong HTML.")
    text_content = data_script.string
    json_str = text_content.split('window._sharedData = ')[-1].rstrip(';')
    raw_data = json.loads(json_str)
    user_info = raw_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]
    return user_info

#Selenium
def scrape_user_selenium(username: str):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    url = f"https://www.instagram.com/{username}/"
    driver.get(url)
    time.sleep(5)
    
    page_source = driver.page_source
    driver.quit()
    
    soup = BeautifulSoup(page_source, 'html.parser')
    data_script = soup.find("script", text=lambda t: t and "profile_pic_url_hd" in t)
    if not data_script:
        raise ValueError("Không tìm thấy dữ liệu trong HTML.")
    text_content = data_script.string
    json_str = text_content.split('window._sharedData = ')[-1].rstrip(';')
    raw_data = json.loads(json_str)
    user_info = raw_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]
    return user_info

def scrape_user_fallback(username: str):
    """Thử các cách cào dữ liệu khác nhau cho đến khi thành công"""
    try:
        return scrape_user(username)
    except Exception:
        print("[Fallback] httpx bị chặn hoặc lỗi, thử requests JSON API...")
    
    try:
        return scrape_user_requests(username)
    except Exception:
        print("[Fallback] requests JSON API bị chặn, thử requests parse HTML...")
    
    try:
        return scrape_user_html_requests(username)
    except Exception:
        print("[Fallback] requests parse HTML bị chặn, thử Selenium...")
    
    try:
        return scrape_user_selenium(username)
    except Exception:
        print("[Fallback] Selenium cũng bị chặn.")
        raise 

def parse_user(data: dict) -> dict:
    result = jmespath.search(
        """{
            name: full_name,
            username: username,
            id: id,
            category: category_name,
            email: business_email,
            mobile: business_phone_number,
            address: business_address_json,
            website: external_url,
            tiktok: bio_links[?contains(@.url, 'tiktok')].url,
            bio: biography,
            bio_links: bio_links[].url,
            homepage: external_url,
            followers: edge_followed_by.count,
            follows: edge_follow.count,
            facebook_id: fbid,
            is_private: is_private,
            is_verified: is_verified,
            profile_image: profile_pic_url_hd
        }""",
        data,
    )
    return result

def save_to_file(filename: str, data):
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
    with open(filename, "r", encoding="utf-8") as f:
        existing_data = json.load(f)
    
    existing_data.append(data)
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)
