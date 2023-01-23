import logging

from ..api.client import ZebrunnerAPI
from ..api.models import LabelModel
from ..context import zebrunner_context


class AgentException(Exception):
    pass


class BaseTcm:
    @staticmethod
    def _attach_label(name: str, value: str) -> None:
        api = ZebrunnerAPI(zebrunner_context.settings.server.hostname, zebrunner_context.settings.server.access_token)
        if not zebrunner_context.test_run_is_active:
            logging.error(f"Failed to attach label '{name}: {value}' to test run because it has not been started yet.")
            return
        label = LabelModel(key=name, value=value)
        api.send_labels([label], zebrunner_context.test_run_id, zebrunner_context.test_id)

    @staticmethod
    def _verify_no_tests() -> None:
        if zebrunner_context.test_is_active:
            raise AgentException(
                "The TCM configuration must be provided before start of tests. Hint: move the "
                "configuration to the code block which is executed before all tests."
            )
