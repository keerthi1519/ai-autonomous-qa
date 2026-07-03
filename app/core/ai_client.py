import json
import logging
import time
from typing import Type

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIClient:

    def __init__(self):

        logger.info("=" * 80)
        logger.info("Initializing AI Client")
        logger.info("Model : %s", settings.MODEL_NAME)
        logger.info("=" * 80)

        self.client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )

        self.model = settings.MODEL_NAME

    # --------------------------------------------------
    # Normal Text Generation
    # --------------------------------------------------

    def generate(self, prompt: str) -> str:

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content.strip()

    # --------------------------------------------------
    # Structured JSON Generation
    # --------------------------------------------------

    def generate_structured(
        self,
        prompt: str,
        schema: Type[BaseModel] | type[dict]
    ):

        prompt = f"""
Return ONLY valid JSON.

{prompt}
"""

        last_error = None

        for attempt in range(1, 4):

            logger.info("=" * 80)
            logger.info("LLM Attempt %d", attempt)
            logger.info("=" * 80)

            try:

                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=0,
                    response_format={
                        "type": "json_object"
                    },
                    messages=[
                        {
                            "role": "system",
                            "content": """
You are an expert QA Automation Engineer.

Return ONLY valid JSON.

Never return markdown.

Never return explanations.

Never use https://example.com.

Always use the supplied Application URL.

Never invent URLs.
"""
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                text = response.choices[0].message.content.strip()

                logger.info("=" * 80)
                logger.info("RAW RESPONSE")
                logger.info("=" * 80)
                logger.info(text)

                data = json.loads(text)

                if schema is dict:
                    return data

                return schema.model_validate(data)

            except json.JSONDecodeError as e:

                logger.exception("Invalid JSON returned.")
                last_error = e

            except ValidationError as e:

                logger.exception("Schema validation failed.")
                last_error = e

            except Exception as e:

                logger.exception("LLM request failed.")
                last_error = e

            time.sleep(1)

        raise Exception(
            f"Failed after 3 attempts.\n{last_error}"
        )

    # --------------------------------------------------
    # Repair Invalid Python
    # --------------------------------------------------

    def repair_python(
        self,
        code: str,
        error: str
    ) -> str:

        repair_prompt = f"""
The following Selenium Python script contains syntax errors.

Syntax Error

{error}

Python Code

{code}

Instructions

1. Fix ONLY the syntax errors.
2. Do NOT change the test logic.
3. Do NOT change imports.
4. Do NOT change assertions.
5. Do NOT change the application URL.
6. Return ONLY valid Python.
7. Do NOT use markdown.
8. Do NOT explain anything.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": repair_prompt
                }
            ]
        )

        repaired = response.choices[0].message.content

        repaired = (
            repaired
            .replace("```python", "")
            .replace("```", "")
            .strip()
        )

        if not repaired:
            raise Exception(
                "LLM returned an empty repaired script."
            )

        logger.info("=" * 80)
        logger.info("REPAIRED PYTHON")
        logger.info("=" * 80)
        logger.info(repaired)

        return repaired


ai_client = AIClient()