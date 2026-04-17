*** Settings ***
Documentation     Tests for the ComparisonView API wrapper.
Library           Collections
Library           ../tests/LynxCompareLibrary.py

*** Test Cases ***

View Has Winner Ticker
    [Documentation]    ComparisonView should expose the winning ticker.
    ${view}=    Get Comparison View
    ${ticker}=    View Winner Ticker    ${view}
    Should Not Be Equal    ${ticker}    TIE

View Has Winner Name
    [Documentation]    ComparisonView should expose the winning company name.
    ${view}=    Get Comparison View
    ${name}=    View Winner Name    ${view}
    Should Not Be Equal    ${name}    TIE

View Summary Is Non Empty
    [Documentation]    summary() should return a non-empty string.
    ${view}=    Get Comparison View
    ${s}=    View Summary    ${view}
    Should Not Be Empty    ${s}
    Should Contain    ${s}    vs

View Section Names Has Seven Entries
    [Documentation]    section_names should return 7 section names.
    ${view}=    Get Comparison View
    ${names}=    View Section Names    ${view}
    ${count}=    Get Length    ${names}
    Should Be Equal As Integers    ${count}    7

View Section Winner Returns Valid
    [Documentation]    section_winner should return a/b/tie for each section.
    ${view}=    Get Comparison View
    ${w}=    View Section Winner    ${view}    Valuation
    Should Match Regexp    ${w}    ^(a|b|tie)$

View Section Winner Ticker Returns Ticker
    [Documentation]    section_winner_ticker should return a ticker or TIE.
    ${view}=    Get Comparison View
    ${t}=    View Section Winner Ticker    ${view}    Valuation
    Should Match Regexp    ${t}    ^(AAPL|MSFT|TIE)$

View Metric Winner Returns Valid
    [Documentation]    metric_winner should return a/b/tie/na.
    ${view}=    Get Comparison View
    ${w}=    View Metric Winner    ${view}    pe_trailing
    Should Match Regexp    ${w}    ^(a|b|tie|na)$

View Metric Winner Ticker Returns Ticker
    [Documentation]    metric_winner_ticker returns the ticker of winner.
    ${view}=    Get Comparison View
    ${t}=    View Metric Winner Ticker    ${view}    pe_trailing
    Should Match Regexp    ${t}    ^(AAPL|MSFT|N/A)$

View Has Warnings
    [Documentation]    has_warnings should be True when warnings exist.
    ${view}=    Get Comparison View
    ${hw}=    View Has Warnings    ${view}
    Should Be True    ${hw}

View To Dict Returns Dict
    [Documentation]    to_dict() should return a serialisable dict.
    ${view}=    Get Comparison View
    ${d}=    View To Dict    ${view}
    Dictionary Should Contain Key    ${d}    ticker_a
    Dictionary Should Contain Key    ${d}    sections
    Dictionary Should Contain Key    ${d}    overall_winner

View Scoreboard Has All Sections
    [Documentation]    scoreboard() should have an entry for each section.
    ${view}=    Get Comparison View
    ${board}=    View Scoreboard    ${view}
    ${keys}=    Get Dictionary Keys    ${board}
    ${count}=    Get Length    ${keys}
    Should Be Equal As Integers    ${count}    7

View Metrics Won By Returns Count
    [Documentation]    metrics_won_by should return a count of won metrics.
    ${view}=    Get Comparison View
    ${count}=    View Metrics Won By    ${view}    AAPL
    Should Be True    ${count} > 0

View Sections Won By Returns Count
    [Documentation]    sections_won_by should return won sections count.
    ${view}=    Get Comparison View
    ${count}=    View Sections Won By    ${view}    AAPL
    Should Be True    ${count} > 0

View Repr Contains Tickers
    [Documentation]    repr() should show both tickers and winner.
    ${view}=    Get Comparison View
    ${r}=    View Repr    ${view}
    Should Contain    ${r}    AAPL
    Should Contain    ${r}    MSFT
