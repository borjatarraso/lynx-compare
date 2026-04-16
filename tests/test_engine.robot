*** Settings ***
Documentation     Tests for the comparison engine core functionality.
Library           Collections
Library           ../tests/LynxCompareLibrary.py

*** Test Cases ***

Comparison Result Has Required Fields
    [Documentation]    A ComparisonResult should have all required fields.
    ${cr}=    Get Mock Comparison Result
    Should Not Be Empty    ${cr.ticker_a}
    Should Not Be Empty    ${cr.ticker_b}
    Should Not Be Empty    ${cr.name_a}
    Should Not Be Empty    ${cr.name_b}

Comparison Has Seven Sections
    [Documentation]    Comparison should produce exactly 7 sections.
    ${cr}=    Get Mock Comparison Result
    ${count}=    Get Length    ${cr.sections}
    Should Be Equal As Integers    ${count}    7

Section Names Are Correct
    [Documentation]    Verify all expected section names exist.
    ${names}=    Get Section Names
    Should Contain    ${names}    Valuation
    Should Contain    ${names}    Profitability
    Should Contain    ${names}    Solvency
    Should Contain    ${names}    Growth
    Should Contain    ${names}    Efficiency
    Should Contain    ${names}    Moat
    Should Contain    ${names}    Intrinsic Value

Overall Winner Is Valid
    [Documentation]    Overall winner should be 'a', 'b', or 'tie'.
    ${cr}=    Get Mock Comparison Result
    Should Match Regexp    ${cr.overall_winner}    ^(a|b|tie)$

Section Winners Are Valid
    [Documentation]    Each section winner should be 'a', 'b', or 'tie'.
    ${cr}=    Get Mock Comparison Result
    FOR    ${s}    IN    @{cr.sections}
        Should Match Regexp    ${s.winner}    ^(a|b|tie)$
    END

Metric Winners Are Valid
    [Documentation]    Each metric winner should be 'a', 'b', 'tie', or 'na'.
    ${cr}=    Get Mock Comparison Result
    FOR    ${s}    IN    @{cr.sections}
        FOR    ${m}    IN    @{s.metrics}
            Should Match Regexp    ${m.winner}    ^(a|b|tie|na)$
        END
    END

Total Wins Consistent With Sections
    [Documentation]    Total wins should equal sum of section wins.
    ${cr}=    Get Mock Comparison Result
    ${sum_a}=    Sum Section Wins A    ${cr}
    ${sum_b}=    Sum Section Wins B    ${cr}
    Should Be Equal As Integers    ${cr.total_wins_a}    ${sum_a}
    Should Be Equal As Integers    ${cr.total_wins_b}    ${sum_b}

Fmt Value Formats Percentage
    [Documentation]    fmt_value should format percentage metrics correctly.
    ${result}=    Format Value    roe    ${0.1534}
    Should Be Equal    ${result}    15.34%

Fmt Value Formats Money
    [Documentation]    fmt_value should format money metrics correctly.
    ${result}=    Format Value    market_cap    ${2500000000000}
    Should Contain    ${result}    $
    Should Contain    ${result}    T

Fmt Value Handles None
    [Documentation]    fmt_value should return N/A for None values.
    ${result}=    Format Value    roe    ${None}
    Should Be Equal    ${result}    N/A

Warnings Generated For Sector Mismatch
    [Documentation]    Warnings should be generated for sector mismatches.
    ${cr}=    Get Mock Comparison Result
    ${has_sector}=    Has Warning Level    ${cr}    sector
    # Our mock data has different sectors
    Should Be True    ${has_sector}
