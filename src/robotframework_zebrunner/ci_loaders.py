import os
from enum import Enum
from typing import Dict, List, Optional, Type

from .api.models import CiContextModel


class BaseContextLoader:
    """
    A class use as base to load environment variables.
    """

    @staticmethod
    def load_context_variables(prefixes: List[str]) -> Dict[str, str]:
        """
        Returns a dictionary with environment variables that start with one of prefixes.
        """
        env_variable_names = list(filter(lambda name: any([name.startswith(x) for x in prefixes]), os.environ))
        return {key: os.environ[key] for key in env_variable_names}


class CiType(Enum):
    """
    A class that inherit from Enum, used to represent CI constants
    """

    JENKINS = "JENKINS"
    TEAM_CITY = "TEAM_CITY"
    CIRCLE_CI = "CIRCLE_CI"
    TRAVIS_CI = "TRAVIS_CI"
    BAMBOO = "BAMBOO"


class JenkinsContextLoader(BaseContextLoader):
    """
    A class that inherit from BaseContextLoader,used to represent JenkinsContext with its own environment variables.

    Attributes:
        CI_ENV_VARIABLE (str): 'JENKINS_URL'.
        CI_TYPE (CiType):
        ENV_VARIABLE_PREFIXES (List[str]): List of prefixes to find and load Jenkins environment variables.
    """

    CI_ENV_VARIABLE = "JENKINS_URL"
    CI_TYPE = CiType.JENKINS
    ENV_VARIABLE_PREFIXES = [
        "CVS_",
        "SVN_",
        "GIT_",
        "NODE_",
        "EXECUTOR_NUMBER",
        "JENKINS_",
        "JOB_",
        "BUILD_",
        "ROOT_BUILD_",
        "RUN_",
        "WORKSPACE",
    ]

    @classmethod
    def resolve(cls) -> Optional[Dict[str, str]]:
        """
        Returns a dictionary with Jenkins environment variables if 'cls.JENKINS_URL' exists
        in operating system environment. Otherwise returns None.

        Args:
            cls (JenkinsContextLoader):

        Returns:
            Union(Dict[str, str], optional): Jenkins environment variables in key-value format or None if 'JENKINS_URL'
            does not exists in os.environment.
        """
        if cls.CI_ENV_VARIABLE in os.environ:
            return cls.load_context_variables(cls.ENV_VARIABLE_PREFIXES)
        else:
            return None


class TeamCityCiContextResolver(BaseContextLoader):
    """
    A class that inherit from BaseContextLoader,used to represent TeamCityCIContext with its own environment variables.

    Attributes:
        CI_ENV_VARIABLE (str): 'TEAMCITY_VERSION'
        CI_TYPE (CiType):
        ENV_VARIABLE_PREFIXES (List[str]): List of prefixes to find and load Team City environment variables
    """

    CI_ENV_VARIABLE = "TEAMCITY_VERSION"
    CI_TYPE = CiType.TEAM_CITY
    ENV_VARIABLE_PREFIXES = [
        "BUILD_",
        "HOSTNAME",
        "SERVER_URL",
        "TEAMCITY_",
    ]

    @classmethod
    def resolve(cls) -> Optional[Dict[str, str]]:
        """
        Returns a dictionary with Jenkins environment variable if 'cls.TEAMCITY_VERSION' exists
        in operating system environment. Otherwise returns None.

        Args:
            cls (JenkinsContextLoader):

        Returns:
            Union(Dict[str, str], optional): Team City environment variables in key-value format or None if
            'cls.TEAMCITY_VERSION' does not exists in os.environment.
        """
        if cls.CI_ENV_VARIABLE in os.environ:
            return cls.load_context_variables(cls.ENV_VARIABLE_PREFIXES)
        else:
            return None


class CircleCiContextResolver(BaseContextLoader):
    """
    A class that inherit from BaseContextLoader,used to represent TeamCityCIContext with its own environment variables.

    Attributes:
        CI_ENV_VARIABLE (str): 'CIRCLECI'
        CI_TYPE (CiType):
        ENV_VARIABLE_PREFIXES (List[str]): List of prefixes to find and load Circle CI environment variables.
    """

    CI_ENV_VARIABLE = "CIRCLECI"
    CI_TYPE = CiType.CIRCLE_CI
    ENV_VARIABLE_PREFIXES = ["CIRCLE", "HOSTNAME"]

    @classmethod
    def resolve(cls) -> Optional[Dict[str, str]]:
        """
        Returns a dictionary with CIRCLECI environment variable if 'cls.CI_ENV_VARIABLE' exists
        in operating system environment. Otherwise returns None.

        Args:
            cls (JenkinsContextLoader):

        Returns:
            Union(Dict[str, str], optional): CIRCLECI environment variables in key-value format or None if
            'cls.CI_ENV_VARIABLE' does not exists in os.environment.
        """
        if cls.CI_ENV_VARIABLE in os.environ:
            return cls.load_context_variables(cls.ENV_VARIABLE_PREFIXES)
        else:
            return None


class TravisCiContextResolver(BaseContextLoader):
    """
    A class that inherit from BaseContextLoader,used to represent TravisCiContext with its own environment variables.

    Attributes:
        CI_ENV_VARIABLE (str): 'TRAVIS'
        CI_TYPE (CiType):
        ENV_VARIABLE_PREFIXES (List[str]): List of prefixes to find and load TRAVIS environment variables.
    """

    CI_ENV_VARIABLE = "TRAVIS"
    CI_TYPE = CiType.TRAVIS_CI
    ENV_VARIABLE_PREFIXES = ["TRAVIS", "USER"]

    @classmethod
    def resolve(cls) -> Optional[Dict[str, str]]:
        """
        Returns a dictionary with TRAVIS environment variable if 'cls.CI_ENV_VARIABLE' exists
        in operating system environment. Otherwise returns None.

        Args:
            cls (JenkinsContextLoader):

        Returns:
            Union(Dict[str, str], optional): TRAVIS environment variables in key-value format or None if
            'cls.CI_ENV_VARIABLE' does not exists in os.environment.
        """
        if cls.CI_ENV_VARIABLE in os.environ:
            return cls.load_context_variables(cls.ENV_VARIABLE_PREFIXES)
        else:
            return None


def resolve_ci_context() -> Optional[CiContextModel]:
    ci_tools: List[Type[BaseContextLoader]] = [
        JenkinsContextLoader,
        TeamCityCiContextResolver,
        CircleCiContextResolver,
        TravisCiContextResolver,
    ]

    ci_context: Optional[Type] = None
    for resolver in ci_tools:
        env_variables = resolver.resolve()  # type: ignore
        if env_variables:
            ci_context = resolver
            break

    if ci_context:
        return CiContextModel(ci_type=ci_context.CI_TYPE.value, env_variables=ci_context.resolve())
    else:
        return None
