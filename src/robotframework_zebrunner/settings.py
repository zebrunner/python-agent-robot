import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import dotenv
import yaml
from pydantic import BaseModel
from pydantic.utils import deep_update

PREFIX = "reporting"
logger = logging.getLogger(__name__)


class TestRunSettings(BaseModel):
    """
    A class that inherit from BaseModel and represents test_run settings.
    """

    display_name: Optional[str] = None
    build: Optional[str] = None
    environment: Optional[str] = None
    context: Optional[str] = None


class ServerSettings(BaseModel):
    """
    A class that inherit from BaseModel and represents server settings.
    """

    hostname: str
    access_token: str


class NotificationsSettings(BaseModel):
    """
    A class that inherit from BaseModel and represents notifications settings.
    """

    slack_channels: Optional[str] = None
    ms_teams_channels: Optional[str] = None
    emails: Optional[str] = None
    notify_on_each_failure: bool = False


class MilestoneSettings(BaseModel):
    """
    A class that inherit from BaseModel and represents milestone settings.
    """

    id: Optional[str]
    name: Optional[str]


class ZebrunnerSettings(BaseModel):
    """
    Zebrunner settings provided by launcher
    """

    @property
    def desired_capabilities(self) -> Optional[dict]:
        try:
            return json.loads(self.capabilities)  # type: ignore
        except ValueError:
            logger.log(logging.WARN, "Failed to serialize ZEBRUNNER_CAPABILITIES option")
            return None

    capabilities: Optional[str] = None
    hub_url: Optional[str] = None


class Settings(BaseModel):
    """
    A class that inherit from BaseModel and represents some settings.
    """

    enabled: bool = True
    project_key: str = "DEF"
    send_logs: bool = True
    server: ServerSettings
    run: TestRunSettings = TestRunSettings()
    notification: Optional[NotificationsSettings] = None
    milestone: Optional[MilestoneSettings] = None
    zebrunner: Optional[ZebrunnerSettings] = None


def _list_settings(model: Type[BaseModel]) -> List:
    """
    Extracts and returns a list with all model fields. Also goes deeper into fields that extend from BaseModel and
    extract theirs fields too.

    Args:
        model (Type[BaseModel]): A model to list its fields.

    Returns:
        setting_names (list): List with all model fields.
    """
    setting_names = []
    for field_name, field_value in model.__fields__.items():
        field_list = [field_name]
        if issubclass(field_value.type_, BaseModel):
            inner_fields = _list_settings(field_value.type_)
            inner_fields = [field_list + inner for inner in inner_fields]
            setting_names += inner_fields
        else:
            setting_names.append(field_list)

    return setting_names


def _put_by_path(settings_dict: dict, path: List[str], value: Any) -> None:
    """
    Creates a dictionary with the first item in path as key and set value as its value if the amount of
    items in path is one.
    Otherwise, creates a set of nested dictionaries, with the first item in path at the top of the head.

    Args:
        settings_dict (dict): Dictionary with settings fields.
        path (List[str]): Strings to be set as dictionary keys.
        value: Some value to be set to las dictionary key.
    """
    if len(path) == 1:
        settings_dict[path[0]] = value
    else:
        current_dict = settings_dict.get(path[0], {})
        _put_by_path(current_dict, path[1:], value)
        settings_dict[path[0]] = current_dict


def _get_by_path(settings_dict: dict, path: List[str], default_value: Any = None) -> Any:
    """
    Returns the value of first path item key if path list has only one element.
    Otherwise, returns values of every key in path list recursively.

    Args:
        settings_dict (dict):
        path (List[str]):
        default_value (optional):
    """
    if len(path) == 1:
        return settings_dict.get(path[0], default_value)
    else:
        inner_dict = settings_dict.get(path[0], {})
        return _get_by_path(inner_dict, path[1:], default_value)


def _load_env(path_list: List[List[str]]) -> dict:
    """"""
    dotenv.load_dotenv(".env")
    settings: Dict[str, Any] = {}
    for path in path_list:
        env_name = "_".join(path).upper()
        env_variable = os.getenv(env_name)
        prefix_env_name = "_".join([PREFIX] + path).upper()
        prefix_env_value = os.getenv(prefix_env_name)
        if prefix_env_value is not None:
            env_variable = prefix_env_value

        if env_variable is not None:
            _put_by_path(settings, path, env_variable)

    return settings


def _load_yaml(path_list: List[List[str]]) -> Dict[str, Any]:
    settings: Dict[str, Any] = {}
    filename = Path("agent.yaml")
    if not filename.exists():
        filename = Path("agent.yml")
        if not filename.exists():
            return settings

    yaml_settings = yaml.safe_load(filename.read_text())
    for setting_path in path_list:
        yaml_path = [name.replace("_", "-") for name in setting_path]
        setting_value = _get_by_path(yaml_settings, yaml_path)

        prefix_yaml_path = [name.replace("_", "-") for name in [PREFIX] + setting_path]
        prefix_settings_value = _get_by_path(yaml_settings, prefix_yaml_path)
        if prefix_settings_value is not None:
            setting_value = prefix_settings_value

        if setting_value is not None:
            _put_by_path(settings, setting_path, setting_value)

    return settings


def load_settings() -> Settings:
    settings_path_list = _list_settings(Settings)
    settings: Dict[str, Any] = {}
    yaml_settings = _load_yaml(settings_path_list)
    settings = deep_update(settings, yaml_settings)
    env_settings = _load_env(settings_path_list)
    settings = deep_update(settings, env_settings)
    return Settings(**settings)
