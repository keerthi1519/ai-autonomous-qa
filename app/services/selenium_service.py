import os

from app.schemas.selenium_schema import SeleniumSuite


class SeleniumService:

    OUTPUT_DIR = "generated_tests/selenium"

    @staticmethod
    def save(
        suite: SeleniumSuite
    ):

        os.makedirs(
            SeleniumService.OUTPUT_DIR,
            exist_ok=True
        )

        print("\n===== Saving Selenium Tests =====")
        print(suite)
        print("=================================\n")

        for test in suite.tests:

            file_path = os.path.join(
                SeleniumService.OUTPUT_DIR,
                test.filename
            )

            print(f"Writing: {file_path}")

            with open(
                file_path,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(test.code)