from typing import Optional

from pydantic.error_wrappers import ValidationError

from .settings import load_settings


class ZebrunnerContext:
    def __init__(self) -> None:
        self.test_run_id: Optional[int] = None
        self.test_id: Optional[int] = None
        self.is_reverted = False
        try:
            self.settings = load_settings()
        except ValidationError:
            self.settings = None  # type: ignore

    @property
    def is_configured(self) -> bool:
        return self.settings is not None

    @property
    def test_is_active(self) -> bool:
        return self.is_configured and self.test_run_is_active and self.test_id is not None

    @property
    def test_run_is_active(self) -> bool:
        return self.is_configured and self.test_run_id is not None


zebrunner_context = ZebrunnerContext()
