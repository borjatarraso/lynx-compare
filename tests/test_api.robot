*** Settings ***
Documentation     Tests for the REST API server endpoints.
Library           Collections
Library           ../tests/LynxCompareLibrary.py

*** Test Cases ***

API App Creates Successfully
    [Documentation]    The Flask app should be created without error.
    ${result}=    Create API App
    Should Be True    ${result}

API Index Returns Endpoints
    [Documentation]    The root endpoint should list available endpoints.
    ${data}=    API Get Index
    Should Contain    ${data["name"]}    Lynx Compare
    Should Not Be Empty    ${data["endpoints"]}

API Health Returns OK
    [Documentation]    The health endpoint should return ok status.
    ${data}=    API Get Health
    Should Be Equal    ${data["status"]}    ok

API About Returns Developer Info
    [Documentation]    The about endpoint should return developer metadata.
    ${data}=    API Get About
    Should Be Equal    ${data["developer"]}    Borja Tarraso
    Should Be Equal    ${data["email"]}    borja.tarraso@member.fsf.org
    Should Contain    ${data["license"]}    BSD 3-Clause

API Compare Missing Params Returns Error
    [Documentation]    Compare endpoint without params should return 400.
    ${status}    ${data}=    API Get Compare Missing
    Should Be Equal As Integers    ${status}    400
    Should Contain    ${data["error"]}    required

API Export Missing Params Returns Error
    [Documentation]    Export endpoint without params should return 400.
    ${status}    ${data}=    API Get Export Missing
    Should Be Equal As Integers    ${status}    400
