*** Settings ***
Documentation     Advanced export tests: default paths, alignment, edge cases.
Library           Collections
Library           OperatingSystem
Library           String
Library           ../tests/LynxCompareLibrary.py

*** Test Cases ***

Default Export Dir Exists
    [Documentation]    The default export directory should be created.
    ${dir}=    Get Default Export Dir
    Directory Should Exist    ${dir}

Default Path Contains Tickers
    [Documentation]    Default filename should contain both tickers.
    ${path}=    Get Default Export Path Html
    Should Contain    ${path}    AAPL
    Should Contain    ${path}    MSFT

Default Path Has Correct Extension HTML
    [Documentation]    HTML default path should end with .html.
    ${path}=    Get Default Export Path Html
    Should End With    ${path}    .html

Default Path Has Correct Extension PDF
    [Documentation]    PDF default path should end with .pdf.
    ${path}=    Get Default Export Path Pdf
    Should End With    ${path}    .pdf

Default Path Has Correct Extension TXT
    [Documentation]    TXT default path should end with .txt.
    ${path}=    Get Default Export Path Txt
    Should End With    ${path}    .txt

Default Path Contains Timestamp
    [Documentation]    Default path should contain a date-like pattern.
    ${path}=    Get Default Export Path Html
    Should Match Regexp    ${path}    \\d{8}_\\d{6}

Export Creates Nested Directories
    [Documentation]    Export should auto-create parent directories.
    ${path}=    Export To Nested Dir
    File Should Exist    ${path}
    [Teardown]    Remove File    ${path}

Text Export Lines Fit 80 Chars
    [Documentation]    All content lines in text export should be <= 80 chars.
    ${widths}=    Export Text Line Widths
    FOR    ${w}    IN    @{widths}
        Should Be True    ${w} <= 80    Line width ${w} exceeds 80 characters
    END

Export Text Alignment Consistent
    [Documentation]    Full-width separator lines (only = or -) should be exactly 80 chars.
    ${text}=    Export Comparison Text
    @{lines}=    Split String    ${text}    \n
    FOR    ${line}    IN    @{lines}
        ${is_pure_sep}=    Evaluate    len($line) > 0 and (set($line) == {'='} or set($line) == {'-'})
        IF    ${is_pure_sep}
            ${length}=    Get Length    ${line}
            Should Be Equal As Integers    ${length}    80
        END
    END

Export Text Uses ASCII Only For Alignment
    [Documentation]    Text export should not use multi-byte Unicode in aligned columns.
    ${text}=    Export Comparison Text
    Should Not Contain    ${text}    \u2714
    Should Not Contain    ${text}    \u2718
    Should Not Contain    ${text}    \u2605
    Should Not Contain    ${text}    \u2654

API Export Bad Format Returns Error
    [Documentation]    Export with unsupported format should return 400.
    ${status}    ${data}=    API Get Export Bad Format
    Should Be Equal As Integers    ${status}    400
    Should Contain    ${data["error"]}    Unsupported format
