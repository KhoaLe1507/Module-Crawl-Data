from concurrent.futures import ThreadPoolExecutor
from typing import List, override
from tqdm import tqdm
import threading
import queue
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


import datetime
import regex
import time
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    NoSuchWindowException,
    NoSuchAttributeException,
)
from bs4 import BeautifulSoup, Tag

from web_scraper import WebScraper, Config, ScrapeResult


def conv_chrome_options(
    chrome_options: List[str], experimental_options: List[tuple]
) -> webdriver.ChromeOptions:
    result = webdriver.ChromeOptions()
    for option in chrome_options:
        result.add_argument(option)
    for option in experimental_options:
        result.add_experimental_option(*option)
    return result


class FacebookConfig(Config):
    def __init__(self) -> None:
        super().__init__()
        self.chrome_options = ["start-maximized"]
        self.experimental_options = [
            ("prefs", {"profile.default_content_setting_values.notifications": 2})
        ]
        self.n_workers: int = 1
        self.n_exceptional_workers: int = 1
        self.username: str = ""
        self.password: str = ""
        self.site_url = "https://www.facebook.com"

        self.is_scraping_general_info: bool = True
        self.is_scraping_about_tab: bool = True
        self.is_scraping_posts: bool = False

        self.login_form_path = '//form[@class="_9vtf"]'
        self.username_input_path = '//input[@type="text"]'
        self.password_input_path = '//input[@type="password"]'
        self.login_button_path = '//button[@name="login"]'
        self.meta_data_element = '//meta[@name="description"]'
        self.avatar_element_path = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[1]/div/a/div/svg/g/image"
        self.beside_avt_container = (
            '//div[@class="x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x1iyjqo2 x2lwn1j"]'
        )
        self.page_name_element_path = '//div[@class="x1e56ztr x1xmf6yo"]/span/h1'
        self.close_button_path = '//div[@class="x92rtbv x10l6tqk x1tk7jg1 x1vjfegm"]'
        self.about_tab_element_path = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[3]/div/div/div/div[1]/div/div/div[1]/div/div/div/div/div/div/a[2]"
        self.contact_and_basic_info_elements_path = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div"


class FacebookAbout(ScrapeResult):
    def __init__(self) -> None:
        self.categories = ""
        self.email = ""
        self.mobile = ""
        self.address = ""
        self.website = []
        self.tiktok = []
        self.instagram = []
        self.youtube = []
        super().__init__()


class FacebookKOL(ScrapeResult):
    def __init__(self, id, url) -> None:
        self.platform = "facebook"
        self.id = id
        self.pageUrl = url
        self.avatarUrl: str | None = None
        self.profileAvatarUrl: str | None = None
        self.pageName: str | None = None
        self.talkingAbout = None
        self.likesCount = None
        self.followers = None
        self.following = None
        self.likes = None
        self.dateCollected = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.about = FacebookAbout()
        super().__init__()


