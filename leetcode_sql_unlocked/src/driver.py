import os
import platform
from urllib.request import urlopen
import ssl
import zipfile
import re

from selenium import webdriver
from selenium.webdriver.support.abstract_event_listener import AbstractEventListener
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver

class EventListener(AbstractEventListener):
    """Attempt to disable animations"""
    def after_click_on(self, url, driver):
        animation =\
        """
        try { jQuery.fx.off = true; } catch(e) {}
        """
        driver.execute_script(animation)

class Driver:
    #agent src: https://www.whatismybrowser.com/guides/the-latest-user-agent/edge
    __WEB_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/94.0.992.50"


    def __download_driver(driver_path, system, try_count=0):
        # determine latest chromedriver version
        #version selection faq: http://chromedriver.chromium.org/downloads/version-selection
        CHROME_RELEASE_URL = "https://sites.google.com/chromium.org/driver/downloads?authuser=0"
        try:
            response = urlopen(
                CHROME_RELEASE_URL,
                context=ssl.SSLContext(ssl.PROTOCOL_TLS)
            ).read()
        except ssl.SSLError:
            response = urlopen(
                CHROME_RELEASE_URL
            ).read()
        #download second latest version,most recent is sometimes not out to public yet

        latest_version = re.findall(
            b"ChromeDriver \d{2,3}\.0\.\d{4}\.\d+", response
        )[try_count].decode().split()[1]
        print('Downloading chromedriver version: ' + latest_version)

        if system == "Windows":
            url = "https://chromedriver.storage.googleapis.com/{}/chromedriver_win32.zip".format(
                latest_version
            )
        elif system == "Darwin":
            url = "https://chromedriver.storage.googleapis.com/{}/chromedriver_mac64.zip".format(
                latest_version
            )
        elif system == "Linux":
            url = "https://chromedriver.storage.googleapis.com/{}/chromedriver_linux64.zip".format(
                latest_version
            )

        try:
            response = urlopen(
                url, context=ssl.SSLContext(ssl.PROTOCOL_TLS)
            )  # context args for mac
        except ssl.SSLError:
            response = urlopen(url)  # context args for mac
        zip_file_path = os.path.join(
            os.path.dirname(driver_path), os.path.basename(url)
        )
        with open(zip_file_path, 'wb') as zip_file:
            while True:
                chunk = response.read(1024)
                if not chunk:
                    break
                zip_file.write(chunk)

        extracted_dir = os.path.splitext(zip_file_path)[0]
        with zipfile.ZipFile(zip_file_path, "r") as zip_file:
            zip_file.extractall(extracted_dir)
        os.remove(zip_file_path)

        driver = os.listdir(extracted_dir)[0]
        try:
            os.rename(os.path.join(extracted_dir, driver), driver_path)
        #for Windows
        except FileExistsError:
            os.replace(os.path.join(extracted_dir, driver), driver_path)

        os.rmdir(extracted_dir)
        os.chmod(driver_path, 0o755)

    def get_driver(path, headless=False):
        system = platform.system()
        if system == "Windows":
            if not path.endswith(".exe"):
                path += ".exe"
        if not os.path.exists(path):
            Driver.__download_driver(path, system)

        options = webdriver.ChromeOptions()
        options.add_argument("--disable-extensions")
        options.add_argument("--window-size=1280,1024")
        options.add_argument("--log-level=3")
        options.add_experimental_option("prefs", {"profile.default_content_setting_values.geolocation" : 1}) # geolocation permission, 0=Ask, 1=Allow, 2=Deny

        options.add_argument("user-agent=" + Driver.__WEB_USER_AGENT)
        if headless:
            #for this program, headless should only be used for testing or to set-up all the db-fiddles before hand
            options.add_argument("--headless")

        driver_dl_index = 1
        while True:
            try:
                driver = webdriver.Chrome(path, options=options)
                break
            #driver not up to date with Chrome browser, try different ver
            except:
                Driver.__download_driver(path, system, driver_dl_index)
                driver_dl_index += 1
                if driver_dl_index > 2:
                    print(f'Tried downloading the {driver_dl_index} most recent chrome drivers. None match current Chrome browser version')
                    break
        return EventFiringWebDriver(driver, EventListener())
