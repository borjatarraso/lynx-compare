*** Settings ***
Documentation     Tests for module imports and structural integrity.
Library           ../tests/LynxCompareLibrary.py

*** Test Cases ***

GUI Module Is Importable
    [Documentation]    The GUI module should import without errors.
    ${ok}=    GUI Module Importable
    Should Be True    ${ok}

TUI Module Is Importable
    [Documentation]    The TUI module should import without errors.
    ${ok}=    TUI Module Importable
    Should Be True    ${ok}

API Module Is Importable
    [Documentation]    The Python API module should import without errors.
    ${ok}=    API Module Importable
    Should Be True    ${ok}

Export Module Is Importable
    [Documentation]    The export module should import without errors.
    ${ok}=    Export Module Importable
    Should Be True    ${ok}

Easter Egg Endpoint Has Art
    [Documentation]    The REST easter-egg endpoint should return ASCII art.
    ${ok}=    API Easter Egg Endpoint Has Art
    Should Be True    ${ok}

Easter Egg Trigger Matches
    [Documentation]    Easter egg should match known trigger words.
    ${r1}=    Check Easter Egg    lynx
    ${r2}=    Check Easter Egg    meow
    ${r3}=    Check Easter Egg    paw
    Should Be True    ${r1}
    Should Be True    ${r2}
    Should Be True    ${r3}

Easter Egg Rejects Random Text
    [Documentation]    Easter egg should not trigger on random input.
    ${r}=    Check Easter Egg    AAPL
    Should Not Be True    ${r}

Easter Egg Handles Whitespace
    [Documentation]    Easter egg should trim whitespace.
    ${r}=    Check Easter Egg Whitespace    ${SPACE}lynx${SPACE}
    Should Be True    ${r}
