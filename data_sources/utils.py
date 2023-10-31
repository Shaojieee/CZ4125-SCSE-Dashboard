from selenium import webdriver
from selenium_stealth import stealth


def create_driver(debug=False):

    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    if debug==False:
        options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(
        options=options
    )
    stealth(driver,
            # user_agent=agent,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    return driver


def get_h_index(citations):
    return sum(x >= i + 1 for i, x in enumerate(sorted(list(citations), reverse=True)))
