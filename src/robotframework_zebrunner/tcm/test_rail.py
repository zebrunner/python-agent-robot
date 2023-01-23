from .base import BaseTcm


class TestRail(BaseTcm):
    SYNC_ENABLED = "com.zebrunner.app/tcm.testrail.sync.enabled"
    SYNC_REAL_TIME = "com.zebrunner.app/tcm.testrail.sync.real-time"
    INCLUDE_ALL = "com.zebrunner.app/tcm.testrail.include-all-cases"
    SUITE_ID = "com.zebrunner.app/tcm.testrail.suite-id"
    RUN_ID = "com.zebrunner.app/tcm.testrail.run-id"
    RUN_NAME = "com.zebrunner.app/tcm.testrail.run-name"
    MILESTONE = "com.zebrunner.app/tcm.testrail.milestone"
    ASSIGNEE = "com.zebrunner.app/tcm.testrail.assignee"
    CASE_ID = "com.zebrunner.app/tcm.testrail.case-id"

    @staticmethod
    def disable_sync() -> None:
        TestRail._verify_no_tests()
        TestRail._attach_label(TestRail.SYNC_ENABLED, "false")

    @staticmethod
    def enable_real_time_sync() -> None:
        TestRail._verify_no_tests()
        TestRail._attach_label(TestRail.SYNC_REAL_TIME, "true")
        TestRail._attach_label(TestRail.INCLUDE_ALL, "true")

    @staticmethod
    def include_all_test_cases_in_new_run() -> None:
        TestRail._verify_no_tests()
        TestRail._attach_label(TestRail.INCLUDE_ALL, "true")

    @staticmethod
    def set_suite_id(suite_id: str) -> None:
        TestRail._verify_no_tests()
        TestRail._attach_label(TestRail.SUITE_ID, suite_id)

    @staticmethod
    def set_run_id(run_id: str) -> None:
        TestRail._verify_no_tests()
        TestRail._attach_label(TestRail.RUN_ID, run_id)

    @staticmethod
    def set_run_name(run_name: str) -> None:
        TestRail._verify_no_tests()
        TestRail._attach_label(TestRail.RUN_NAME, run_name)

    @staticmethod
    def set_milestone(milestone: str) -> None:
        TestRail._verify_no_tests()
        TestRail._attach_label(TestRail.MILESTONE, milestone)

    @staticmethod
    def set_assignee(assignee: str) -> None:
        TestRail._verify_no_tests()
        TestRail._attach_label(TestRail.ASSIGNEE, assignee)

    @staticmethod
    def set_case_id(test_case_id: str) -> None:
        TestRail._attach_label(TestRail.CASE_ID, test_case_id)
