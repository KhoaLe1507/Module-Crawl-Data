import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    NoSuchWindowException,
)
from log import Log
from src.facebook.config import FacebookConfig, Xpaths
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def handle_login_from_redirecting(
    driver: webdriver.Chrome, current_url: str, config: FacebookConfig
) -> None:
    try:
        login_form = driver.find_element(By.XPATH, '//div[@id="loginform"]')
        username_input = login_form.find_element(By.XPATH, '//input[@type="text"]')
        password_input = login_form.find_element(By.XPATH, '//input[@type="password"]')
        for i in config.username:
            time.sleep(0.2)
            username_input.send_keys(i)
        time.sleep(2)
        for i in config.password:
            time.sleep(0.2)
            password_input.send_keys(i)

        login_button = None
        try:
            login_button = login_form.find_element(By.XPATH, '//button[@name="login"]')
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
        Log.error(e.msg)
        raise NoSuchElementException("Log in by another way")
    except NoSuchWindowException as e:
        Log.error(e.msg)
    except ElementClickInterceptedException as e:
        Log.error(e)
    finally:
        time.sleep(3)


def handle_login_from_kol_page(
    driver: webdriver.Chrome, config: FacebookConfig
) -> None:
    try:
        username_input = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[2]/form/div/div[4]/div/div/label/div/input",
        )
        password_input = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[2]/form/div/div[5]/div/div/label/div/input",
        )
        for i in config.username:
            time.sleep(0.2)
            username_input.send_keys(i)
        time.sleep(2)
        for i in config.password:
            time.sleep(0.2)
            password_input.send_keys(i)

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
        Log.error(e.msg)
        raise NoSuchElementException("Log in by another way")
    except NoSuchWindowException as e:
        Log.error(e.msg)
    except ElementClickInterceptedException as e:
        Log.error(e)
    finally:
        time.sleep(3)


def handle_login_from_block_page(
    driver: webdriver.Chrome, config: FacebookConfig
) -> None:
    """
    Handle login from block page

    Params:
        driver (Chrome): the current driver
    """

    try:
        # Find login form
        login_form = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[2]/div/form",
        )

        # Find inputs
        username_input = login_form.find_element(By.XPATH, "div[2]/div[1]/label/input")
        password_input = login_form.find_element(By.XPATH, "div[2]/div[2]/label/input")

        # Fill the inputs
        for i in config.username:
            time.sleep(0.2)
            username_input.send_keys(i)
        time.sleep(2)
        for i in config.password:
            time.sleep(0.2)
            password_input.send_keys(i)

        login_button = None
        try:
            login_button = login_form.find_element(By.XPATH, "div[2]/div[3]/div/div")
            login_button.click()
        except ElementClickInterceptedException:
            time.sleep(3)
            try:
                if login_button:
                    login_button.click()
            except ElementClickInterceptedException:
                raise ElementClickInterceptedException("Cannot login")

        Log.info("Log in succesffuly")

    except NoSuchElementException as e:
        Log.error(e.msg)
        raise NoSuchElementException("Log in by another way")
    except NoSuchWindowException as e:
        Log.error(e.msg)
    except ElementClickInterceptedException as e:
        Log.error(e.msg)
    finally:
        time.sleep(3)


def handle_login_from_main_page(
    driver: webdriver.Chrome,
    url: str | None,
    is_logged_in: bool,
    config: FacebookConfig,
) -> None:
    try:
        if not is_logged_in:
            driver.get(config.site_url)  # Go to facebook login page

            try:
                # Find login form
                login_form = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, Xpaths.login_form_path))
                )

                # Find username input and fill
                username_input = login_form.find_element(
                    By.XPATH, Xpaths.username_input_path
                )
                for i in config.username:
                    time.sleep(0.2)
                    username_input.send_keys(i)

                time.sleep(3)

                # Find password input and fill
                password_input = login_form.find_element(
                    By.XPATH, Xpaths.password_input_path
                )
                for i in config.password:
                    time.sleep(0.2)
                    password_input.send_keys(i)

                time.sleep(3)

                # Click login button
                login_button = None
                try:
                    login_button = login_form.find_element(
                        By.XPATH, Xpaths.login_button_path
                    )
                    login_button.click()
                except ElementClickInterceptedException:
                    try:
                        if login_button:
                            login_button.click()
                    except ElementClickInterceptedException as e:
                        Log.error(e.msg)
                        raise ElementClickInterceptedException("Cannot login")

                is_logged_in = True

                Log.info("Log in succesffuly")

            except NoSuchElementException as e:
                Log.error("Element Error: ", e.msg)
            except Exception as e:
                Log.error("Error: ", e)

            time.sleep(5)

        if url:
            # Get the infomation
            driver.get(url)

    except Exception:
        Log.info("Cannot get the page.")
