import json
import logging
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from pprint import pformat
from typing import List, Optional, Union

import httpx
from httpx import Client, Request, Response

from .models import (
    ArtifactReferenceModel,
    AttachTestsToSessionModel,
    FinishTestModel,
    FinishTestSessionModel,
    LabelModel,
    LogRecordModel,
    PlatformModel,
    RerunDataModel,
    StartTestModel,
    StartTestRunModel,
    StartTestSessionModel,
)
from ..errors import AgentApiError
from ..utils import Singleton

logger = logging.getLogger(__name__)


def log_response(response: Response, log_level: int = logging.DEBUG) -> None:
    """Logger customized configuration"""
    request = response.request
    request.read()

    logger.log(
        log_level,
        f"Request {request.method} {request.url}\n"
        f"Headers: \n{pformat(dict(request.headers))}\n\n"
        f"Content: \n{request.content!r}\n\n"
        f"Response Code: {response.status_code}\n"
        f" Content: \n{pformat(response.json())}",
    )


class ZebrunnerAPI(metaclass=Singleton):
    """
    A singleton Zebrunner API representation
    """

    _authenticated = False

    def __init__(self, service_url: str = None, access_token: str = None):
        if service_url and access_token:
            self.service_url = service_url.rstrip("/")
            self.access_token = access_token
            self._client = Client()
            self._auth_token = None
            self._authenticated = False

    def _sign_request(self, request: Request) -> Request:
        """
        Returns a request with the _auth_token set to the authorization request header.
        """
        request.headers["Authorization"] = f"Bearer {self._auth_token}"
        return request

    def auth(self) -> None:
        """
        Validates the user access token with http post method and if it is correct, authenticates the user.
        """
        if not self.access_token or not self.service_url:
            return

        url = f"{self.service_url}/api/iam/v1/auth/refresh"
        try:
            response = self._client.post(url, json={"refreshToken": self.access_token})
        except httpx.RequestError as e:
            raise AgentApiError("Failed to authorize zebrunner agent", e)

        if not response.is_success:
            raise AgentApiError(
                "Failed to authorize zebrunner agent", {"status_code": response.status_code, "body": response.json()}
            )

        self._auth_token = response.json()["authToken"]
        self._client.auth = self._sign_request  # type: ignore
        self._authenticated = True

    def start_test_run(self, project_key: str, body: StartTestRunModel) -> Optional[int]:
        """
        Send POST request creating new test run. Raise ApiAgentException if request failed
        """
        url = f"{self.service_url}/api/reporting/v1/test-runs"

        try:
            response = self._client.post(
                url, params={"projectKey": project_key}, json=body.dict(exclude_none=True, by_alias=True)
            )
        except httpx.RequestError as e:
            raise AgentApiError("Failed to create test run", e)

        if not response.is_success:
            raise AgentApiError(
                "Failed to create test run. Non successful response code",
                {"status_code": response.status_code, "body": response.json()},
            )

        return response.json()["id"]

    def start_test(self, test_run_id: int, body: StartTestModel) -> Optional[int]:
        """
        Send POST request creating new test. Raise AgentApiError in case of any exceptions
        """
        url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/tests"

        try:
            response = self._client.post(url, json=body.dict(exclude_none=True, by_alias=True))
        except httpx.RequestError as e:
            raise AgentApiError("Failed to create test", e)

        if not response.is_success:
            raise AgentApiError(
                "Failed to create test. Non successful response code",
                {"status_code": response.status_code, "body": response.json()},
            )

        return response.json()["id"]

    def update_test(self, test_run_id: int, test_id: int, test: StartTestModel) -> Optional[int]:
        """
        Send PUT request updating some test. Raise AgentApiError in case of any exceptions
        """

        url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/tests/{test_id}/"
        try:
            response = self._client.post(url, json=test.dict(exclude_none=True, by_alias=True))
        except httpx.RequestError as e:
            raise AgentApiError("Failed to update test", e)

        if not response.is_success:
            raise AgentApiError(
                "Failed to update test. Non successful status code",
                {"status_code": response.status_code, "body": response.json()},
            )

        return response.json()["id"]

    def finish_test(self, test_run_id: int, test_id: int, body: FinishTestModel) -> None:
        """
        Send PUT request finishing current test. Raise AgentApiError in case of any exceptions
        """
        url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/tests/{test_id}"

        try:
            response = self._client.put(url, json=body.dict(exclude_none=True, by_alias=True))
        except httpx.RequestError as e:
            raise AgentApiError("Failed to finish test", e)

        if not response.is_success:
            raise AgentApiError(
                "Failed to finish test. Non  successful status code",
                {"status_code": response.status_code, "body": response.json()},
            )

    def finish_test_run(self, test_run_id: int) -> None:
        """
        Send PUT request finishing current test run. Raise AgentApiError in case of any exceptions
        """
        url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}"
        try:
            response = self._client.put(
                url,
                json={"endedAt": (datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(seconds=1)).isoformat()},
            )
        except httpx.RequestError as e:
            raise AgentApiError("Failed to finish test run", e)

        if not response.is_success:
            raise AgentApiError(
                "Failed to finish test run. Non  successful status code",
                {"status_code": response.status_code, "body": response.json()},
            )

    def send_logs(self, test_run_id: int, logs: List[LogRecordModel]) -> None:
        """
        Send POST request uploading logs. Raise AgentApiError in case of any exceptions
        """
        url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/logs"

        body = [x.dict(exclude_none=True, by_alias=True) for x in logs]
        try:
            response = self._client.post(url, json=body)
        except httpx.RequestError as e:
            raise AgentApiError("Failed to send logs", e)

        if not response.is_success:
            raise AgentApiError(
                "Failed to send logs. Non successful status code",
                {"status_code": response.status_code, "body": response.json()},
            )

    def send_screenshot(self, test_run_id: int, test_id: int, image_path: Union[str, Path]) -> None:
        """
        Send screenshot to zebrunner. Raise AgentApiError in case of any exceptions
        """
        url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/tests/{test_id}/screenshots"
        with open(image_path, "rb") as image:
            try:
                response = self._client.post(
                    url,
                    content=image.read(),
                    headers={
                        "Content-Type": "image/png",
                        "x-zbr-screenshot-captured-at": str(round(time.time() * 1000)),
                    },
                )
            except httpx.RequestError as e:
                raise AgentApiError("Failed to send screenshot", e)

            if not response.is_success:
                raise AgentApiError(
                    "Failed to send screenshot. Non successful status code",
                    {"status_code": response.status_code, "body": response.json()},
                )

    def send_artifact(self, filename: Union[str, Path], test_run_id: int, test_id: Optional[int] = None) -> None:
        """
        Send artifact to zebrunner. Attach it to test run if test_id is None else attach it to test.
        Raise AgentApiError in case of any exceptions
        """
        if test_id:
            url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/tests/{test_id}/artifacts"
        else:
            url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/artifacts"

        with open(filename, "rb") as file:
            try:
                response = self._client.post(url, files={"file": file})
            except httpx.RequestError as e:
                raise AgentApiError("Failed to send artifact", e)

            if not response.is_success:
                raise AgentApiError(
                    "Failed to send artifact. Non successful status code",
                    {"status_code": response.status_code, "body": response.json()},
                )

    def send_artifact_references(
        self, references: List[ArtifactReferenceModel], test_run_id: int, test_id: Optional[int] = None
    ) -> None:
        """
        Send artifact reference to zebrunner. Attach it to test run if test_id is None else attach it to test.
        Raise AgentApiError in case of any exceptions
        """
        if test_id:
            url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/tests/{test_id}/artifact-references"
        else:
            url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/artifact-references/"
        json_items = [item.dict(exclude_none=True, by_alias=True) for item in references]

        try:
            response = self._client.put(url, json={"items": json_items})
        except httpx.RequestError as e:
            raise AgentApiError("Failed to send artifact reference", e)

        if not response.is_success:
            raise AgentApiError(
                "Failed to send artifact reference. Non successful status code",
                {"status_code": response.status_code, "body": response.json()},
            )

    def send_labels(self, labels: List[LabelModel], test_run_id: int, test_id: Optional[int] = None) -> None:
        """
        Send labels to zebrunner. Attach it to test run if test_id is None else attach it to test.
        Raise AgentApiError in case of any exceptions
        """
        if test_id:
            url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/tests/{test_id}/labels"
        else:
            url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/labels"
        labels_json = [label.dict(exclude_none=True, by_alias=True) for label in labels]

        try:
            response = self._client.put(url, json={"items": labels_json})
        except httpx.RequestError as e:
            raise AgentApiError("Failed to send labels", e)

        if not response.is_success:
            raise AgentApiError(
                "Failed to send labels. Non successful status code",
                {"status_code": response.status_code, "body": response.json()},
            )

    def start_test_session(self, test_run_id: int, body: StartTestSessionModel) -> Optional[str]:
        """
        Send POST request starting test session. Raise AgentApiError in case of any exceptions
        """
        url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/test-sessions"

        try:
            response = self._client.post(url, json=body.dict(exclude_none=True, by_alias=True))
        except httpx.RequestError as e:
            raise AgentApiError("Failed to start session", e)

        if not response.status_code == 200:
            raise AgentApiError(
                "Failed to start session. Non successful status code",
                {"status_code": response.status_code, "body": response.json()},
            )

        return response.json().get("id")

    def add_tests_to_session(self, test_run_id: int, session_id: str, related_tests: List[int]) -> None:
        """
        Send PUT request attaching new test to test session. Raise AgentApiError in case of any exceptions
        """
        url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/test-sessions/{session_id}"
        body = AttachTestsToSessionModel(test_ids=related_tests)
        try:
            response = self._client.put(url, json=body.dict(exclude_none=True, by_alias=True))
        except httpx.RequestError as e:
            raise AgentApiError("Failed to attach tests to session", e)

        if not response.is_success:
            raise AgentApiError(
                "Failed to attach tests to session. Non successful status code",
                {"status_code": response.status_code, "body": response.json()},
            )

    def finish_test_session(self, test_run_id: int, test_id: str, body: FinishTestSessionModel) -> None:
        """
        Send PUT request finishing test session. Raise AgentApiError in case of any exceptions
        """
        url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/test-sessions/{test_id}"
        try:
            response = self._client.put(url, json=body.dict(exclude_none=True, by_alias=True))
        except httpx.RequestError as e:
            raise AgentApiError("Failed to start session", e)

        if not response.is_success:
            raise AgentApiError(
                "Failed to finish session. Non successful status code",
                {"status_code": response.status_code, "body": response.json()},
            )

    def get_rerun_tests(self, run_context: str) -> RerunDataModel:
        """Exchange run context on tests to run. Raise AgentApiError in case of any exceptions"""
        url = f"{self.service_url}/api/reporting/v1/run-context-exchanges"
        run_context_dict = json.loads(run_context)
        try:
            response = self._client.post(url, json=run_context_dict)
        except httpx.RequestError as e:
            raise AgentApiError("Failed to get rerun tests", e)

        if not response.is_success:
            raise AgentApiError(
                "Failed to get rerun tests. Non successful status code",
                {"status_code": response.status_code, "body": response.json()},
            )

        response_data = response.json()
        for test in response_data["testsToRun"]:
            test["correlationData"] = json.loads(test["correlationData"]) if test["correlationData"] else None

        return RerunDataModel(**response_data)

    def reverse_test_registration(self, test_run_id: int, test_id: int) -> None:
        """Send PUT request reversing test registration. Raise AgentApiError in case of any exceptions"""

        url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/tests/{test_id}"

        try:
            response = self._client.delete(url)
        except httpx.RequestError as e:
            raise AgentApiError("Failed to revert test registration", e)

        if not response.is_success:
            raise AgentApiError(
                "Failed to revert test registration. Non successful status code",
                {"status_code": response.status_code, "body": response.json()},
            )

    def set_test_run_platform(self, run_id: int, platform: PlatformModel) -> None:
        """Update test run platform. Raise AgentApiError in case of any exceptions"""
        url = f"{self.service_url}/api/reporting/v1/test-runs/{run_id}/platform"

        try:
            response = self._client.put(url, json=platform.dict(exclude_none=True, by_alias=True))
        except httpx.RequestError as e:
            raise AgentApiError("failed to set test run platform", e)

        if not response.is_success:
            raise AgentApiError(
                "Failed to set test run platform. Non successful status code",
                {"status_code": response.status_code, "body": response.json()},
            )

    def patch_test_run_build(self, run_id: int, build: str) -> None:
        """Set test run build. Raise AgentApiError in case of any exceptions"""
        url = f"{self.service_url}/api/reporting/v1/test-runs/{run_id}"

        body = {
            "op": "replace",
            "path": "/config/build",
            "value": build,
        }

        try:
            response = self._client.patch(url, json=[body])
        except httpx.RequestError as e:
            raise AgentApiError("failed to patch test run build", e)

        if not response.is_success:
            raise AgentApiError(
                "Failed to patch test run platform. Non successful status code",
                {"status_code": response.status_code, "body": response.json()},
            )

    def close(self) -> None:
        """
        Close the connection pool without block-usage.
        """
        self._client.close()
