import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class DOMAnalyzer:

    @staticmethod
    def analyze(application_url: str):

        options = Options()

        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=options)

        try:

            driver.get(application_url)

            # ----------------------------------------
            # Wait for the page to actually render.
            # Many apps (React/Vue/Angular SPAs) load an
            # empty shell first and render via JavaScript,
            # so scraping immediately returns nothing.
            # ----------------------------------------

            WebDriverWait(driver, 20).until(
                lambda d: d.execute_script(
                    "return document.readyState"
                ) == "complete"
            )

            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        "input, button, a, select, textarea"
                    ))
                )
            except Exception:
                # Page has no interactive elements or is very
                # slow — continue with whatever is present.
                pass

            # Give client-side frameworks a moment to finish
            # rendering attribute values (ids, names, etc.).
            time.sleep(2)

            dom = {
                "title": driver.title,
                "url": driver.current_url,
                "inputs": [],
                "buttons": [],
                "links": [],
                "dropdowns": [],
                "textareas": [],
                "checkboxes": [],
                "radio_buttons": []
            }

            # -----------------------------
            # Inputs
            # -----------------------------

            for element in driver.find_elements(By.TAG_NAME, "input"):
                dom["inputs"].append({
                    "id": element.get_attribute("id"),
                    "name": element.get_attribute("name"),
                    "type": element.get_attribute("type"),
                    "placeholder": element.get_attribute("placeholder"),
                    "class": element.get_attribute("class")
                })

            # -----------------------------
            # Buttons
            # -----------------------------

            for element in driver.find_elements(By.TAG_NAME, "button"):
                dom["buttons"].append({
                    "text": element.text,
                    "id": element.get_attribute("id"),
                    "class": element.get_attribute("class"),
                    "type": element.get_attribute("type")
                })

            # -----------------------------
            # Links
            # -----------------------------

            for element in driver.find_elements(By.TAG_NAME, "a"):
                dom["links"].append({
                    "text": element.text,
                    "href": element.get_attribute("href")
                })

            # -----------------------------
            # Dropdowns
            # -----------------------------

            for element in driver.find_elements(By.TAG_NAME, "select"):
                dom["dropdowns"].append({
                    "id": element.get_attribute("id"),
                    "name": element.get_attribute("name")
                })

            # -----------------------------
            # Textareas
            # -----------------------------

            for element in driver.find_elements(By.TAG_NAME, "textarea"):
                dom["textareas"].append({
                    "id": element.get_attribute("id"),
                    "name": element.get_attribute("name")
                })

            # -----------------------------
            # Checkboxes
            # -----------------------------

            for element in driver.find_elements(
                By.XPATH, "//input[@type='checkbox']"
            ):
                dom["checkboxes"].append({
                    "id": element.get_attribute("id"),
                    "name": element.get_attribute("name")
                })

            # -----------------------------
            # Radio Buttons
            # -----------------------------

            for element in driver.find_elements(
                By.XPATH, "//input[@type='radio']"
            ):
                dom["radio_buttons"].append({
                    "id": element.get_attribute("id"),
                    "name": element.get_attribute("name")
                })

            return dom

        finally:

            driver.quit()
