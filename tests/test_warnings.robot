*** Settings ***
Documentation     Tests for comparability warnings (sector, industry, tier).
Library           Collections
Library           ../tests/LynxCompareLibrary.py

*** Test Cases ***

Warning Industry Present In Mock
    [Documentation]    Mock data should have industry mismatch warning.
    ${cr}=    Get Mock Comparison Result
    ${has}=    Has Warning Level    ${cr}    industry
    Should Be True    ${has}

Warning Sector Present In Mock
    [Documentation]    Mock data should have sector mismatch warning.
    ${cr}=    Get Mock Comparison Result
    ${has}=    Has Warning Level    ${cr}    sector
    Should Be True    ${has}

All Three Warnings Non Exclusive
    [Documentation]    Sector, industry, and tier warnings can all fire together.
    ${cr}=    Build Mock With All Warnings
    ${levels}=    Warning Levels    ${cr}
    Should Contain    ${levels}    sector
    Should Contain    ${levels}    industry
    Should Contain    ${levels}    tier
    ${count}=    Count Warnings    ${cr}
    Should Be Equal As Integers    ${count}    3

Tier Warning Standalone
    [Documentation]    Tier mismatch generates its own warning independently.
    ${cr}=    Build Mock With Tier Mismatch
    ${has_tier}=    Has Warning Level    ${cr}    tier
    Should Be True    ${has_tier}
    ${count}=    Count Warnings    ${cr}
    Should Be Equal As Integers    ${count}    1

Warning Levels Are Valid
    [Documentation]    Warning levels should be sector, industry, or tier.
    ${cr}=    Build Mock With All Warnings
    FOR    ${w}    IN    @{cr.warnings}
        Should Match Regexp    ${w.level}    ^(sector|industry|tier)$
    END

Warning Messages Are Non Empty
    [Documentation]    Each warning message should be non-empty.
    ${cr}=    Build Mock With All Warnings
    FOR    ${w}    IN    @{cr.warnings}
        Should Not Be Empty    ${w.message}
    END

Text Export Includes Warning Text
    [Documentation]    Plain-text export should contain warning labels.
    ${result}=    Export Text Contains Warnings
    Should Be True    ${result}

HTML Export Includes Warning Text
    [Documentation]    HTML export should contain warning sections.
    ${result}=    Export Html Contains Warnings
    Should Be True    ${result}