class FacebookScraper(WebScraper):
    def __init__(self, config: FacebookConfig) -> None:
        super().__init__(config)
        self.lock = threading.Lock()
        self.driver_queue = queue.Queue()
        self.exceptional_driver_queue = queue.Queue()
        self.chrome_options = conv_chrome_options(
            config.chrome_options, config.experimental_options
        )
        self.config = config
        self.__is_logged_in = False

    def __setup(self):
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
            logging.info("Started the drivers succesfully")
        except Exception as e:
            logging.info("Starting the drivers failed")
            logging.error("Error: ", e)

    @override
    def close(self) -> None:
        while not self.driver_queue.empty():
            self.driver_queue.get().quit()

    @override
    def run(self, urls: List[str]) -> None:
        self.__setup()
        with ThreadPoolExecutor(max_workers=self.config.n_workers) as executor:
            for i, url in enumerate(urls):
                kol = FacebookKOL(i, url)
                with self.lock:
                    self.result.append(kol)

            if self.config.is_scraping_general_info:
                for url, kol in tqdm(zip(urls, self.result)):
                    executor.submit(self.__scrape_url, url, kol)

            if self.config.is_scraping_about_tab or self.config.is_scraping_posts:
                for _ in range(self.config.n_workers):
                    driver = self.driver_queue.get()
                    driver.get(driver.current_url)
                    try:
                        self.__handle_login_from_redirecting(driver, driver.current_url)
                    except NoSuchElementException:
                        self.__handle_login_from_kol_page(driver)

                    self.driver_queue.put(driver)

            if self.config.is_scraping_about_tab:
                for url, kol in tqdm(zip(urls, self.result)):
                    executor.submit(self.__scrape_about_tab, url, kol)

    def __scrape_general_url(self, driver: webdriver.Chrome, kol: FacebookKOL) -> None:
        try:
            time.sleep(4)

            meta_data_element = driver.find_elements(
                By.XPATH, self.config.meta_data_element
            )
            if meta_data_element:
                try:
                    content = meta_data_element[0].get_attribute("content")
                    if content is None:
                        content = ""
                    pattern = r"[\d,]+(?:\.\d+)?\s+(?:likes|talking about)"
                    matches = regex.findall(pattern, content)

                    if len(matches) > 0:
                        likes_content = matches[0].strip().split()
                        talking_about_content = matches[1].strip().split()
                        kol.likesCount = likes_content[0]
                        kol.talkingAbout = talking_about_content[0]
                except NoSuchAttributeException as e:
                    logging.error(e.msg)

            try:
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                avt_element = soup.find("image")
                if avt_element and isinstance(avt_element, Tag):
                    kol.avatarUrl = avt_element.attrs["xlink:href"]

                    poster_element = soup.find(
                        "img", {"data-imgperflogname": "profileCoverPhoto"}
                    )
                    if poster_element and isinstance(poster_element, Tag):
                        kol.profileAvatarUrl = poster_element.attrs["src"]

            except NoSuchElementException as e:
                logging.error(e.msg)

            beside_avt_container = None
            try:
                beside_avt_container = driver.find_element(
                    By.XPATH, self.config.beside_avt_container
                )
            except NoSuchElementException as e:
                logging.error(e.msg)

            if beside_avt_container:
                try:
                    page_name_element = beside_avt_container.find_element(
                        By.XPATH, self.config.page_name_element_path
                    )
                    kol.pageName = page_name_element.text
                except NoSuchElementException as e:
                    logging.error(e.msg)

                lff_element = beside_avt_container.find_elements(By.TAG_NAME, "a")
                for a_tag in lff_element:
                    a_content = a_tag.text.split()
                    kol[a_content[1]] = a_content[0]

        except NoSuchElementException as e:
            logging.error("Element Error: ", e.msg)
        except Exception as e:
            logging.error(e)

    def __scrape_about_tab(self, url: str, kol: FacebookKOL) -> None:
        driver = self.driver_queue.get()
        driver.get(url)
        try:
            logging.info(f"Start scraping {kol.pageName}'s about tab.")
            about_tab_element = None
            try:
                about_tab_element = driver.find_element(
                    By.XPATH, self.config.about_tab_element_path
                )
                about_tab_element.click()
            except NoSuchElementException as e:
                logging.error(e.msg)
                return
            except ElementClickInterceptedException:
                if about_tab_element:
                    try:
                        about_tab_element.click()
                    except ElementClickInterceptedException as e:
                        logging.error(e.msg)
                        return

            time.sleep(5)

            contact_and_basic_info_elements = driver.find_elements(
                By.XPATH, self.config.contact_and_basic_info_elements_path
            )
            for j, contact_and_basic_info_element in enumerate(
                contact_and_basic_info_elements
            ):
                logging.info(j)
                try:
                    span_tag = contact_and_basic_info_element.find_element(
                        By.XPATH, "div/div[1]/div/h2/span"
                    )
                except NoSuchElementException as e:
                    logging.error(e.msg)
                    continue

                logging.info(span_tag.text.lower())
                match span_tag.text.lower():
                    case "categories":
                        try:
                            categories_element = (
                                contact_and_basic_info_element.find_element(
                                    By.XPATH, '//div[@class="xat24cr"]'
                                )
                            )
                            logging.info(f"Categories: {categories_element.text}")
                            kol.about.categories = categories_element.text
                        except NoSuchElementException as e:
                            logging.error(e.msg)

                    case "contact info":
                        div_elements = contact_and_basic_info_element.find_elements(
                            By.XPATH, "div/div"
                        )[1:]
                        logging.info(f"Div elements: {len(div_elements)}")
                        for k, div_element in enumerate(div_elements):
                            span_elements = div_element.find_elements(
                                By.TAG_NAME, "span"
                            )
                            logging.info(f"Span: {len(span_elements)}")
                            if span_elements[1].text != "":
                                logging.info(
                                    span_elements[1].text.lower(), span_elements[0].text
                                )
                                kol.about[span_elements[1].text.lower()] = (
                                    span_elements[0].text
                                )
                            else:
                                logging.info(
                                    f"contactInfo{k + 1}", span_elements[0].text
                                )
                                kol.about[f"contactInfo{k + 1}"] = span_elements[0].text

                    case "websites and social links":
                        try:
                            website_part = contact_and_basic_info_element.find_element(
                                By.XPATH, "div/div[2]/div/div/div[2]/ul"
                            )

                            website_list = website_part.find_elements(By.TAG_NAME, "li")
                            logging.info(f"Website list: {len(website_list)}")
                            for website in website_list:
                                span_elements = website.find_elements(
                                    By.TAG_NAME, "span"
                                )
                                logging.info(
                                    span_elements[1].text.lower(), span_elements[0].text
                                )
                                kol.about[span_elements[1].text.lower()].append(
                                    span_elements[0].text
                                )
                        except NoSuchElementException as e:
                            logging.error(e.msg)

                        social_list_elements = (
                            contact_and_basic_info_element.find_elements(
                                By.XPATH, "div/div[3]/div/div/div"
                            )
                        )
                        logging.info(f"Social list: {social_list_elements}")
                        for social_list_element in social_list_elements:
                            social_elements = social_list_element.find_elements(
                                By.TAG_NAME, "li"
                            )
                            for social_element in social_elements:
                                span_elements = social_element.find_elements(
                                    By.TAG_NAME, "span"
                                )
                                logging.info(
                                    span_elements[1].text.lower(), span_elements[0].text
                                )
                                kol.about[span_elements[1].text.lower()].append(
                                    span_elements[0].text
                                )

                    case "basic info":
                        div_elements = contact_and_basic_info_element.find_elements(
                            By.XPATH, "div/div"
                        )[1:]
                        logging.info(f"Div elements: {len(div_elements)}")
                        for k, div_element in enumerate(div_elements):
                            span_elements = div_element.find_elements(
                                By.TAG_NAME, "span"
                            )
                            logging.info(f"Span: {len(span_elements)}")
                            if len(span_elements) == 1:
                                logging.info(f"basicInfo{k + 1}", span_elements[0].text)
                                kol.about[f"basicInfo{k + 1}"] = span_elements[0].text
                            else:
                                logging.info(
                                    span_elements[1].text.lower(), span_elements[0].text
                                )
                                kol.about[span_elements[1].text.lower()] = (
                                    span_elements[0].text
                                )

            logging.info(
                f"Scrape the about tab of url {driver.current_url} successfully"
            )

        except NoSuchElementException as e:
            logging.error(e.msg)
        except Exception as e:
            logging.error(e)
        finally:
            self.driver_queue.put(driver)

    def __scrape_url(self, url: str, kol: FacebookKOL) -> None:
        driver = self.driver_queue.get()
        try:
            driver.get(url)
            time.sleep(1)
            close_button = None
            try:
                close_button = driver.find_element(
                    By.XPATH, self.config.close_button_path
                )
                close_button.click()
            except NoSuchElementException:
                raise NoSuchElementException("Login de")
            except ElementClickInterceptedException:
                time.sleep(3)
                if close_button:
                    try:
                        close_button.click()
                    except ElementClickInterceptedException:
                        raise ElementClickInterceptedException("Cannot close the table")

            self.__scrape_general_url(driver, kol)
            logging.info(
                f'Scraped "{kol.pageName}"\'s general info at {url} successfully'
            )

        except NoSuchElementException:
            time.sleep(2)
            exception_driver = self.exceptional_driver_queue.get()
            self.__handle_login_from_main_page(exception_driver, url)
            self.__scrape_general_url(exception_driver, kol)
            self.exceptional_driver_queue.put(exception_driver)
            logging.info(f'Scraped "{kol.pageName}" at {url} successfully')
        except Exception as e:
            logging.error(e)

        finally:
            self.driver_queue.put(driver)

    def __handle_login_from_main_page(
        self,
        driver: webdriver.Chrome,
        url: str | None = None,
    ) -> None:
        try:
            if not self.__is_logged_in:
                driver.get(self.config.site_url)

                try:
                    login_form = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, self.config.login_form_path)
                        )
                    )
                    username_input = login_form.find_element(
                        By.XPATH, self.config.username_input_path
                    )
                    for i in self.config.username:
                        time.sleep(0.2)
                        username_input.send_keys(i)

                    time.sleep(3)
                    password_input = login_form.find_element(
                        By.XPATH, self.config.password_input_path
                    )
                    for i in self.config.password:
                        time.sleep(0.2)
                        password_input.send_keys(i)

                    time.sleep(3)
                    login_button = None
                    try:
                        login_button = login_form.find_element(
                            By.XPATH, self.config.login_button_path
                        )
                        login_button.click()
                    except ElementClickInterceptedException:
                        if login_button:
                            try:
                                login_button.click()
                            except ElementClickInterceptedException as e:
                                logging.error(e.msg)
                                raise ElementClickInterceptedException("Cannot login")

                    self.__is_logged_in = True

                except NoSuchElementException as e:
                    logging.error("Element Error:", e.msg)
                except Exception as e:
                    logging.error("Error:", e)

                time.sleep(5)

            if url:
                driver.get(url)

        except Exception:
            logging.error("Cannot get the page.")

    def __handle_login_from_redirecting(
        self, driver: webdriver.Chrome, current_url: str
    ) -> None:
        try:
            login_form = driver.find_element(By.XPATH, '//div[@id="loginform"]')
            username_input = login_form.find_element(By.XPATH, '//input[@type="text"]')
            password_input = login_form.find_element(
                By.XPATH, '//input[@type="password"]'
            )
            for i in self.config.username:
                time.sleep(0.2)
                username_input.send_keys(i)
            time.sleep(2)
            for i in self.config.password:
                time.sleep(0.2)
                password_input.send_keys(i)

            login_button = None
            try:
                login_button = login_form.find_element(
                    By.XPATH, '//button[@name="login"]'
                )
                login_button.click()
            except ElementClickInterceptedException:
                time.sleep(3)
                if login_button:
                    try:
                        login_button.click()
                    except ElementClickInterceptedException:
                        raise ElementClickInterceptedException("Cannot login")

            if driver.current_url != current_url:
                driver.get(current_url)

        except NoSuchElementException as e:
            logging.error(e.msg)
            raise NoSuchElementException("Logging in by another way")
        except NoSuchWindowException as e:
            logging.error(e.msg)
        except ElementClickInterceptedException as e:
            logging.error(e)
        finally:
            time.sleep(3)

    def __handle_login_from_kol_page(self, driver: webdriver.Chrome) -> None:
        try:
            username_input = driver.find_element(
                By.XPATH,
                "/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[2]/form/div/div[4]/div/div/label/div/input",
            )
            password_input = driver.find_element(
                By.XPATH,
                "/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[2]/form/div/div[5]/div/div/label/div/input",
            )
            for i in self.config.username:
                time.sleep(0.2)
                username_input.send_keys(i)
            time.sleep(2)
            for i in self.config.password:
                time.sleep(0.2)
                password_input.send_keys(i)

            # Find login button and click
            login_button = None
            try:
                login_button = driver.find_element(
                    By.XPATH,
                    "/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[2]/form/div/div[6]/div",
                )
                login_button.click()
            except ElementClickInterceptedException:
                time.sleep(3)
                if login_button:
                    try:
                        login_button.click()
                    except ElementClickInterceptedException:
                        raise ElementClickInterceptedException("Cannot login")

        except NoSuchElementException as e:
            logging.error(e.msg)
            raise NoSuchElementException("Logging in by another way")
        except NoSuchWindowException as e:
            logging.error(e.msg)
        except ElementClickInterceptedException as e:
            logging.error(e)
        finally:
            time.sleep(3)


# EOF
