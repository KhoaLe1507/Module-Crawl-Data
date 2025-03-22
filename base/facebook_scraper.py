from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from typing import List, Dict, override
import datetime
import regex
import time

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

from web_scraper import WebScraper, Config


@dataclass
class FacebookConfig(Config):
    username: str = ""
    password: str = ""
    site_url = "https://www.facebook.com"
    # is_scraping_general_info: bool = True
    # is_scraping_about_tab: bool = True
    # is_scraping_posts: bool = False

    is_scraping_general_info: bool = True
    is_scraping_about_tab: bool = False
    is_scraping_posts: bool = False

    login_form_path = '//form[@class="_9vtf"]'
    username_input_path = '//input[@type="text"]'
    password_input_path = '//input[@type="password"]'
    login_button_path = '//button[@name="login"]'
    meta_data_element = '//meta[@name="description"]'
    avatar_element_path = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[1]/div/a/div/svg/g/image"
    beside_avt_container = (
        '//div[@class="x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x1iyjqo2 x2lwn1j"]'
    )
    page_name_element_path = '//div[@class="x1e56ztr x1xmf6yo"]/span/h1'
    close_button_path = '//div[@class="x92rtbv x10l6tqk x1tk7jg1 x1vjfegm"]'
    about_tab_element_path = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[3]/div/div/div/div[1]/div/div/div[1]/div/div/div/div/div/div/a[2]"
    contact_and_basic_info_elements_path = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div"


@dataclass
class FacebookKOL:
    def __init__(self) -> None:
        self.platform = "facebook"
        self.id: int | None = None

        self.pageUrl: str | None = None
        self.avatarUrl: str | None = None
        self.profileAvatarUrl: str | None = None

        self.pageName: str | None = None

        self.talkingAbout = None
        self.following = None
        self.followers = None
        self.likes = None

        self.dateCollected: str | None = None
        self.other: Dict[str, str] = {}


