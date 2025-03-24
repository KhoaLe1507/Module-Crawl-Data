from selenium.webdriver.common.by import By

from selenium.common.exceptions import (
    NoSuchElementException,
)

from log import Log

from facebook_config import FacebookKOL


def fb_about_categories(contact_and_basic_info_element, kol: FacebookKOL):
    try:
        categories_element = contact_and_basic_info_element.find_element(
            By.XPATH, '//div[@class="xat24cr"]'
        )
        Log.info(f"Categories: {categories_element.text}")
        kol.about.categories = categories_element.text
    except NoSuchElementException as e:
        Log.error(e.msg)


def fb_about_contact_info(contact_and_basic_info_element, kol: FacebookKOL):
    div_elements = contact_and_basic_info_element.find_elements(By.XPATH, "div/div")[1:]
    Log.info(f"Div elements: {len(div_elements)}")
    for k, div_element in enumerate(div_elements):
        span_elements = div_element.find_elements(By.TAG_NAME, "span")
        Log.info(f"Span: {len(span_elements)}")
        if span_elements[1].text != "":
            Log.info(span_elements[1].text.lower(), span_elements[0].text)
            kol.about[span_elements[1].text.lower()] = span_elements[0].text
        else:
            Log.info(f"contactInfo{k + 1}", span_elements[0].text)
            kol.about[f"contactInfo{k + 1}"] = span_elements[0].text


def fb_about_website_and_social_links(contact_and_basic_info_element, kol: FacebookKOL):
    try:
        website_part = contact_and_basic_info_element.find_element(
            By.XPATH, "div/div[2]/div/div/div[2]/ul"
        )

        website_list = website_part.find_elements(By.TAG_NAME, "li")
        Log.info(f"Website list: {len(website_list)}")
        for website in website_list:
            span_elements = website.find_elements(By.TAG_NAME, "span")
            Log.info(span_elements[1].text.lower(), span_elements[0].text)
            kol.about[span_elements[1].text.lower()].append(span_elements[0].text)
    except NoSuchElementException as e:
        Log.error(e.msg)

    social_list_elements = contact_and_basic_info_element.find_elements(
        By.XPATH, "div/div[3]/div/div/div"
    )
    Log.info(f"Social list: {social_list_elements}")
    for social_list_element in social_list_elements:
        social_elements = social_list_element.find_elements(By.TAG_NAME, "li")
        for social_element in social_elements:
            span_elements = social_element.find_elements(By.TAG_NAME, "span")
            Log.info(span_elements[1].text.lower(), span_elements[0].text)
            kol.about[span_elements[1].text.lower()].append(span_elements[0].text)


def fb_about_basic_info(contact_and_basic_info_element, kol: FacebookKOL):
    div_elements = contact_and_basic_info_element.find_elements(By.XPATH, "div/div")[1:]
    Log.info(f"Div elements: {len(div_elements)}")
    for k, div_element in enumerate(div_elements):
        span_elements = div_element.find_elements(By.TAG_NAME, "span")
        Log.info(f"Span: {len(span_elements)}")
        if len(span_elements) == 1:
            Log.info(f"basicInfo{k + 1}", span_elements[0].text)
            kol.about[f"basicInfo{k + 1}"] = span_elements[0].text
        else:
            Log.info(span_elements[1].text.lower(), span_elements[0].text)
            kol.about[span_elements[1].text.lower()] = span_elements[0].text


# EOF
