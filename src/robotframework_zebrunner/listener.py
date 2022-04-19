import json
import logging
from typing import List, Optional

from pydantic import ValidationError
from robot import running, result
from robot.libraries.BuiltIn import BuiltIn

from .api.client import ZebrunnerAPI
from .api.models import FinishTestModel, StartTestModel, StartTestRunModel, TestStatus
from .api.models import (
    MilestoneModel,
    NotificationTargetModel,
    NotificationsModel,
    NotificationsType,
    TestRunConfigModel,
)
from .ci_loaders import resolve_ci_context
from .selenium_integration import SeleniumSessionManager, inject_driver
from .settings import Settings, load_settings


class ZebrunnerListener:
    ROBOT_LISTENER_API_VERSION = 3

    test_run_id: Optional[int]
    test_id: Optional[int]
    settings: Optional[Settings]
    session_manager: Optional[SeleniumSessionManager]

    def __init__(self) -> None:
        self.test_run_id = None
        self.test_id = None
        try:
            self.settings = load_settings()
        except ValidationError as e:
            logging.error("Failed to load zebrunner config", exc_info=e)
            self.settings = None
            return

        server_config = self.settings.server
        self.api = ZebrunnerAPI(server_config.hostname, server_config.access_token)
        self.api.auth()

    def _path_run_id(self, test_run: StartTestRunModel):
        try:
            builtin = BuiltIn()
            builtin.import_library("pabot.PabotLib")
            pabot = builtin.get_library_instance("pabot.PabotLib")
            pabot.acquire_lock("zebrunner")
            if pabot.get_parallel_value_for_key("ZEBRUNNER_ID"):
                zebrunner_id = pabot.get_parallel_value_for_key("ZEBRUNNER_ID")
                run_context = {"mode": "APPEND", "testRunUuid": zebrunner_id}
                run_context_str = json.dumps(run_context)
                rerun_tests = self.api.get_rerun_tests(run_context_str)
                test_run.uuid = rerun_tests.test_run_uuid
            else:
                pabot.set_parallel_value_for_key("ZEBRUNNER_ID", test_run.uuid)
        finally:
            pabot.release_lock("zebrunner")

    def _is_pabot_enabled(self) -> bool:
        try:
            builtin = BuiltIn()
            builtin.import_library("pabot.PabotLib")

            for key in builtin.get_variables(True):
                if key.startswith("PABOT"):
                    return True
        except RuntimeError as e:
            return False

        return False

    def start_suite(self, data: running.TestSuite, result: result.TestSuite) -> None:
        if not self.settings:
            return

        display_name = self.settings.run.display_name if self.settings.run else ""
        start_run = StartTestRunModel(
            name=display_name or data.name,
            framework="robotframework",
            config=TestRunConfigModel(
                environment=self.settings.run.environment,
                build=self.settings.run.build,
            ),
        )

        if self._is_pabot_enabled():
            self._path_run_id(start_run)

        if self.settings.milestone:
            start_run.milestone = MilestoneModel(
                id=self.settings.milestone.id,
                name=self.settings.milestone.name,
            )

        if self.settings.notification:
            notification = self.settings.notification
            targets: List[NotificationTargetModel] = []
            if notification.emails:
                targets.append(
                    NotificationTargetModel(
                        type=NotificationsType.EMAIL_RECIPIENTS,
                        value=notification.emails,
                    )
                )

            if notification.slack_channels:
                targets.append(
                    NotificationTargetModel(
                        type=NotificationsType.SLACK_CHANNELS,
                        value=notification.slack_channels,
                    )
                )

            if notification.ms_teams_channels:
                targets.append(
                    NotificationTargetModel(
                        type=NotificationsType.MS_TEAMS_CHANNELS,
                        value=notification.ms_teams_channels,
                    )
                )

            start_run.notifications = NotificationsModel(
                notify_on_each_failure=self.settings.notification.notify_on_each_failure,
                targets=targets,
            )

        start_run.ci_context = resolve_ci_context()

        self.test_run_id = self.api.start_test_run(self.settings.project_key, start_run)
        if self.test_run_id:
            self.session_manager = inject_driver(
                self.settings, self.api, self.test_run_id
            )

    def end_suite(self, name: str, attributes: dict) -> None:
        if not self.settings:
            return

        if self.test_run_id:
            self.api.finish_test_run(self.test_run_id)
            if self.session_manager:
                self.session_manager.finish_all_sessions()

    def start_test(self, data: running.TestCase, result: result.TestCase) -> None:
        if not self.settings:
            return

        if self.test_run_id:
            start_test = StartTestModel(
                name=data.name,
                class_name=data.longname,
                test_case=data.longname,
                method_name=data.name,
            )
            self.test_id = self.api.start_test(self.test_run_id, start_test)

        if self.session_manager and self.test_id:
            self.session_manager.add_test(self.test_id)

    def end_test(self, data: running.TestCase, attributes: result.TestCase) -> None:
        if not self.settings:
            return

        if self.test_id and self.test_run_id:
            if self.session_manager:
                self.session_manager.remove_test(self.test_id)

            status = TestStatus.FAILED
            if attributes.status == "PASS":
                status = TestStatus.PASSED
            elif attributes.status == "FAIL":
                status = TestStatus.FAILED
            else:
                status = TestStatus.SKIPPED

            finish_test = FinishTestModel(result=status.value)
            self.api.finish_test(self.test_run_id, self.test_id, finish_test)


class ZebrunnerLib:
    ROBOT_LIBRARY_LISTENER = ZebrunnerListener()
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
