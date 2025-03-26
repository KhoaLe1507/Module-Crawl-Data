from selenium.webdriver.common.by import By

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)

from log import Log

from facebook_config import FacebookKOL, Xpaths
from selenium import webdriver


def scrape_contact_and_basic_info(driver: webdriver.Chrome, kol: FacebookKOL) -> None:
    """
    Scrape the contact and basic info in about tab

    Params:
        driver (Chrome): current driver
        index (int): index of kol dictionary in list

    Return:
        Dictionary of kol infomation
    """

    try:
        # Get contact and basic info element
        contact_and_basic_info_elements = driver.find_elements(
            By.XPATH, Xpaths.contact_and_basic_info_elements_path
        )
        for _, contact_and_basic_info_element in enumerate(
            contact_and_basic_info_elements
        ):
            try:
                span_tag = contact_and_basic_info_element.find_element(
                    By.XPATH, "div/div[1]/div/h2/span"
                )
            except NoSuchElementException as e:
                Log.error(e.msg)
                continue

            Log.info(3, span_tag.text)

            match span_tag.text.lower():
                case "categories":  # Get categories tags
                    try:
                        categories_element = (
                            contact_and_basic_info_element.find_element(
                                By.XPATH, '//div[@class="xat24cr"]'
                            )
                        )

                        kol.about.categories = categories_element.text

                        Log.info(4, kol.about.categories)

                    except NoSuchElementException as e:
                        Log.error(e.msg)

                case "contact info":  # Get contact info tags
                    div_elements = contact_and_basic_info_element.find_elements(
                        By.XPATH, "div/div"
                    )[1:]

                    for k, div_element in enumerate(div_elements):
                        span_elements = div_element.find_elements(By.TAG_NAME, "span")

                        if span_elements[1].text != "":
                            Log.info(
                                4,
                                f"{span_elements[1].text.lower()}: {span_elements[0].text}",
                            )

                            kol.about[span_elements[1].text.lower()] = span_elements[
                                0
                            ].text
                        else:
                            Log.info(4, f"contactInfo{k + 1}: {span_elements[0].text}")

                            kol.about[f"contactInfo{k + 1}"] = span_elements[0].text

                case "websites and social links":  # Get website and social links
                    # Check whether the list has length of 2 or 3
                    list_web_social = contact_and_basic_info_element.find_elements(
                        By.XPATH, "div/div"
                    )
                    len_web_social = len(list_web_social)

                    # Get website links
                    try:
                        website_part = None
                        if len_web_social == 3:
                            website_part = contact_and_basic_info_element.find_element(
                                By.XPATH,
                                f"div/div[{len_web_social - 1}]/div/div/div[2]/ul",
                            )
                        # Check if website_part is existed?
                        elif (
                            len_web_social == 2 and "Website" in list_web_social[1].text
                        ):
                            website_part = contact_and_basic_info_element.find_element(
                                By.XPATH, f"div/div[{len_web_social}]/div/div/div[2]/ul"
                            )

                        website_list = []
                        if website_part is not None:
                            website_list = website_part.find_elements(By.TAG_NAME, "li")

                        Log.info(4, f"Websites: {len(website_list)}")

                        for website in website_list:
                            span_elements = website.find_elements(By.TAG_NAME, "span")

                            kol.about[span_elements[1].text.lower()].append(
                                span_elements[0].text
                            )

                            Log.info(
                                5,
                                f"{span_elements[1].text.lower()}: {span_elements[0].text}",
                            )

                    except NoSuchElementException as e:
                        Log.error(e.msg)
                    except StaleElementReferenceException as e:
                        Log.error(e.msg)
                    except Exception as e:
                        Log.exception(e)

                    # Get social links and check if social_list is existed?
                    if len_web_social == 3 or (
                        len_web_social == 2 and "Website" not in list_web_social[1].text
                    ):
                        social_list_elements = (
                            contact_and_basic_info_element.find_elements(
                                By.XPATH, f"div/div[{len_web_social}]/div/div/div"
                            )
                        )
                    else:
                        continue

                    Log.info(4, f"Social: {len(social_list_elements)}")

                    for social_list_element in social_list_elements:
                        social_elements = social_list_element.find_elements(
                            By.TAG_NAME, "li"
                        )
                        for social_element in social_elements:
                            span_elements = social_element.find_elements(
                                By.TAG_NAME, "span"
                            )

                            kol.about[span_elements[1].text.lower()].append(
                                span_elements[0].text
                            )

                            Log.info(
                                5,
                                f"{span_elements[1].text.lower()}: {span_elements[0].text}",
                            )

                case "basic info":  # Get basic info
                    div_elements = contact_and_basic_info_element.find_elements(
                        By.XPATH, "div/div"
                    )[1:]

                    for k, div_element in enumerate(div_elements):
                        span_elements = div_element.find_elements(By.TAG_NAME, "span")

                        if len(span_elements) == 1:
                            if "review" in span_elements[0].text:
                                Log.info(
                                    4,
                                    f"Reviews: {span_elements[0].text}",
                                )
                                kol.about["reviews"] = span_elements[0].text
                            else:
                                Log.info(
                                    4, f"basicInfo{k + 1}: {span_elements[0].text}"
                                )
                                kol.about[f"basicInfo{k + 1}"] = span_elements[0].text
                        else:
                            Log.info(
                                4,
                                f"{span_elements[1].text.lower()}: {span_elements[0].text}",
                            )
                            kol.about[span_elements[1].text.lower()] = span_elements[
                                0
                            ].text
    except NoSuchElementException as e:
        Log.error(e.msg)
    except Exception as e:
        Log.exception(e)


