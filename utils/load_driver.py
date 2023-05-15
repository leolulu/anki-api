import time
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def get_edge_driver(retries=99, delay=1) -> str:
    """
    Downloads and installs the Microsoft Edge Chromium webdriver.

    :param retries: The number of times to retry before giving up (default 10).
    :param delay: The number of seconds to wait between retries (default 10).

    :raises: WebDriverException if the driver cannot be installed after all retries.
    """
    driver = ""
    for i in range(retries):
        try:
            driver = EdgeChromiumDriverManager().install()
            break
        except:
            if i == retries:
                print("Download driver fail, stop retrying...")
                raise
            print("Download driver fail, Retrying...")
            time.sleep(delay)
    return driver
