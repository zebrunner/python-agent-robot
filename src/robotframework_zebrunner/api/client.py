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
    FinishTestModel,
    FinishTestSessionModel,
    LabelModel,
    LogRecordModel,
    RerunDataModel,
    StartTestModel,
    StartTestRunModel,
    StartTestSessionModel,
)

logger = logging.getLogger(__name__)


def log_response(response: Response, log_level: int = logging.DEBUG) -> None:
    """
    Logger customized configuration.

    Args:
         response (Response): Http response from server to client
         log_level (int): Logging messages which are less severe than level will be ignored.

    Attributes:
        request (Request): Request instance associated to the current response.
    """
    request = response.request
    request.read()

    logger.log(
        log_level,
        f"Request {request.method} {request.url}\n" # type: ignore
        f"Headers: \n{pformat(dict(request.headers))}\n\n"
        f"Content: \n{request.content}\n\n"
        f"Response Code: {response.status_code}\n"
        f" Content: \n{pformat(response.json())}",
    )


class ZebrunnerAPI:
    """
    A class used to represent ZebrunnerAPI using Singleton Pattern which guarantees that will exist only one instance
    of this class.

    Attributes:
        authenticated (bool): True when a valid access token is given.

    """

    authenticated = False

    def __init__(self, service_url: str = None, access_token: str = None):
        """
        Args:
            service_url (str): Url to access Zebrunner API. None by default.
            access_token (str): Access token to access Zebrunner API. None by default.
        """
        if service_url and access_token:
            self.service_url = service_url.rstrip("/")
            self.access_token = access_token
            self._client = Client()
            self._auth_token = None
            self.authenticated = False

    def _sign_request(self, request: Request) -> Request:
        """
        Returns a request with the _auth_token set to the authorization request header.

        Args:
            request (Request):

        Returns:
            request (Request): Request whose authorization request header has been set with _auth_token.

        """
        request.headers["Authorization"] = f"Bearer {self._auth_token}"
        return request

    def auth(self) -> None:
        """
        Validates the user access token with http post method and if it is correct, authenticates the user.

        Attributes:
            url (str): Url to validates the user access token.

        """
        if not self.access_token or not self.service_url:
            return

        url = self.service_url + "/api/iam/v1/auth/refresh"
        try:
            response = self._client.post(url, json={"refreshToken": self.access_token})
        except httpx.RequestError as e:
            logger.warning("Error while sending request to zebrunner.", exc_info=e)
            return

        if response.status_code != 200:
            log_response(response, logging.ERROR)
            return

        self._auth_token = response.json()["authToken"]
        self._client.auth = self._sign_request # type: ignore
        self.authenticated = True

    def start_test_run(self, project_key: str, body: StartTestRunModel) -> Optional[int]:
        """
        Execute an http post with the given project_key and body, which contains StartTestRunModel.
        If everything is OK, returns response id value for test run. Otherwise, logs errors and returns None.

        Args:
            project_key (str):
            body (StartTestRunModel): Entity with TestRun properties.

        Attributes:
            url (str): Url to access api reporting test runs.

        Returns:
            (int, optional): Returns http response 'id' value if http post was OK. Otherwise, returns None.
        """
        url = self.service_url + "/api/reporting/v1/test-runs"

        try:
            response = self._client.post(
                url, params={"projectKey": project_key}, json=body.dict(exclude_none=True, by_alias=True)
            )
        except httpx.RequestError as e:
            logger.warning("Error while sending request to zebrunner.", exc_info=e)
            return None

        if response.status_code != 200:
            log_response(response, logging.ERROR)
            return None

        return response.json()["id"]

    def start_test(self, test_run_id: int, body: StartTestModel) -> Optional[int]:
        """
        Execute an http post with the given test_run_id and body, which contains StartTestModel.
        If everything is OK, returns response id value for test. Otherwise, logs errors and returns None.

        Args:
            test_run_id (int): Number that identifies test_run.
            body (StartTestModel): Entity with Test properties.

        Returns:
            (int, optional): Returns http response 'id' value if http post was OK. Otherwise, returns None.
        """
        url = self.service_url + f"/api/reporting/v1/test-runs/{test_run_id}/tests"

        try:
            response = self._client.post(url, json=body.dict(exclude_none=True, by_alias=True))
        except httpx.RequestError as e:
            logger.warning("Error while sending request to zebrunner.", exc_info=e)
            return None

        if response.status_code != 200:
            log_response(response, logging.ERROR)
            return None

        return response.json()["id"]

    def update_test(self, test_run_id: int, test_id: int, test: StartTestModel) -> Optional[int]:
        url = self.service_url + f"/api/reporting/v1/test-runs/{test_run_id}/tests/{test_id}/"
        try:
            response = self._client.post(url, json=test.dict(exclude_none=True, by_alias=True))
        except httpx.RequestError as e:
            logger.warning("Error while sending request to zebrunner.", exc_info=e)
            return None

        if response.status_code != 200:
            log_response(response, logging.ERROR)
            return None

        return response.json()["id"]

    def finish_test(self, test_run_id: int, test_id: int, body: FinishTestModel) -> None:
        """
        Execute an http put with the given test_run_id, test_id, and body, which contains FinishTestModel.
        If everything is OK, finish the Test. Otherwise, logs errors.

        Args:
            test_run_id (int): Number that identifies test_run.
            test_id (int): Number that identifies test.
            body (FinishTestModel): Entity with FinishTest properties.

        """
        url = self.service_url + f"/api/reporting/v1/test-runs/{test_run_id}/tests/{test_id}"

        try:
            response = self._client.put(url, json=body.dict(exclude_none=True, by_alias=True))
        except httpx.RequestError as e:
            logger.warning("Error while sending request to zebrunner.", exc_info=e)
            return

        if response.status_code != 200:
            log_response(response, logging.ERROR)

    def finish_test_run(self, test_run_id: int) -> None:
        """
        Execute an http put with the given test_run_id.
        If everything is OK, updates endedAt value finishing test_run. Otherwise, logs errors.

        Args:
            test_run_id (int): Number that identifies test_run.
        """
        url = self.service_url + f"/api/reporting/v1/test-runs/{test_run_id}"
        try:
            response = self._client.put(
                url,
                json={"endedAt": (datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(seconds=1)).isoformat()},
            )
        except httpx.RequestError as e:
            logger.warning("Error while sending request to zebrunner.", exc_info=e)
            return

        if response.status_code != 200:
            log_response(response, logging.ERROR)
            return

    def send_logs(self, test_run_id: int, logs: List[LogRecordModel]) -> None:
        """
        Convert a list of LogRecordModel to dictionary format(json) and send them to logs endpoint
        associated with the appropriate test_run_id, for reporting.

        Args:
            test_run_id (int): Number that identifies test_run.
            logs (List[LogRecordModel]): List of LogRecordModel to send for reporting.
        """
        url = self.service_url + f"/api/reporting/v1/test-runs/{test_run_id}/logs"

        body = [x.dict(exclude_none=True, by_alias=True) for x in logs]
        self._client.post(url, json=body)

    def send_screenshot(self, test_run_id: int, test_id: int, image_path: Union[str, Path]) -> None:
        """
        Open an image file by its path, read the binary content and send it to screenshots endpoint
        associated with the appropriate test_id, for reporting.

        Args:
            test_run_id (int): Number that identifies test_run.
            test_id (int): Number that identifies test.
            image_path (Union[str,Path)]: Path to identify image location in directory structure.

        Raises:
            FileNotFoundError: If screenshot file is not reachable.

        """
        url = self.service_url + f"/api/reporting/v1/test-runs/{test_run_id}/tests/{test_id}/screenshots"
        with open(image_path, "rb") as image:
            self._client.post(
                url,
                content=image.read(),
                headers={"Content-Type": "image/png", "x-zbr-screenshot-captured-at": str(round(time.time() * 1000))},
            )

    def send_artifact(self, filename: Union[str, Path], test_run_id: int, test_id: Optional[int] = None) -> None:
        """
        Open a file by its path, read the binary content and sent it to artifacts endpoint
        associated with the appropriate test_id if one is given.
        Otherwise the artifacts endpoint is the one associated with only the appropriate test_run_id.

        Args:
            filename (Union[str, Path]): Path to identify artifact location in directory structure.
            test_run_id (int): Number that identifies test_run.
            test_id: (int, optional): Number that identifies test.

        Raises:
            FileNotFoundError: If artifact file is not reachable.

        """
        if test_id:
            url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/tests/{test_id}/artifacts"
        else:
            url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/artifacts"
        with open(filename, "rb") as file:
            self._client.post(url, files={"file": file})

    def send_artifact_references(
        self, references: List[ArtifactReferenceModel], test_run_id: int, test_id: Optional[int] = None
    ) -> None:
        """
        Convert a list of ArtifactsReferenceModel to dictionary format(json) and send them to
        test artifact-references endpoint associated with the appropriate test_id if one is given.
        Otherwise the artifact-references endpoint is the one associated with only the appropriate test_run_id.

        Args:
            references (List[ArtifactReferenceModel]): List of artifacts references to send for reporting.
            test_run_id (int): Number that identifies test_run.
            test_id: (int, optional): Number that identifies test.
        """
        if test_id:
            url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/tests/{test_id}/artifact-references"
        else:
            url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/artifact-references/"
        json_items = [item.dict(exclude_none=True, by_alias=True) for item in references]
        self._client.put(url, json={"items": json_items})

    def send_labels(self, labels: List[LabelModel], test_run_id: int, test_id: Optional[int] = None) -> None:
        """
        Convert a list of LabelModel to dictionary format(json) and send them to
        labels endpoint associated with the appropiate test_id if one is given.
        Otherwise, the labels endpoint is the one associated with only the appropriate test_run_id.

        Args:
            labels (List[LabelModel]): List of labels to send for reporting.
            test_run_id (int): Number that identifies test_run.
            test_id: (optional int): Number that identifies test.

        """
        if test_id:
            url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/tests/{test_id}/labels"
        else:
            url = f"{self.service_url}/api/reporting/v1/test-runs/{test_run_id}/labels"
        labels_json = [label.dict(exclude_none=True, by_alias=True) for label in labels]
        self._client.put(url, json={"items": labels_json})

    def start_test_session(self, test_run_id: int, body: StartTestSessionModel) -> Optional[str]:
        """
        Execute an http post with the given test_run_id and body, which contains StartTestSessionModel.
        If everything is OK, returns response id value for test. Otherwise, logs errors and returns None.

        Args:
            test_run_id (int): Number that identifies test_run.
            body (StartTestSessionModel): Entity with TestSession properties.

        Returns:
            (string, optional): Returns http response 'id' value if http post was OK. Otherwise, returns None.
        """
        url = self.service_url + f"/api/reporting/v1/test-runs/{test_run_id}/test-sessions"
        response = self._client.post(url, json=body.dict(exclude_none=True, by_alias=True))
        if not response.status_code == 200:
            log_response(response, logging.ERROR)
            return None

        return response.json().get("id")

    def finish_test_session(self, test_run_id: int, session_id: str, body: FinishTestSessionModel) -> None:
        """
        Execute an http put with the given test_run_id, zebrunner_id and body, which contains FinishTestSessionModel.
        If everything is OK, finish the test_session.

        """
        url = self.service_url + f"/api/reporting/v1/test-runs/{test_run_id}/test-sessions/{session_id}"
        self._client.put(url, json=body.dict(exclude_none=True, by_alias=True))

    def get_rerun_tests(self, run_context: str) -> RerunDataModel:
        """"""
        url = self.service_url + "/api/reporting/v1/run-context-exchanges"
        run_context_dict = json.loads(run_context)
        response = self._client.post(url, json=run_context_dict)
        response_data = response.json()
        for test in response_data["testsToRun"]:
            correlation_data = test["correlationData"]
            if correlation_data is not None:
                test["correlationData"] = json.loads(correlation_data)
        return RerunDataModel(**response_data)

    def close(self) -> None:
        """
        Close the connection pool without block-usage.
        """
        self._client.close()
