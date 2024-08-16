# python-agent-robot

The official Zebrunner Robotframework agent provides the reporting functionality. It can automatically track Selenium sessions
and send the info about session details to Zebrunner backend. It can be easily integrated into a project by just installing the library
and adding the configuration file.

Including reporting into your project is easy - just install the agent and provide minimal valid configuration for reporting.

Feel free to support the development with a [**donation**](https://www.paypal.com/donate/?hosted_button_id=MNHYYCYHAKUVA) for the next improvements.

<p align="center">
  <a href="https://zebrunner.com/"><img alt="Zebrunner" src="https://github.com/zebrunner/zebrunner/raw/master/docs/img/zebrunner_intro.png"></a>
</p>


## Installation

    pip install robotframework-zebrunner


## Configuration
After the installation, reporting is disabled by default. It won't send any data to the Zebrunner service without a valid configuration.

It is currently possible to provide the configuration via:
1. Environment variables
2. YAML file

`pyproject.toml`, `command arguments` are in plans for future releases.



<!-- groups:start -->

### Environment variables
The following configuration parameters are recognized by the agent:

- `REPORTING_ENABLED` - enables or disables reporting. The default value is `true`.
- `REPORTING_SERVER_HOSTNAME` - mandatory if reporting is enabled. It is Zebrunner server hostname. It can be obtained in Zebrunner on the 'Account & profile' page under the 'Service URL' section;
- `REPORTING_SERVER_ACCESS_TOKEN` - mandatory if reporting is enabled. Access token must be used to perform API calls. It can be obtained in Zebrunner on the 'Account & profile' page under the 'Token' section;
- `REPORTING_PROJECT_KEY` - optional value. It is the project that the test run belongs to. The default value is `DEF`. You can manage projects in Zebrunner in the appropriate section;
- `REPORTING_RUN_DISPLAY_NAME` - optional value. It is the display name of the test run. The default value is `Default Suite`;
- `REPORTING_RUN_BUILD` - optional value. It is the build number that is associated with the test run. It can depict either the test build number or the application build number;
- `REPORTING_RUN_ENVIRONMENT` - optional value. It is the environment where the tests will run;
- `REPORTING_SEND_LOGS` - Sends test logs to Zebrunner. Default: `true`;
- `REPORTING_NOTIFICATION_NOTIFY_ON_EACH_FAILURE` - optional value. Specifies whether Zebrunner should send notification to Slack/Teams on each test failure. The notifications will be sent even if the suite is still running. The default value is `false`;
- `REPORTING_NOTIFICATION_SLACK_CHANNELS` - optional value. The list of comma-separated Slack channels to send notifications to. Notification will be sent only if Slack integration is properly configured in Zebrunner with valid credentials for the project the tests are reported to. Zebrunner can send two type of notifications: on each test failure (if appropriate property is enabled) and on suite finish;
- `REPORTING_NOTIFICATION_MS_TEAMS_CHANNELS` - optional value. The list of comma-separated Microsoft Teams channels to send notifications to. Notification will be sent only if Teams integration is configured in Zebrunner project with valid webhooks for the channels. Zebrunner can send two type of notifications: on each test failure (if appropriate property is enabled) and on suite finish;
- `REPORTING_NOTIFICATION_EMAILS` - optional value. The list of comma-separated emails to send notifications to. This type of notification does not require further configuration on Zebrunner side. Unlike other notification mechanisms, Zebrunner can send emails only on suite finish;
 - `REPORTING_RUN_TREAT_SKIPS_AS_FAILURES` - optional value. If value is false all test-runs with skipped & passed tests
 would be marked as passed.

Agent also recognizes `.env` file in the resources root folder.

### Yaml file
Agent recognizes agent.yaml or agent.yml file in the resources root folder. It is currently not possible to configure an alternative file location.

Below is a sample configuration file:
```yaml
reporting:
  enabled: true
  project-key: DEF
  send-logs: true
  server:
    hostname: localhost:8080
    access-token: <token>
  notification:
    notify-on-each-failure: true
    slack-channels: automation, dev-team
    ms-teams-channels: automation, qa-team
    emails: example@example.com
  run:
    treat-skips-as-failures: false
    display-name: Nightly Regression Suite
    build: 1.12.1.96-SNAPSHOT
    environment: TEST-1
```

- `reporting.enabled` - enables or disables reporting. The default value is `true`;
- `reporting.server.hostname` - mandatory if reporting is enabled. Zebrunner server hostname. Can be obtained in Zebrunner on the 'Account & profile' page under the 'Service URL' section;
- `reporting.server.access-token` - mandatory if reporting is enabled. Access token must be used to perform API calls. Can be obtained in Zebrunner on the 'Account & profile' page under the 'Token' section;
- `reporting.project-key` - optional value. The project that the test run belongs to. The default value is `DEF`. You can manage projects in Zebrunner in the appropriate section;
- `reporting.send-logs` - Sends test logs to Zebrunner. Default: `true`
- `reporting.run.display-name` - optional value. The display name of the test run. The default value is Default Suite;
- `reporting.run.build` - optional value. The build number that is associated with the test run. It can depict either the test build number or the application build number;
- `reporting.run.environment` - optional value. The environment in which the tests will run.
- `reporting.notification.notify-on-each-failure` - optional value. Specifies whether Zebrunner should send notification to Slack/Teams on each test failure. The notifications will be sent even if the suite is still running. The default value is `false`;
- `reporting.notification.slack-channels` - optional value. The list of comma-separated Slack channels to send notifications to. Notification will be sent only if Slack integration is properly configured in Zebrunner with valid credentials for the project the tests are reported to. Zebrunner can send two type of notifications: on each test failure (if appropriate property is enabled) and on suite finish;
- `reporting.notification.ms-teams-channels` - optional value. The list of comma-separated Microsoft Teams channels to send notifications to. Notification will be sent only if Teams integration is configured in Zebrunner project with valid webhooks for the channels. Zebrunner can send two type of notifications: on each test failure (if appropriate property is enabled) and on suite finish;
- `reporting.notification.emails` - optional value. The list of comma-separated emails to send notifications to. This type of notification does not require further configuration on Zebrunner side. Unlike other notification mechanisms, Zebrunner can send emails only on suite finish;
 - `reporting.run.treat_skips_as_failures` - optional value. If value is false all test-runs with skipped & passed tests
 would be marked as passed.

If the required configurations are not provided, there is a warning displayed in logs with the problem description and the names of options
which need to be specified. Parameter names are case-insensitive and can be written in upper and lower registers.

<!-- groups:end -->

### Activate listener

There is two options for activation of Zebrunner listener.

Command line argument:
```
robot --listener robotframework_zebrunner.ZebrunnerListener
```
Import Zebrunner library into your project:
```
Library  robotframework_zebrunner.ZebrunnerLib
```


## Collecting captured screenshot
Sometimes it may be useful to have the ability to track captured screenshots in scope of Zebrunner Reporting. The agent comes
with the API allowing you to send your screenshots to Zebrunner, so that they could be attached to the test.

```
*** Settings ***
Library     robotframework_zebrunner.ZebrunnerLib

With screenshot
    ...
    Create File  ${OUTPUTDIR}/selenium-screenshot-1.png
    Capture Page Screenshot	${OUTPUTDIR}/selenium-screenshot-1.png
    Attach Test Screenshot  ${OUTPUTDIR}/selenium-screenshot-1.png
    ...
```

## Additional reporting capabilities

### Tracking test maintainer

You may want to add transparency to the process of automation maintenance by having an engineer responsible for
evolution of specific tests or test classes. Zebrunner comes with a concept of a maintainer - a person that can be
assigned to maintain tests. In order to keep track of those, the agent comes with the `maintainer` tag.

See a sample test bellow:

```
*** Settings ***
Library     robotframework_zebrunner.ZebrunnerLib

With maintainer
    [Tags]  maintainer=<maintainer_name>
    Should Be True    5 + 5 == 10
```

### Attaching labels
In some cases, it may be useful to attach some meta information related to a test. The agent comes with a concept of a label.
Label is a key-value pair associated with a test. The key and value are represented by a `str`. Labels can be attached to
tests and test runs.

There is a tag that can be used to attach labels to a test. There is also an API to attach labels during test or execution.
The agent has functions that can be used to attach labels.
```
*** Settings ***
Library     robotframework_zebrunner.ZebrunnerLib

With labels
    [Tags]  labels: some_label=123, other_label=234

    Attach Test Label   some_test_label  value
    Attach Test Run Label  some_test_run_label  value
    Should Be True    5 + 5 == 10
```
The test from the sample above attaches 3 test-level labels.

### Reverting test registration
In some cases it might be handy not to register test execution in Zebrunner. This may be caused by very special circumstances of test environment or execution conditions.


Zebrunner agent comes with a convenient method revert_registration() from CurrentTest class for reverting test registration at runtime. The following code snippet shows a case where test is not reported on Monday.
```
*** Settings ***
Library     robotframework_zebrunner.ZebrunnerLib

Revert test
     Current Test Revert Registration
     Should Be True    5 + 5 == 10
```

### Overriding run attributes
This section contains information on agent APIs allowing to manipulate test run attributes during runtime.

#### Setting build at runtime
All the configuration mechanisms listed above provide possibility to declaratively set test run build. But there might be cases when actual build becomes available only at runtime.

For such cases Zebrunner agent has a special method that can be used at any moment of the suite execution:
```
*** Settings ***
Library     robotframework_zebrunner.ZebrunnerLib
Suite Setup  Current Test Run Set Build  0.0.1
```

#### Setting locale
If you want to get full reporting experience and collect as much information in Zebrunner as its possible, you may want to report the test run locale.

For this, Zebrunner agent has a special method that can be used at any moment of the suite execution:
```
*** Settings ***
Library     robotframework_zebrunner.ZebrunnerLib
Suite Setup  Current Test Run Set Locale  EN
```

#### Overriding platform
A test run in Zebrunner may have platform associated with the run. If there is at least one initiated `Remote` driver session within the test run, then its platform will be displayed as a platform of the whole test run. Even if subsequent `Remote` drivers are initiated on another platform, the very first one will be displayed as the run platform.

In some cases you may want to override the platform of the first `Remote` driver session. Another problem is that it is not possible to specify `API` as a platform.

Zebrunner provides two special methods to solve both of these problems: `Current Test Run Set Platform` and `Current Test Run Set Platform Version`.
In the example below, the hook sets the API as a platform associated with the current test run.

```
*** Settings ***
Library     robotframework_zebrunner.ZebrunnerLib
Suite Setup  Current Test Run Set Platform  API
```

### Collecting additional artifacts
In case your tests or an entire test run produce some artifacts, it may be useful to track them in Zebrunner.
The agent comes with a few convenient methods for uploading artifacts in Zebrunner and linking them to the currently running test or test run.
Artifacts and artifact references can be attached using functions. Together with an artifact
or artifact reference, you must provide the display name. For the file, this name must contain the file extension that
reflects the actual content of the file. If the file extension does not match the file content, this file will not be
saved in Zebrunner. Artifact reference can have an arbitrary name.

#### Attaching artifact to test
```
*** Settings ***
Library     robotframework_zebrunner.ZebrunnerLib

With artifact
    Attach Test Artifact  requirements.txt
    ...
```

#### Attaching artifact reference to test

```
*** Settings ***
Library     robotframework_zebrunner.ZebrunnerLib

With artifact reference
    Attach Test Artifact Reference  google  https://google.com
    ...
```


#### Attaching artifact to test run

```
*** Settings ***
Library     robotframework_zebrunner.ZebrunnerLib

Attach Test Run Artifact  requirements.txt
```

#### Attaching artifact reference to test run

```
*** Settings ***
Library     robotframework_zebrunner.ZebrunnerLib

Attach Test Run Artifact Reference  google  https://google.com
```

Artifact uploading process is performed in the foreground now, so it will block the execution thread while sending.
The background uploading will be available in upcoming releases.

## Syncing test executions with external TCM systems

Zebrunner provides an ability to upload test results to external test case management systems (TCMs) on test run finish. For some TCMs it is possible to upload results in real-time during the test run execution.

This functionality is currently supported for TestRail, Xray, Zephyr Squad and Zephyr Scale.

### TestRail

For successful upload of test run results in TestRail, two steps must be performed:

1. Integration with TestRail is configured and enabled for Zebrunner project
2. Configuration is performed on the tests side


#### Configuration

Zebrunner agent has a special `Test Rail` keywords:

`Test Rail Set Suite Id  <id>`
:   Mandatory. The method sets TestRail suite id for current test run. This method must be invoked before all tests.

`Test Rail Set Case Id  <id>` or `test_rail_case_id=<id>` tag
:   Mandatory. Using these mechanisms you can set TestRail's case associated with specific automated test. It is highly recommended using the `test_rail_case_id` tag instead of keyword. Use the keyword only for special cases

`Test Rail Disable Sync`
:   Optional. Disables result upload. Same as `Test Rail Set Suite Id`, this keyword must be invoked before all tests

`Test Rail Include All Test Cases In New Run`
:   Optional. Includes all cases from suite into newly created run in TestRail. Same as `#set_suite_id(str)`, this method must be invoked before all tests

`Test Rail Enable Real Time Sync`
:   Optional. Enables real-time results upload. In this mode, result of test execution will be uploaded immediately after test finish. This method also automatically invokes `Test Rail Include All Test Cases In New Run`. Same as `Test Rail Set Suite Id`, this keyword must be invoked before all tests

`Test Rail Set Run Id  <id>`
:   Optional. Adds result into existing TestRail run. If not provided, test run is treated as new. Same as `Test Rail Set Suite Id`, this keyword must be invoked before all tests

`Test Rail Set Run Name  <name>`
:   Optional. Sets custom name for new TestRail run. By default, Zebrunner test run name is used. Same as `Test Rail Set Suite Id`, this keyword must be invoked before all tests

`Test Rail Set Milestone  <milestone>`
:   Optional. Adds result in TestRail milestone with the given name. Same as `Test Rail Set Suite Id`, this keyword must be invoked before all tests

`Test Rail Set Assignee <assignee>`
:   Optional. Sets TestRail run assignee. Same as `Test Rail Set Suite Id`, this keyword must be invoked before all tests

By default, a new run containing only cases assigned to the tests will be created in TestRail on test run finish.

#### Example

In the example below, a new run with name "Best run ever" will be created in TestRail on test run finish. Suite id is `321` and assignee is "Deve Loper". Results of the `awesome_test1` will be uploaded as result of cases with id `10000`, `10001`, `10002`. Results of the `awesome_test2` will be uploaded as result of case with id `20000`.
```
*** Settings ***
Library     robotframework_zebrunner.ZebrunnerLib
Suite Setup  Run Keywords  Test Rail Set Suite Id  1
...          AND           Test Rail Set Run Name  Best run ever
...          AND           Test Rail Set Assignee  Deve Loper

With Case Id
  [Tags]  test_rail_case_id=1
  ... 

With Another Case id
  Test Rail Set Case Id  2
```

### Xray

For successful upload of test run results in Xray two steps must be performed:

1. Xray integration is configured and enabled in Zebrunner project
2. Xray configuration is performed on the tests side

#### Configuration

Zebrunner agent has a special `Xray` keywords to control results upload:

`Xray Set Execution Key  <key>`
:   Mandatory. The method sets Xray execution key. This method must be invoked before all tests.

`Xray Set Test Key  <key>` or `xray_test_key=<key>`
:   Mandatory. Using these mechanisms you can set test keys associated with specific automated test. It is highly recommended using the `xray_test_key` tag instead of keyword. Use the keyword only for special cases

`Xray Disable Sync`
:   Optional. Disables result upload. Same as `Xray Set Execution Key`, this method must be invoked before all tests

`Xray Enable Real Time Sync`
:   Optional. Enables real-time results upload. In this mode, result of test execution will be uploaded immediately after test finish. Same as `Xray Set Execution Key`, this method must be invoked before all tests

By default, results will be uploaded to Xray on test run finish.

#### Example

In the example below, results will be uploaded to execution with key `ZBR-42`. Results of the `awesome_test1` will be uploaded as result of tests with key `ZBR-10000`, `ZBR-10001`, `ZBR-10002`. Results of the `awesome_test2` will be uploaded as result of test with key `ZBR-20000`.

```
*** Settings ***
Library     robotframework_zebrunner.ZebrunnerLib
Suite Setup  Xray Set Execution Key  ZBR-42


With test key
  [Tags]  xray_test_key=ZBR-10000  xray_test_key=ZBR-10001  xray_test_key=ZBR-10002
  ... 

With Another Test Key
  Xray Set Test Key  ZBR-20000

```


### Zephyr

For successful upload of test run results in Zephyr two steps must be performed:

1. Zephyr integration is configured and enabled in Zebrunner project
2. Zephyr configuration is performed on the tests side

Described steps work for both Zephyr Squad and Zephyr Scale.

#### Configuration

Zebrunner agent has a special `Zephyr` keywords to control results upload:

`Zephyr Set Test Cycle Key  <key>`
:   Mandatory. The method sets Zephyr test cycle key. This method must be invoked before all tests.

`Zephyr Set Jira Project Key  <key>`
:   Mandatory. Sets Zephyr Jira project key. Same as `Zephyr Set Test Cycle Key`, this method must be invoked before all tests

`Zephyr Set Test Case Key  <key>` or `zephyr_test_case_key=<key>`
:   Mandatory. Using these mechanisms you can set test case keys associated with specific automated test. It is highly recommended using the `zephyr_test_case_key=1` tag instead of keyword. Use the keyword only for special cases

`Zephyr Disable Sync`
:   Optional. Disables result upload. Same as `Zephyr Set Test Cycle Key`, this method must be invoked before all tests

`Zephyr Enable Real Time Sync`
:   Optional. Enables real-time results upload. In this mode, result of test execution will be uploaded immediately after test finish. Same as `Zephyr Set Test Cycle Key`, this method must be invoked before all tests

By default, results will be uploaded to Zephyr on test run finish.

#### Example

In the example below, results will be uploaded to test cycle with key `ZBR-R42` from project with key `ZBR`. Results of the `awesome_test1` will be uploaded as result of tests with key `ZBR-T10000`, `ZBR-T10001`, `ZBR-T10002`. Results of the `awesome_test2` will be uploaded as result of test with key `ZBR-T20000`.

```
*** Settings ***
Library     robotframework_zebrunner.ZebrunnerLib
Suite Setup  Run Keywords  Zephyr Set Test Cycle Key  ZBR-R42
...          AND           Zephyr Set Jira Project Key  ZBR


With test key
  [Tags]  zephyr_test_case_key=ZBR-T10000  zephyr_test_case_key=ZBR-T10001  zephyr_test_case_key=ZBR-T10002
  ... 

With Another Test Key
  Zephyr Set Test Case Key  ZBR-T20000


#conftest.py
from pytest_zebrunner.tcm import Zephyr

@pytest.hookimpl(trylast=True)
def pytest_sessionstart(session: Session) -> None:
    Zephyr.set_test_cycle_key("ZBR-R42");
    Zephyr.set_jira_project_key("ZBR");

```

## Selenium WebDriver support

The Zebrunner test agent is capable of tracking tests along with remote Selenium WebDriver sessions.

### Capturing session artifacts

Zebrunner supports 3 types of test session artifacts:

- Video recording
- Session log
- VNC streaming

Test agent itself does not capture those artifacts since it has no control over underlying Selenium Grid implementation, however, it is possible to attach appropriate artifact references by providing specially designed set of driver session capabilities (**enabling capabilities**) - see the table below for more details. Only the `True` value is considered as trigger to save the link.

| Artifact        | Display name | Enabling capability | Default reference                                  | Reference overriding capability |
|-----------------|--------------|---------------------|----------------------------------------------------|---------------------------------|
| Video recording | Video        | enableVideo         | `artifacts/test-sessions/<session-id>/video.mp4`   | videoLink                       |
| Session log     | Log          | enableLog           | `artifacts/test-sessions/<session-id>/session.log` | logLink                         |
| VNC streaming   |              | enableVNC           | `<provider-integration-host>/ws/vnc/<session-id>`  | vncLink                         |

The **display name** is the name of the artifact that will be displayed on Zebrunner UI. This value is predefined and unfortunately can not be changed at the moment.

The **default reference** is a reference to a location, where artifact is **expected to reside** in S3-compatible storage once created by test environment - it is important that it stays in sync with test environment configuration. It is possible to override references if needed by providing **reference overriding capabilities**. Note, that special `<session-id>` placeholder is supported and can be used as part of the value of those capabilities allowing runtime session id (generated by WebDriver) to be included into actual reference value.

#### VNC streaming

VNC is an artifact of a special type. They don't have a name and are not displayed among other artifacts. They are displayed in the video section on Zebrunner UI during session execution and are dropped off on session close.

Default reference to the VNC streaming is based on `provider` capability. Value of this capability will be converted to preconfigured integration from **Test Environment Provider** group. The resolved integration must have a filled in URL property and be enabled in order to save the link to VNC streaming. The `<provider-integration-host>` placeholder of the default link will be replaced by the host of the obtained integration URL. Also, the `http` protocol in the VNC streaming url will be automatically replaced by `ws`, and `https` protocol will be replaced by `wss`. Currently, we only support Selenium, Zebrunner and MCloud integrations.


## Contribution

To check out the project and build from the source, do the following:
```
git clone git://github.com/zebrunner/python-agent-pytest.git
cd python-agent-pytest
```

## License

Zebrunner reporting agent for PyTest is released under version 2.0 of the [Apache License](https://www.apache.org/licenses/LICENSE-2.0).