class FacebookScraper(WebScraper):
    def __init__(self, config: FacebookConfig = FacebookConfig()) -> None:
        super().__init__(config)
        self.config = config
        self.__is_logged_in = False

    @override
    def _run(self, executor: ThreadPoolExecutor, urls: List[str]) -> None:
        if self.config.is_scraping_general_info:
            for i, url in enumerate(urls):
                executor.submit(self.__scrape_url, url, i)

        if self.config.is_scraping_about_tab:
            for i, url in enumerate(urls):
                executor.submit(self.__scrape_about_tab, url, i)

        if self.config.is_scraping_about_tab or self.config.is_scraping_posts:
            for _ in range(self.config.n_workers):
                driver = self.driver_queue.get()
                driver.get(driver.current_url)
                try:
                    self.__handle_login_from_redirecting(driver, driver.current_url)
                except NoSuchElementException:
                    self.__handle_login_from_kol_page(driver)

                self.driver_queue.put(driver)

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

                        # kol[likes_content[1]] = likes_content[0]
                        kol.likes = likes_content[0]
                        kol.talkingAbout = talking_about_content[0]
                except NoSuchAttributeException as e:
                    print(e.msg)

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
                print(e.msg)

            beside_avt_container = None
            try:
                beside_avt_container = driver.find_element(
                    By.XPATH, self.config.beside_avt_container
                )
            except NoSuchElementException as e:
                print(e.msg)

            if beside_avt_container:
                try:
                    page_name_element = beside_avt_container.find_element(
                        By.XPATH, self.config.page_name_element_path
                    )
                    kol.pageName = page_name_element.text
                except NoSuchElementException as e:
                    print(e.msg)

                lff_element = beside_avt_container.find_elements(By.TAG_NAME, "a")
                for a_tag in lff_element:
                    a_content = a_tag.text.split()
                    kol.other[a_content[1]] = a_content[0]

        except NoSuchElementException as e:
            print("Element Error: ", e.msg)
        except Exception as e:
            print(e)

    def __scrape_about_tab(self, url: str, i: int):
        driver = self.driver_queue.get()
        driver.get(url)

        self.result[i]["categories"] = ""
        self.result[i]["email"] = ""
        self.result[i]["mobile"] = ""
        self.result[i]["address"] = ""
        self.result[i]["website"] = []
        self.result[i]["tiktok"] = []
        self.result[i]["instagram"] = []
        self.result[i]["youtube"] = []

        try:
            print(f"Start scrape page {self.result[i]['pageName']}")
            about_tab_element = None
            try:
                about_tab_element = driver.find_element(
                    By.XPATH, self.config.about_tab_element_path
                )
                about_tab_element.click()
            except NoSuchElementException as e:
                print(e.msg)
                return
            except ElementClickInterceptedException:
                if about_tab_element:
                    try:
                        about_tab_element.click()
                    except ElementClickInterceptedException as e:
                        print(e.msg)
                        return

            time.sleep(5)

            contact_and_basic_info_elements = driver.find_elements(
                By.XPATH, self.config.contact_and_basic_info_elements_path
            )
            for j, contact_and_basic_info_element in enumerate(
                contact_and_basic_info_elements
            ):
                print(j)
                try:
                    span_tag = contact_and_basic_info_element.find_element(
                        By.XPATH, "div/div[1]/div/h2/span"
                    )
                except NoSuchElementException as e:
                    print(e.msg)
                    continue

                print(span_tag.text.lower())
                match span_tag.text.lower():
                    case "categories":
                        try:
                            categories_element = (
                                contact_and_basic_info_element.find_element(
                                    By.XPATH, '//div[@class="xat24cr"]'
                                )
                            )
                            print(f"Categories: {categories_element.text}")
                            self.result[i]["categories"] = categories_element.text
                        except NoSuchElementException as e:
                            print(e.msg)

                    case "contact info":
                        div_elements = contact_and_basic_info_element.find_elements(
                            By.XPATH, "div/div"
                        )[1:]
                        print(f"Div elements: {len(div_elements)}")
                        for k, div_element in enumerate(div_elements):
                            span_elements = div_element.find_elements(
                                By.TAG_NAME, "span"
                            )
                            print(f"Span: {len(span_elements)}")
                            if span_elements[1].text != "":
                                print(
                                    span_elements[1].text.lower(), span_elements[0].text
                                )
                                self.result[i][span_elements[1].text.lower()] = (
                                    span_elements[0].text
                                )
                            else:
                                print(f"contactInfo{i + 1}", span_elements[0].text)
                                self.result[i][f"contactInfo{k + 1}"] = span_elements[
                                    0
                                ].text

                    case "websites and social links":
                        try:
                            website_part = contact_and_basic_info_element.find_element(
                                By.XPATH, "div/div[2]/div/div/div[2]/ul"
                            )

                            website_list = website_part.find_elements(By.TAG_NAME, "li")
                            print(f"Website list: {len(website_list)}")
                            for website in website_list:
                                span_elements = website.find_elements(
                                    By.TAG_NAME, "span"
                                )
                                print(
                                    span_elements[1].text.lower(), span_elements[0].text
                                )
                                self.result[i][span_elements[1].text.lower()].append(
                                    span_elements[0].text
                                )
                        except NoSuchElementException as e:
                            print(e.msg)

                        social_list_elements = (
                            contact_and_basic_info_element.find_elements(
                                By.XPATH, "div/div[3]/div/div/div"
                            )
                        )
                        print(f"Social list: {social_list_elements}")
                        for social_list_element in social_list_elements:
                            social_elements = social_list_element.find_elements(
                                By.TAG_NAME, "li"
                            )
                            for social_element in social_elements:
                                span_elements = social_element.find_elements(
                                    By.TAG_NAME, "span"
                                )
                                print(
                                    span_elements[1].text.lower(), span_elements[0].text
                                )
                                self.result[i][span_elements[1].text.lower()].append(
                                    span_elements[0].text
                                )

                    case "basic info":
                        div_elements = contact_and_basic_info_element.find_elements(
                            By.XPATH, "div/div"
                        )[1:]
                        print(f"Div elements: {len(div_elements)}")
                        for k, div_element in enumerate(div_elements):
                            span_elements = div_element.find_elements(
                                By.TAG_NAME, "span"
                            )
                            print(f"Span: {len(span_elements)}")
                            if len(span_elements) == 1:
                                print(f"basicInfo{k + 1}", span_elements[0].text)
                                self.result[i][f"basicInfo{k + 1}"] = span_elements[
                                    0
                                ].text
                            else:
                                print(
                                    span_elements[1].text.lower(), span_elements[0].text
                                )
                                self.result[i][span_elements[1].text.lower()] = (
                                    span_elements[0].text
                                )

            print(f"Scrape the about tab of url {driver.current_url} successfully")

        except NoSuchElementException as e:
            print(e.msg)
        except Exception:
            pass
        finally:
            self.driver_queue.put(driver)
            return self.result[i]

    def __scrape_url(self, url: str, i: int) -> None:
        driver = self.driver_queue.get()
        kol = FacebookKOL()
        kol.id = i
        kol.pageUrl = url
        # url = url[:-1]

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
            print(f"Scrape the page of {kol.pageName} with url {url} successfully")

        except NoSuchElementException:
            time.sleep(2)
            exception_driver = self.exceptional_driver_queue.get()
            self.__handle_login_from_main_page(exception_driver, url)
            self.__scrape_general_url(exception_driver, kol)
            self.exceptional_driver_queue.put(exception_driver)
            print(f"Scrape the page of {kol.pageName} with url {url} successfully")

        except Exception as e:
            print(e)
        finally:
            kol.dateCollected = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with self.lock:
                self.result.append(asdict(kol))
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
                                print(e.msg)
                                raise ElementClickInterceptedException("Cannot login")

                    self.__is_logged_in = True

                except NoSuchElementException as e:
                    print("Element Error:", e.msg)
                except Exception as e:
                    print("Error:", e)

                time.sleep(5)

            if url:
                driver.get(url)

        except Exception:
            print("Cannot get the page.")

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
            print(e.msg)
            raise NoSuchElementException("Logging in by another way")
        except NoSuchWindowException as e:  # if the window is closed
            print(e.msg)
        except ElementClickInterceptedException:
            pass
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
            print(e.msg)
            raise NoSuchElementException("Logging in by another way")
        except NoSuchWindowException as e:
            print(e.msg)
        except ElementClickInterceptedException:
            pass
        finally:
            time.sleep(3)
