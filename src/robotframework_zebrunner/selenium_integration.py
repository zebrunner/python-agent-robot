import copy
import logging
from typing import Dict, List, Optional

from .api.client import ZebrunnerAPI
from .api.models import FinishTestSessionModel, StartTestSessionModel
from .settings import Settings

logger = logging.getLogger(__name__)


class SeleniumSession:
    zebrunner_id: Optional[str]
    id: str
    tests: List[int]

    def __init__(self, id: str, tests: List[int]) -> None:
        self.id = id
        self.tests = tests
        self.zebrunner_id = None


class SeleniumSessionManager:
    def __init__(self, api: ZebrunnerAPI, test_run_id: int) -> None:
        self._active_tests: List[int] = []
        self._active_sessions: Dict[str, SeleniumSession] = {}
        self._api = api
        self._test_run_id = test_run_id

    def start_session(self, session_id: str, capabilities: dict, desired_capabilities: dict) -> None:
        session = SeleniumSession(session_id, copy.copy(self._active_tests))
        self._active_sessions[session_id] = session

        start_session_model = StartTestSessionModel(
            session_id=session_id, 
            desired_capabilities=desired_capabilities, 
            capabilities=capabilities, 
            test_ids=session.tests
        )
        zebrunner_session_id = self._api.start_test_session(self._test_run_id, start_session_model)

        if zebrunner_session_id:
            session.zebrunner_id = zebrunner_session_id

    def finish_session(self, session_id: str) -> None:
        session = self._active_sessions[session_id]
        if session.zebrunner_id and self._test_run_id:
            finish_session_model = FinishTestSessionModel(test_ids=session.tests)
            self._api.finish_test_session(self._test_run_id, session.zebrunner_id, finish_session_model)
        del self._active_sessions[session_id]

    def finish_all_sessions(self) -> None:
        for session_id in list(self._active_sessions.keys()):
            self.finish_session(session_id)

    def add_test(self, test_id: int) -> None:
        self._active_tests.append(test_id)
        for _, session in self._active_sessions.items():
            session.tests.append(test_id)
    
    def remove_test(self, test_id: int) -> None:
        self._active_tests.remove(test_id)


def inject_driver(settings: Settings, api: ZebrunnerAPI, test_run_id: int) -> SeleniumSessionManager:
    try:
        from selenium.webdriver.remote.webdriver import WebDriver

        session_manager = SeleniumSessionManager(api, test_run_id)
        base_init = WebDriver.__init__
        base_quit = WebDriver.quit

        def init(  # type: ignore
            session: WebDriver,
            command_executor: str = "http://127.0.0.1:4444/wd/hub",
            desired_capabilities: dict = None,
            browser_profile=None,
            proxy=None,
            keep_alive: bool = False,
            file_detector=None,
            options=None,
        ) -> None:  # type: ignore
            # Override capabilities and command_executor with new ones provided by zebrunner.
            caps = copy.deepcopy(desired_capabilities)
            if settings.zebrunner:
                zeb_settings = settings.zebrunner
                if zeb_settings.hub_url:
                    command_executor = zeb_settings.hub_url
                if zeb_settings.desired_capabilities and caps:
                    caps.update(zeb_settings.desired_capabilities)

            base_init(
                session,
                command_executor,
                caps,
                browser_profile,
                proxy,
                keep_alive,
                file_detector,
                options,
            )
            session_manager.start_session(session.session_id, session.capabilities, desired_capabilities or {}) # type: ignore

        def quit(session) -> None:  # type: ignore
            session_manager.finish_session(session.session_id)
            base_quit(session)

        WebDriver.__init__ = init # type: ignore
        WebDriver.quit = quit # type: ignore

    except ImportError:
        logger.warning("Selenium library is not installed.")
    
    return session_manager
