from app.core.ai_client import ai_client


class CodeRepairAgent:
    """
    Repairs Selenium test scripts that contain Python syntax errors.

    Thin wrapper around ai_client.repair_python(), which builds the
    repair prompt, strips markdown fences from the response, and
    rejects empty results.
    """

    @staticmethod
    def repair(code: str, error: str) -> str:
        return ai_client.repair_python(code, error)
