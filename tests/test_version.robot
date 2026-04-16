*** Settings ***
Documentation     Tests for version and metadata consistency.
Library           OperatingSystem
Library           Process
Library           ../tests/LynxCompareLibrary.py

*** Test Cases ***

Version Is 1.0.0
    [Documentation]    Version should be 1.0.0 after major release.
    ${version}=    Get Version
    Should Be Equal    ${version}    1.0.0

App Name Is Lynx Compare
    [Documentation]    App name constant should be correct.
    ${name}=    Get About App Name
    Should Be Equal    ${name}    Lynx Compare

Version Flag Works
    [Documentation]    --version should print version and exit cleanly.
    ${result}=    Run Process    python    -m    lynx_compare    --version
    Should Be Equal As Integers    ${result.rc}    0
    Should Contain    ${result.stdout}    1.0.0

About Flag Shows Version
    [Documentation]    --about should show the current version.
    ${result}=    Run Process    python    -m    lynx_compare    --about
    Should Be Equal As Integers    ${result.rc}    0
    Should Contain    ${result.stdout}    1.0.0
