# from bs4 import BeautifulSoup
# import requests
#
# # Giả sử URL của user TikTok
# url = 'https://www.tiktok.com/@ttruc.__'
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
# }
#
# response = requests.get(url, headers=headers)
# response.
# soup = BeautifulSoup(response.text, 'html5lib')
#
# # Tìm các div chứa class "DivVideoFeedV2"
# divs = soup.select('div[class*="DivItemContainerV2 "]')
#
# print(soup)