import logging
import sys
from pathlib import Path
from typing import Optional, Union

from .api.client import ZebrunnerAPI
from .api.models import ArtifactReferenceModel, LabelModel, PlatformModel
from .context import zebrunner_context
from .errors import AgentApiError, AgentError
from .listener import ZebrunnerListener
from .tcm.test_rail import TestRail
from .tcm.xray import Xray
from .tcm.zephyr import Zephyr


class ZebrunnerLib:
    if not ("robotframework_zebrunner.ZebrunnerListener" in sys.argv):
        ROBOT_LIBRARY_LISTENER = ZebrunnerListener()

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def attach_test_screenshot(self, path: Union[str, Path]) -> None:
        """
        Send screenshot to zebrunner and attach it to test
        """
        if not zebrunner_context.test_is_active:
            raise AgentError("There is no active test to attach screenshot")

        try:
            api = ZebrunnerAPI(
                zebrunner_context.settings.server.hostname,
                zebrunner_context.settings.server.access_token,
            )
            api.send_screenshot(
                zebrunner_context.test_run_id, zebrunner_context.test_id, path
            )
        except AgentApiError as e:
            logging.error("Failed to attach test screenshot", exc_info=e)

    def attach_test_artifact(self, path: Union[str, Path]) -> None:
        """
        Send artifact to zebrunner and attach it to test. Artifact is any file from disk
        """
        if not zebrunner_context.test_is_active:
            raise AgentError("There is no active test to attach artifact")

        try:
            api = ZebrunnerAPI(
                zebrunner_context.settings.server.hostname,
                zebrunner_context.settings.server.access_token,
            )
            api.send_artifact(
                path, zebrunner_context.test_run_id, zebrunner_context.test_id
            )
        except AgentApiError as e:
            logging.error("Failed to attach test artifact", exc_info=e)

    def attach_test_run_artifact(self, path: Union[str, Path]) -> None:
        """
        Send artifact to zebrunner and attach it to test run. Artifact is any file from disk
        """
        if not zebrunner_context.test_run_is_active:
            raise AgentError("There is no active test run to attach artifact")

        try:
            api = ZebrunnerAPI(
                zebrunner_context.settings.server.hostname,
                zebrunner_context.settings.server.access_token,
            )
            api.send_artifact(path, zebrunner_context.test_run_id)
        except AgentApiError as e:
            logging.error("Failed to attach test run artifact", exc_info=e)

    def attach_test_artifact_reference(self, name: str, ref: str) -> None:
        """
        Send artifact reference to zebrunner and attach it to test. Artifact reference is a URL
        """
        if not zebrunner_context.test_is_active:
            raise AgentError("There is no active test to attach artifact reference")

        try:
            api = ZebrunnerAPI(
                zebrunner_context.settings.server.hostname,
                zebrunner_context.settings.server.access_token,
            )
            api.send_artifact_references(
                [ArtifactReferenceModel(name=name, value=ref)],
                zebrunner_context.test_run_id,
                zebrunner_context.test_id,
            )
        except AgentApiError as e:
            logging.error("Failed to attach test artifact reference", exc_info=e)

    def attach_test_run_artifact_reference(self, name: str, ref: str) -> None:
        """
        Send artifact reference to zebrunner and attach it to test run. Artifact reference is a URL
        """
        if not zebrunner_context.test_run_is_active:
            raise AgentError("There is no active test run to attach artifact reference")

        try:
            api = ZebrunnerAPI(
                zebrunner_context.settings.server.hostname,
                zebrunner_context.settings.server.access_token,
            )
            api.send_artifact_references(
                [ArtifactReferenceModel(name=name, value=ref)],
                zebrunner_context.test_run_id,
            )
        except AgentApiError as e:
            logging.error("Failed to attach test run artifact reference", exc_info=e)

    def attach_test_label(self, name: str, value: str) -> None:
        """
        Attach label to test in zebrunner
        """
        if not zebrunner_context.test_is_active:
            raise AgentError("There is no active test to attach label")

        try:
            api = ZebrunnerAPI(
                zebrunner_context.settings.server.hostname,
                zebrunner_context.settings.server.access_token,
            )
            api.send_labels(
                [LabelModel(key=name, value=value)],
                zebrunner_context.test_run_id,
                zebrunner_context.test_id,
            )
        except AgentApiError as e:
            logging.error("Failed to attach label to test", exc_info=e)

    def attach_test_run_label(self, name: str, value: str) -> None:
        """
        Attach label to test run in zebrunner
        """
        if not zebrunner_context.test_run_is_active:
            raise AgentError("There is no active test run to attach label")

        try:
            api = ZebrunnerAPI(
                zebrunner_context.settings.server.hostname,
                zebrunner_context.settings.server.access_token,
            )
            api.send_labels(
                [LabelModel(key=name, value=value)], zebrunner_context.test_run_id
            )
        except AgentApiError as e:
            logging.error("Failed to attach label to test run", exc_info=e)

    def current_test_revert_registration(self) -> None:
        if not zebrunner_context.test_is_active:
            raise AgentError("There is not active test to revert")

        settings = zebrunner_context.settings
        try:
            api = ZebrunnerAPI(settings.server.hostname, settings.server.access_token)
            api.reverse_test_registration(zebrunner_context.test_run_id, zebrunner_context.test_id)
            zebrunner_context.is_reverted = True
        except AgentApiError as e:
            logging.error("Failed to revert test registration", exc_info=e)
    
    def current_test_run_set_build(self, build: str) -> None:
        if not build.strip():
            raise AgentError("Build must not be empty")

        if not zebrunner_context.test_run_is_active:
            raise AgentError("There is not active test run to set build")

        settings = zebrunner_context.settings
        try:
            api = ZebrunnerAPI(settings.server.hostname, settings.server.access_token)
            api.patch_test_run_build(zebrunner_context.test_run_id, build)
        except AgentApiError as e:
            logging.error("Failed to set build", exc_info=e)

    def current_test_run_set_locale(self, locale: str) -> None:
        if not locale.strip():
            raise AgentError("Locale must no be empty")
        if not zebrunner_context.test_run_is_active:
            raise AgentError("There is not active test run to set locale")

        label = "com.zebrunner.app/sut.locale"
        settings = zebrunner_context.settings
        try:
            api = ZebrunnerAPI(settings.server.hostname, settings.server.access_token)
            api.send_labels([LabelModel(key=label, value=locale)], zebrunner_context.test_run_id, None)
        except AgentApiError as e:
            logging.error("failed to set locale", exc_info=e)

    def current_test_run_set_platform(self, name: str) -> None:
        if not name.strip():
            raise AgentError("Platform must not be empty")

        self.current_test_run_set_platform_version(name, None)

    def current_test_run_set_platform_version(self, name: str, version: Optional[str]) -> None:
        if not name.strip():
            raise AgentError("Platform must not be empty")
        if not zebrunner_context.test_run_is_active:
            raise AgentError("There is not active test run to set platform")

        settings = zebrunner_context.settings
        try:
            api = ZebrunnerAPI(settings.server.hostname, settings.server.access_token)
            api.set_test_run_platform(
                zebrunner_context.test_run_id,
                PlatformModel(name=name, version=version),
            )
        except AgentApiError as e:
            logging.error("Failed to set platform", exc_info=e)

    def test_rail_disable_sync(self) -> None:
        TestRail.disable_sync()

    def test_rail_enable_real_time_sync(self) -> None:
        TestRail.enable_real_time_sync()

    def test_rail_include_all_test_cases_in_new_run(self) -> None:
        TestRail.include_all_test_cases_in_new_run()

    def test_rail_set_suite_id(self, suite_id: str) -> None:
        TestRail.set_suite_id(suite_id)

    def test_rail_set_run_id(self, run_id: str) -> None:
        TestRail.set_run_id(run_id)

    def test_rail_set_run_name(self, run_name: str) -> None:
        TestRail.set_run_name(run_name)

    def test_rail_set_milestone(self, milestone: str) -> None:
        TestRail.set_milestone(milestone)

    def test_rail_set_assignee(self, assignee: str) -> None:
        TestRail.set_assignee(assignee)

    def test_rail_set_case_id(self, test_case_id: str) -> None:
        TestRail.set_case_id(test_case_id)
    
    def xray_disable_sync(self) -> None:
        Xray.disable_sync()

    def xray_enable_real_time_sync(self) -> None:
        Xray.enable_real_time_sync()

    def xray_set_execution_key(self, execution_key: str) -> None:
        Xray.set_execution_key(execution_key)

    def xray_set_test_key(self, test_key: str) -> None:
        Xray.set_test_key(test_key)
    
    def zephyr_disable_sync(self) -> None:
        Zephyr.disable_sync()

    def zephyr_enable_real_time_sync(self) -> None:
        Zephyr.enable_real_time_sync()

    def zephyr_set_test_cycle_key(self, key: str) -> None:
        Zephyr.set_test_cycle_key(key)

    def zephyr_set_jira_project_key(self, key: str) -> None:
        Zephyr.set_jira_project_key(key)

    def zephyr_set_test_case_key(self, key: str) -> None:
        Zephyr.set_test_case_key(key)
