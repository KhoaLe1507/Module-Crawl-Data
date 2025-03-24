from concurrent.futures import ThreadPoolExecutor
from typing import List, override
from tqdm import tqdm
import queue
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import regex
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    NoSuchAttributeException,
)
from bs4 import BeautifulSoup, Tag

from web_scraper import WebScraper
from facebook_config import FacebookConfig, FacebookKOL, Xpaths
from log import Log
from facebook_handle_login import (
    handle_login_from_redirecting,
    handle_login_from_kol_page,
    handle_login_from_block_page,
    handle_login_from_main_page,
)
from fb_about_utils import (
    fb_about_categories,
    fb_about_contact_info,
    fb_about_website_and_social_links,
    fb_about_basic_info,
)


def conv_chrome_options(
    chrome_options: List[str], experimental_options: List[tuple]
) -> webdriver.ChromeOptions:
    result = webdriver.ChromeOptions()
    for option in chrome_options:
        result.add_argument(option)
    for option in experimental_options:
        result.add_experimental_option(*option)
    return result


class FacebookScraper(WebScraper):
    def __init__(self, config: FacebookConfig) -> None:
        super().__init__(config)
        self.driver_queue = queue.Queue()
        self.exceptional_driver_queue = queue.Queue()
        self.chrome_options = conv_chrome_options(
            config.chrome_options, config.experimental_options
        )
        self.config = config
        self.__is_logged_in = False

    def __start_drivers(self):
        try:
            for _ in range(self.config.n_workers):
                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=self.chrome_options,
                )
                self.driver_queue.put(driver)
            for _ in range(self.config.n_exceptional_workers):
                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=self.chrome_options,
                )
                self.exceptional_driver_queue.put(driver)
            Log.info("Started the drivers succesfully")
        except Exception as e:
            Log.info("Starting the drivers failed")
            Log.error("Error: ", e)

    @override
    def close(self) -> None:
        super().close()
        while not self.driver_queue.empty():
            self.driver_queue.get().quit()

    def __log_in_driver(self, driver) -> None:
        # If cannot login by this way, try another way
        try:
            return handle_login_from_redirecting(
                driver, driver.current_url, self.config
            )
        except NoSuchElementException:
            pass

        try:
            return handle_login_from_kol_page(driver, self.config)
        except NoSuchElementException:
            pass

        try:
            return handle_login_from_block_page(driver, self.config)
        except NoSuchElementException as e:
            Log.error(e.msg)

    @override
    def run(self, urls: List[str]) -> None:
        self.__start_drivers()
        # Multi-threading
        with ThreadPoolExecutor(max_workers=self.config.n_workers) as executor:
            for i, url in enumerate(urls):
                kol = FacebookKOL(i, url)
                self.result.append(kol)

            # Scrape the information that not need to login
            if self.config.is_scraping_general_info:
                for url, kol in tqdm(zip(urls, self.result)):
                    executor.submit(self.__scrape_url, url, kol)

            # Login for each driver
            if self.config.is_scraping_about_tab or self.config.is_scraping_posts:
                for _ in range(self.config.n_workers):
                    driver = self.driver_queue.get()
                    driver.get(driver.current_url)
                    self.__log_in_driver(driver)
                    self.driver_queue.put(driver)

            # Scrape the about tab
            if self.config.is_scraping_about_tab:
                for url, kol in tqdm(zip(urls, self.result)):
                    executor.submit(self.__scrape_about_tab, url, kol)

    def __scrape_general_url(self, driver: webdriver.Chrome, kol: FacebookKOL) -> None:
        try:
            # Waiting for page loaded
            time.sleep(4)

            """Head Part"""
            # Get metadata if can access the page without login
            meta_data_element = driver.find_elements(By.XPATH, Xpaths.meta_data_element)
            if meta_data_element:
                try:
                    content = meta_data_element[0].get_attribute("content")
                    pattern = r"[\d,]+(?:\.\d+)?\s+(?:likes|talking about)"
                    if content:
                        matches = regex.findall(pattern, content)

                        if len(matches) > 0:
                            likes_content = matches[0].strip().split()  # Get likes
                            talking_about_content = (
                                matches[1].strip().split()
                            )  # Get talking about

                            # kol[likes_content[1]] = likes_content[0]
                            kol.likesCount = likes_content[0]
                            kol.talkingAbout = talking_about_content[0]

                            Log.info(1, f"Likes: {likes_content[0]}")
                            Log.info(1, f"Talking about: {talking_about_content[0]}")

                except NoSuchAttributeException as e:
                    Log.error(e.msg)

            """Body Part 1"""
            # Get the avatar url
            try:
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                avt_element = soup.find("image")
                if isinstance(avt_element, Tag):
                    kol.avatarUrl = avt_element.attrs["xlink:href"]  # Avatar link

                poster_element = soup.find(
                    "img", {"data-imgperflogname": "profileCoverPhoto"}
                )
                if isinstance(poster_element, Tag):
                    kol.profileAvatarUrl = poster_element.attrs[
                        "src"
                    ]  # Poster avatar link

                Log.info(1, f"Avatar URL: {kol.avatarUrl}")
                Log.info(1, f"Profile avatar URL: {kol.profileAvatarUrl}")

            except NoSuchElementException as e:
                Log.info(e.msg)

            # Get the page name
            beside_avt_container = None
            try:
                beside_avt_container = driver.find_element(
                    By.XPATH, Xpaths.beside_avt_container
                )
            except NoSuchElementException as e:
                Log.info(e.msg)

            try:
                if beside_avt_container:
                    page_name_element = beside_avt_container.find_element(
                        By.XPATH, Xpaths.page_name_element_path
                    )
                    kol.pageName = page_name_element.text

                    Log.info(1, f"Page name: {kol.pageName}")

            except NoSuchElementException as e:
                Log.info(e.msg)

            # Get likes, followers, followings
            if beside_avt_container:
                lff_element = beside_avt_container.find_elements(By.TAG_NAME, "a")
                for a_tag in lff_element:
                    a_content = a_tag.text.split()
                    kol[a_content[1]] = a_content[0]

                    Log.info(1, f"{a_content[1]}: {a_content[0]}")

            # Get intro description
            try:
                intro_element = driver.find_element(
                    By.XPATH, Xpaths.intro_description_element_path
                )
                kol["introDescription"] = intro_element.text

                Log.info(1, f"Intro description: {kol.introDescription}")

            except NoSuchElementException as e:
                Log.error(e.msg)

        except NoSuchElementException as e:
            Log.error("Element Error: ", e.msg)
        except Exception as e:
            Log.error(e)

    def __scrape_about_tab(self, url: str, kol: FacebookKOL) -> None:
        Log.info(f"Start scraping {kol.pageName}'s about tab.")
        driver = self.driver_queue.get()
        try:
            driver.get(url)
            about_tab_element = None
            try:
                about_tab_element = driver.find_element(
                    By.XPATH, Xpaths.about_tab_element_path
                )
                about_tab_element.click()
            except NoSuchElementException as e:
                Log.error(e.msg)
                return
            except ElementClickInterceptedException:
                if about_tab_element:
                    try:
                        about_tab_element.click()
                    except ElementClickInterceptedException as e:
                        Log.error(e.msg)
                        return

            time.sleep(5)

            contact_and_basic_info_elements = driver.find_elements(
                By.XPATH, Xpaths.contact_and_basic_info_elements_path
            )
            for j, contact_and_basic_info_element in enumerate(
                contact_and_basic_info_elements
            ):
                Log.info(j)
                try:
                    span_tag = contact_and_basic_info_element.find_element(
                        By.XPATH, "div/div[1]/div/h2/span"
                    )
                except NoSuchElementException as e:
                    Log.error(e.msg)
                    continue

                Log.info(span_tag.text.lower())
                match span_tag.text.lower():
                    case "categories":
                        fb_about_categories(contact_and_basic_info_element, kol)

                    case "contact info":
                        fb_about_contact_info(contact_and_basic_info_element, kol)

                    case "websites and social links":
                        fb_about_website_and_social_links(
                            contact_and_basic_info_element, kol
                        )

                    case "basic info":
                        fb_about_basic_info(contact_and_basic_info_element, kol)

            Log.info(f"Scrape the about tab of url {driver.current_url} successfully")

        except NoSuchElementException as e:
            Log.error(e.msg)
        except Exception as e:
            Log.error(e)
        finally:
            self.driver_queue.put(driver)

    def __scrape_url(self, url: str, kol: FacebookKOL) -> None:
        driver = self.driver_queue.get()  # Lấy driver từ hàng đợi
        try:
            Log.info(f"Start scraping general information from {url}")

            # Navigate to the page
            driver.get(url)

            time.sleep(1)

            # Find the login table in center
            close_button = None
            try:
                close_button = driver.find_element(By.XPATH, Xpaths.close_button_path)
                close_button.click()  # Click to close the table
            except NoSuchElementException:
                raise NoSuchElementException("Login de")
            except ElementClickInterceptedException:
                time.sleep(3)
                try:
                    if close_button:
                        close_button.click()  # Try to click to close the table again
                except ElementClickInterceptedException:
                    raise ElementClickInterceptedException("Cannot close the table")

            self.__scrape_general_url(driver, kol)  # Scrape general information

            Log.info(
                f"Scrape the page of {kol['pageName']} with url {url} successfully"
            )

        except NoSuchElementException:  # Handle exception if we cannot access the page
            time.sleep(2)  # Sleep to wait the page load

            exception_driver = self.exceptional_driver_queue.get()
            handle_login_from_main_page(
                exception_driver, url, self.__is_logged_in, self.config
            )  # Login and take the information

            self.__scrape_general_url(
                exception_driver, kol
            )  # Scrape general information

            self.exceptional_driver_queue.put(
                exception_driver
            )  # Pay back the exceptional driver

            Log.info(
                f"Scrape the page of {kol['pageName']} with url {url} successfully"
            )

        except Exception as e:
            Log.error(e)
        finally:
            self.driver_queue.put(driver)  # Pay back the driver to the queue


# EOF