def scrape_privacy_and_legal_info(
    driver: webdriver.Chrome,
    kol: FacebookKOL,
):
    """
    Scrape the privacy and legal info in about tab

    Params:
        driver (Chrome): current driver
        index (int): index of kol dictionary in list

    Return:
        Dictionary of kol infomation
    """

    try:
        # Get privacy and legal info element
        privacy_and_legal_info_elements = driver.find_elements(
            By.XPATH,
            "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div",
        )

        for _, privacy_and_legal_info_element in enumerate(
            privacy_and_legal_info_elements
        ):
            # Find each part of info
            try:
                span_tag = privacy_and_legal_info_element.find_element(
                    By.XPATH, "div/div[1]/div/h2/span"
                )
                title = "".join(
                    [
                        span_text.capitalize() if i > 0 else span_text
                        for i, span_text in enumerate(span_tag.text.lower().split())
                    ]
                )

                kol.about[title] = {}

                Log.info(3, span_tag.text)

            except NoSuchElementException as e:
                Log.error(e.msg)
                continue
            except StaleElementReferenceException as e:
                Log.error(e.msg)
                continue

            div_elements = privacy_and_legal_info_element.find_elements(
                By.XPATH, "div/div"
            )
            div_elements = div_elements[1:] if len(div_elements) > 1 else []

            for k, div_element in enumerate(div_elements):
                # Find each element of each part of info
                span_elements = div_element.find_elements(By.TAG_NAME, "span")

                if len(span_elements) < 2:
                    continue

                if span_elements[1].text != "":
                    Log.info(
                        4, f"{span_elements[1].text.lower()}: {span_elements[0].text}"
                    )
                    kol.about[title][span_elements[1].text.lower()] = span_elements[
                        0
                    ].text
                else:
                    Log.info(4, f"{title}{k + 1}: {span_elements[0].text}")
                    kol.about[title][f"{title}{k + 1}"] = span_elements[0].text

    except NoSuchElementException as e:
        Log.error(e.msg)
    except Exception as e:
        Log.exception(e)


def scrape_page_transparency(
    driver: webdriver.Chrome,
    kol: FacebookKOL,
):
    """
    Scrape the page transparency in about tab

    Params:
        driver (Chrome): current driver
        index (int): index of kol dictionary in list

    Return:
        Dictionary of kol infomation
    """

    try:
        page_trans_elements = driver.find_elements(
            By.XPATH,
            "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div/div",
        )

        page_id_spans = page_trans_elements[1].find_elements(By.TAG_NAME, "span")
        creation_date_spans = page_trans_elements[2].find_elements(By.TAG_NAME, "span")

        kol.about.pageId = page_id_spans[0].text
        kol.about.creationDate = creation_date_spans[0].text

        Log.info(3, f"Page ID: {kol.about['pageId']}")
        Log.info(3, f"Creation date: {kol.about['creationDate']}")

    except NoSuchElementException as e:
        Log.error(e.msg)
    except Exception as e:
        Log.exception(e)


def scrape_detail_info(driver: webdriver.Chrome, kol: FacebookKOL):
    """
    Scrape the detail info in about tab

    Params:
        driver (Chrome): current driver
        index (int): index of kol dictionary in list

    Return:
        Dictionary of kol infomation
    """

    try:
        page_trans_elements = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div",
        )
        kol.about.detail = page_trans_elements.text

        Log.info(3, f"Detail info: {kol.about.detail}")

    except NoSuchElementException as e:
        Log.error(e.msg)
    except Exception as e:
        Log.exception(e)


# EOF
