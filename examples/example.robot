*** Settings ***
Library     SeleniumLibrary
Library     robotframework_zebrunner.ZebrunnerLib
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

Open Google
    [Tags]  robot:skip
    ${caps}  Evaluate  {"enableVideo": True, "enableLogs": True, "enableVNC": True, "provider": "zebrunner"}
    SeleniumLibrary.Open Browser    https://google.com  chrome  remote_url=https://tolik:90eaktVT97VqUOy5@engine.zebrunner.dev/wd/hub  desired_capabilities=${caps}
    SeleniumLibrary.Close Browser
