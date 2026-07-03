from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


class DOMAnalyzer:

    @staticmethod
    def analyze(application_url: str):

        options = Options()

        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)

        driver.get(application_url)

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

        inputs = driver.find_elements(By.TAG_NAME, "input")

        for element in inputs:

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

        buttons = driver.find_elements(By.TAG_NAME, "button")

        for element in buttons:

            dom["buttons"].append({

                "text": element.text,

                "id": element.get_attribute("id"),

                "class": element.get_attribute("class"),

                "type": element.get_attribute("type")

            })

        # -----------------------------
        # Links
        # -----------------------------

        links = driver.find_elements(By.TAG_NAME, "a")

        for element in links:

            dom["links"].append({

                "text": element.text,

                "href": element.get_attribute("href")

            })

        # -----------------------------
        # Dropdowns
        # -----------------------------

        selects = driver.find_elements(By.TAG_NAME, "select")

        for element in selects:

            dom["dropdowns"].append({

                "id": element.get_attribute("id"),

                "name": element.get_attribute("name")

            })

        # -----------------------------
        # Textareas
        # -----------------------------

        textareas = driver.find_elements(By.TAG_NAME, "textarea")

        for element in textareas:

            dom["textareas"].append({

                "id": element.get_attribute("id"),

                "name": element.get_attribute("name")

            })

        # -----------------------------
        # Checkboxes
        # -----------------------------

        checkboxes = driver.find_elements(
            By.XPATH,
            "//input[@type='checkbox']"
        )

        for element in checkboxes:

            dom["checkboxes"].append({

                "id": element.get_attribute("id"),

                "name": element.get_attribute("name")

            })

        # -----------------------------
        # Radio Buttons
        # -----------------------------

        radios = driver.find_elements(
            By.XPATH,
            "//input[@type='radio']"
        )

        for element in radios:

            dom["radio_buttons"].append({

                "id": element.get_attribute("id"),

                "name": element.get_attribute("name")

            })

        driver.quit()

        return dom