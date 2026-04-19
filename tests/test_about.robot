*** Settings ***
Documentation     Tests for the About module functionality.
Library           Collections
Library           OperatingSystem
Library           Process
Library           ../tests/LynxCompareLibrary.py

*** Test Cases ***

About Text Contains Developer Info
    [Documentation]    Verify about text includes developer name and email.
    ${text}=    Get About Text
    Should Contain    ${text}    Borja Tarraso
    Should Contain    ${text}    borja.tarraso@member.fsf.org

About Text Contains License Info
    [Documentation]    Verify about text includes BSD 3-Clause license.
    ${text}=    Get About Text
    Should Contain    ${text}    BSD 3-Clause License

About Text Contains Version
    [Documentation]    Verify about text includes the version string.
    ${text}=    Get About Text
    Should Contain    ${text}    v1.0

About Lines Returns List
    [Documentation]    Verify about_lines returns a non-empty list.
    ${lines}=    Get About Lines
    ${length}=    Get Length    ${lines}
    Should Be True    ${length} > 5

Developer Metadata Is Correct
    [Documentation]    Verify developer metadata constants.
    ${developer}=    Get Developer Name
    Should Be Equal    ${developer}    Borja Tarraso
    ${email}=    Get Developer Email
    Should Be Equal    ${email}    borja.tarraso@member.fsf.org
    ${license}=    Get License Name
    Should Be Equal    ${license}    BSD 3-Clause License

About CLI Flag Works
    [Documentation]    Verify --about flag displays info and exits.
    ${result}=    Run Process    python    -m    lynx_compare    --about
    Should Be Equal As Integers    ${result.rc}    0
    Should Contain    ${result.stdout}    Borja Tarraso
    Should Contain    ${result.stdout}    BSD 3-Clause License
