

from datetime import datetime, timedelta
import logging
from typing import List, Optional

import httpx

from .api.client import ZebrunnerAPI
from .api.models import LogRecordModel


class LogBuffer:
    logs: List[LogRecordModel]
    last_push: datetime
    test_run_id: Optional[int]
    api: ZebrunnerAPI

    def __init__(self, api: ZebrunnerAPI, test_run_id: Optional[int]) -> None:
        self.logs = []
        self.last_push = datetime.utcnow()
        self.api = api
        self.test_run_id = test_run_id

    def add_log(self, log: LogRecordModel) -> None:
        if datetime.utcnow() - self.last_push >= timedelta(seconds=1):
            self.push_logs()

        self.logs.append(log)

    def push_logs(self) -> None:
        try:
            if self.test_run_id:
                self.api.send_logs(self.test_run_id, self.logs)
        except httpx.HTTPError as e:
            logging.error("Failed to send logs to zebrunner", exc_info=e)
        finally:
            self.logs = []
            self.last_push = datetime.utcnow()
