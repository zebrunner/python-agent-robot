*** Settings ***
Library     SeleniumLibrary
# Library     robotframework_zebrunner.ZebrunnerLib
# Library     pabot.PabotLib

*** Test Cases ***
Passed Test Case
    [Documentation]    Shows some assertion keywords
    Should Be True    5 + 5 == 10

Failed Test Case
    Should Be True  2 + 2 == 5

Skipped Test Case
    [Tags]  robot:skip
    Should Be True    5 + 5 == 10

Super long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long long name
    Should Be True    5 + 5 == 10

Open Google Chrome
    [Tags]
    ${caps}  Evaluate  {"enableVideo": True, "enableLogs": True, "enableVNC": True, "provider": "zebrunner"}
    SeleniumLibrary.Open Browser    https://google.com  chrome  remote_url=https://{URL}/wd/hub  desired_capabilities=${caps}
    SeleniumLibrary.Close Browser

Open Firefox
    [Tags]
    ${caps}  Evaluate  {"enableVideo": True, "enableLogs": True, "enableVNC": True, "provider": "zebrunner"}
    SeleniumLibrary.Open Browser    https://google.com  firefox  remote_url=https://{URL}/wd/hub  desired_capabilities=${caps}
    Should Be True  2 + 2 == 5
    SeleniumLibrary.Close Browser
