import logging
import time

import requests
from requests import Response
from webdriver_manager.core.config import ssl_verify, wdm_progress_bar
from webdriver_manager.core.download_manager import WDMDownloadManager
from webdriver_manager.core.http import HttpClient
from webdriver_manager.core.logger import set_logger
from webdriver_manager.core.utils import show_download_progress
from webdriver_manager.microsoft import EdgeChromiumDriverManager


class MyHttpClientWithProxy(HttpClient):
    def __init__(self):
        super().__init__()

    def get(self, url, params=None, **kwargs) -> Response:
        try:
            resp = requests.get(url=url, verify=ssl_verify(), stream=True, **kwargs)
        except:
            print("内置client下载失败，采用代理client下载...")
            proxies = {
                "http": "http://127.0.0.1:10809",
                "https": "http://127.0.0.1:10809",
            }
            resp = requests.get(url=url, verify=ssl_verify(), stream=True, proxies=proxies, **kwargs)
        self.validate_response(resp)
        if wdm_progress_bar():
            show_download_progress(resp)
        return resp


def get_edge_driver(retries=99, delay=1) -> str:
    """
    Downloads and installs the Microsoft Edge Chromium webdriver.

    :param retries: The number of times to retry before giving up (default 10).
    :param delay: The number of seconds to wait between retries (default 10).

    :raises: WebDriverException if the driver cannot be installed after all retries.
    """
    config_logger()
    driver = ""
    for i in range(retries):
        try:
            driver = EdgeChromiumDriverManager(download_manager=WDMDownloadManager(http_client=MyHttpClientWithProxy())).install()
            break
        except:
            if i == retries:
                print("Download driver fail, stop retrying...")
                raise
            print("Download driver fail, Retrying...")
            time.sleep(delay)
    return driver


def config_logger():
    logger = logging.getLogger("MY_WDM")
    logger.setLevel(logging.ERROR)
    logger.addHandler(logging.StreamHandler())
    set_logger(logger)
