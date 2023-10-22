from selenium import webdriver
from selenium_stealth import stealth


def create_driver(debug=False):

    options = webdriver.ChromeOptions()
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

