# python-agent-robot

The official Zebrunner Robotframework agent provides the reporting functionality. It can automatically track Selenium sessions
and send the info about session details to Zebrunner backend. It can be easily integrated into a project by just installing the library
and adding the configuration file.

Including reporting into your project is easy - just install the agent and provide minimal valid configuration for reporting.


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
    treat_skips_as_failures: false
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
which need to be specified. Parameter names are case insensitive and can be written in upper and lower registers.

<!-- groups:end -->

### Activate listener

There is two options for activation of Zebrunner listener.

Command line argument:
```bash
robot --listener robotframework_zebrunner.ZebrunnerListener ...
```

Import Zebrunner library into your project:
```
Library  robotframework_zebrunner.ZebrunnerLib
```
