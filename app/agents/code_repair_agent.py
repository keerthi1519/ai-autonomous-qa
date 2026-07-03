from app.core.ai_client import ai_client


class CodeRepairAgent:

    @staticmethod
    def repair(code: str, error: str) -> str:

        prompt = f"""
You are an expert Python engineer specializing in Selenium and Pytest.

A Selenium test file contains Python syntax errors.

Your task is to repair ONLY the syntax errors.

Rules:
1. Do NOT change the business logic.
2. Do NOT modify test names.
3. Do NOT modify assertions unless required to fix syntax.
4. Preserve imports whenever possible.
5. Return ONLY valid Python source code.
6. Do NOT use markdown.
7. Do NOT wrap the response inside ```python```.
8. Ensure the returned code passes Python AST parsing.

Syntax Error:
{error}

Python Code:
{code}
"""

        return ai_client.generate_text(prompt)