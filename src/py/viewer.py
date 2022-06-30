from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from . import config

def run():
    options = Options()
    options._arguments = [f"-ssb http://localhost:{config.main.web_port}"]
    options.preferences["browser.ssb.enabled"] = True
    driver = webdriver.Firefox(options=options)
    driver.get(f"http://localhost:{config.main.web_port}")
    driver.fullscreen_window()