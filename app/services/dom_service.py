import json
import logging

from app.agents.dom_analyzer import DOMAnalyzer

logger = logging.getLogger(__name__)


class DOMService:
    """
    Service layer for extracting DOM information
    from the target application.
    """

    @staticmethod
    def analyze(application_url: str) -> dict:

        if not application_url:
            raise ValueError("Application URL is required.")

        application_url = application_url.strip()

        logger.info("=" * 80)
        logger.info("DOM ANALYSIS STARTED")
        logger.info("Application URL : %s", application_url)
        logger.info("=" * 80)

        try:

            dom = DOMAnalyzer.analyze(application_url)

            logger.info("=" * 80)
            logger.info("DOM ANALYSIS COMPLETED")
            logger.info("=" * 80)
            logger.info(json.dumps(dom, indent=4))

            return dom

        except Exception as e:

            logger.exception("DOM Analysis Failed")

            raise Exception(
                f"Unable to analyze website DOM.\n{str(e)}"
            )