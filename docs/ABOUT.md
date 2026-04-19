# Lynx Compare — About

## About

All four interface modes include an About section displaying:

- **Application name**: Lynx Compare
- **Version**: v2.0
- **Developer**: Borja Tarraso <borja.tarraso@member.fsf.org>
- **License**: BSD 3-Clause License (full text included)

### Accessing About

| Mode        | How to access                                       |
| ----------- | --------------------------------------------------- |
| Console     | `lynx-compare --about`                              |
| Interactive | Type `about` at the prompt                          |
| TUI         | Press `F1` (available on input and result screens) |
| Graphical   | Click the **About** button in the toolbar           |

### Graphical About Dialog

The graphical About dialog features:

- **Centered on screen** with auto-computed size (min 540x640)
- **License text** has its own vertical scrollbar (rest of dialog is fixed)
- **Logo image** (`logo_sm_green.png`) displayed at the top
- **Close button** at the bottom (always visible)
- **Escape key** also closes the dialog
- **Mouse-wheel scrolling** on the license text area

### TUI About Dialog

- Fixed layout with only the license text in a scrollable container
- Press `Escape` or `Enter` to close

## Graphical Logo

- **Toolbar icon** (top-left): `logo_sm_quarter_green.png` (39x44px)
- **About dialog logo**: `logo_sm_green.png` (157x179px)
- The window icon is also set to `logo_sm_quarter_green.png`
