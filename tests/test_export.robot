*** Settings ***
Documentation     Tests for the export module functionality.
Library           Collections
Library           OperatingSystem
Library           ../tests/LynxCompareLibrary.py

*** Test Cases ***

Export Text Contains Header
    [Documentation]    Plain-text export should contain the header with app name.
    ${text}=    Export Comparison Text
    Should Contain    ${text}    Lynx Compare
    Should Contain    ${text}    Comparison Report

Export Text Contains Company Names
    [Documentation]    Plain-text export should contain both company names.
    ${text}=    Export Comparison Text
    Should Contain    ${text}    AAPL
    Should Contain    ${text}    MSFT

Export Text Contains Sections
    [Documentation]    Plain-text export should contain section names.
    ${text}=    Export Comparison Text
    Should Contain    ${text}    VALUATION
    Should Contain    ${text}    PROFITABILITY
    Should Contain    ${text}    SOLVENCY
    Should Contain    ${text}    GROWTH
    Should Contain    ${text}    EFFICIENCY
    Should Contain    ${text}    MOAT
    Should Contain    ${text}    INTRINSIC VALUE

Export Text Contains Verdict
    [Documentation]    Plain-text export should contain the final verdict.
    ${text}=    Export Comparison Text
    Should Contain    ${text}    FINAL VERDICT

Export Text Contains Footer
    [Documentation]    Plain-text export footer should have developer info.
    ${text}=    Export Comparison Text
    Should Contain    ${text}    Borja Tarraso
    Should Contain    ${text}    BSD 3-Clause License

Export HTML Contains Doctype
    [Documentation]    HTML export should be a valid HTML5 document.
    ${html}=    Export Comparison HTML
    Should Contain    ${html}    <!DOCTYPE html>
    Should Contain    ${html}    </html>

Export HTML Has White Background
    [Documentation]    HTML export should use white background for readability.
    ${html}=    Export Comparison HTML
    Should Contain    ${html}    background: #ffffff

Export HTML Contains Company Info
    [Documentation]    HTML export should contain company tickers.
    ${html}=    Export Comparison HTML
    Should Contain    ${html}    AAPL
    Should Contain    ${html}    MSFT

Export HTML Contains Sections
    [Documentation]    HTML export should contain all section headings.
    ${html}=    Export Comparison HTML
    Should Contain    ${html}    VALUATION
    Should Contain    ${html}    PROFITABILITY

Export HTML Contains Styling
    [Documentation]    HTML export should contain embedded CSS.
    ${html}=    Export Comparison HTML
    Should Contain    ${html}    <style>
    Should Contain    ${html}    </style>

Export HTML Is Print Friendly
    [Documentation]    HTML export should contain print media query.
    ${html}=    Export Comparison HTML
    Should Contain    ${html}    @media print

Export To File HTML
    [Documentation]    Export dispatcher should write an HTML file.
    ${path}=    Export Comparison To File    html
    File Should Exist    ${path}
    ${content}=    Get File    ${path}
    Should Contain    ${content}    <!DOCTYPE html>
    [Teardown]    Remove File    ${path}

Export To File Text
    [Documentation]    Export dispatcher should write a text file.
    ${path}=    Export Comparison To File    text
    File Should Exist    ${path}
    ${content}=    Get File    ${path}
    Should Contain    ${content}    Lynx Compare
    [Teardown]    Remove File    ${path}
