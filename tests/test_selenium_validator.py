"""Unit tests for the Selenium script quality validator."""

from app.agents.selenium_generator import SeleniumGenerator

APP_URL = "https://demo.example-app.com/"
DOM = {"inputs": [{"name": "username"}], "buttons": [{"text": "Login"}]}

GOOD_SCRIPT = f'''
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pytest


def test_login():
    options = Options()
    driver = webdriver.Chrome(options=options)
    try:
        driver.get("{APP_URL}")
        el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        assert el.is_displayed()
    finally:
        driver.quit()
'''


def validate(code):
    return SeleniumGenerator.validate_script_quality(code, APP_URL, DOM)


class TestScriptValidator:

    def test_good_script_passes(self):
        assert validate(GOOD_SCRIPT) == []

    def test_missing_url_rejected(self):
        code = GOOD_SCRIPT.replace(APP_URL, "https://other-site.com/")
        assert any("Application URL" in e for e in validate(code))

    def test_placeholder_rejected(self):
        code = GOOD_SCRIPT.replace('"username"', '"REPLACE_USERNAME"')
        assert any("Placeholder" in e for e in validate(code))

    def test_forbidden_url_rejected(self):
        code = GOOD_SCRIPT + '\n# see http://localhost:3000\n'
        assert any("localhost" in e for e in validate(code))

    def test_hallucinated_feature_rejected(self):
        code = GOOD_SCRIPT.replace("test_login", "test_checkout")
        assert any("checkout" in e for e in validate(code))

    def test_fragile_locator_rejected(self):
        code = GOOD_SCRIPT.replace(
            '(By.NAME, "username")',
            '(By.XPATH, "//*[contains(text(), \'Login\')]")'
        )
        assert any("normalize-space" in e for e in validate(code))

    def test_module_level_code_rejected(self):
        code = (
            "from selenium import webdriver\n"
            "import pytest\n"
            f'driver = webdriver.Chrome()\n'
            f'driver.get("{APP_URL}")\n'
            "WebDriverWait = None\n"
            "assert driver.title\n"
            "driver.quit()\n"
        )
        errors = validate(code)
        assert any("module level" in e for e in errors)
        assert any("test function" in e.lower() for e in errors)

    def test_missing_driver_quit_rejected(self):
        code = GOOD_SCRIPT.replace("driver.quit()", "pass")
        assert any("driver.quit()" in e for e in validate(code))
