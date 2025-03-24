from web_scraper import Config, ScrapeResult
from typing import override
import datetime


class FacebookConfig(Config):
    def __init__(self) -> None:
        super().__init__()
        self.chrome_options = ["start-maximized"]
        self.experimental_options = [
            ("prefs", {"profile.default_content_setting_values.notifications": 2})
        ]
        self.n_workers: int = 2
        self.n_exceptional_workers: int = 1
        self.username: str = ""
        self.password: str = ""
        self.site_url = "https://www.facebook.com"

        self.is_scraping_general_info: bool = True
        self.is_scraping_about_tab: bool = True
        self.is_scraping_posts: bool = False

    @override
    def check(self) -> None:
        super().check()
        if self.n_workers <= 0 or self.n_workers >= 8:
            raise ValueError("Number of workers must be positive and smaller than 8")
        if self.n_exceptional_workers <= 0 or self.n_exceptional_workers >= 5:
            raise ValueError(
                "Number of exceptional workers must be positive and smaller than 5"
            )


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
        self.introDescription: str | None = None
        self.about = FacebookAbout()
        super().__init__()


class Xpaths:
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
    about_elements_path = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[1]/div"
    contact_and_basic_info_elements_path = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div"
    privacy_and_legal_info_elements_path = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div"
    intro_description_element_path = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[1]/div/div/span"


# EOF
