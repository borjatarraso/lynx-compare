"""Tkinter graphical user interface for Lynx Compare."""

from __future__ import annotations

import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from lynx_compare.engine import ComparisonResult, SectionResult, Warning

# ---------------------------------------------------------------------------
# Colour palette  (Catppuccin Mocha)
# ---------------------------------------------------------------------------
BG = "#1e1e2e"
BG_SURFACE = "#242438"
BG_CARD = "#2a2a3d"
BG_INPUT = "#313147"
BG_HOVER = "#3a3a52"
FG = "#cdd6f4"
FG_DIM = "#6c7086"
FG_WIN = "#a6e3a1"
FG_LOSE = "#585b70"
FG_TIE = "#f9e2af"
ACCENT = "#89b4fa"
ACCENT2 = "#cba6f7"   # mauve
BORDER = "#45475a"
BTN_BG = "#89b4fa"
BTN_FG = "#1e1e2e"
BTN_ACTIVE = "#74c7ec"
BTN_DANGER = "#f38ba8"
BTN_SUBTLE = "#45475a"
BTN_SUBTLE_FG = "#bac2de"
WARN_RED = "#f38ba8"
WARN_ORANGE = "#fab387"
WARN_YELLOW = "#f9e2af"
TROPHY_COL = "#f9e2af"
CROWN_COL = "#a6e3a1"
SPLASH_BG = "#181825"

# Unicode
CHECK = "\u2714"
CROSS = "\u2718"
TROPHY = "\u2605"
CROWN = "\u2654"
WARN_ICON = "\u26a0"
ARROW_L = "\u25c0\u2500\u2500"
ARROW_R = "\u2500\u2500\u25b6"
ARROW_TIE_S = "\u25c0\u2550\u25b6"
ARROW_NA_S = "\u2500\u2500\u2500"
DIAMOND = "\u25c6"
EXPAND = "\u25bc"    # ▼
COLLAPSE = "\u25b2"  # ▲
LYNX = "\U0001f43e"  # 🐾

import platform as _plat
if _plat.system() == "Windows":
    _FAMILY = "Segoe UI"
elif _plat.system() == "Darwin":
    _FAMILY = "Helvetica"
else:
    _FAMILY = "Noto Sans"

FONT = (_FAMILY, 11)
FONT_BOLD = (_FAMILY, 11, "bold")
FONT_SMALL = (_FAMILY, 10)
FONT_TINY = (_FAMILY, 9)
FONT_TITLE = (_FAMILY, 18, "bold")
FONT_SPLASH = (_FAMILY, 28, "bold")
FONT_SPLASH_SUB = (_FAMILY, 12)
FONT_SECTION = (_FAMILY, 12, "bold")
FONT_VERDICT = (_FAMILY, 14, "bold")
FONT_WARN = (_FAMILY, 10, "bold")
FONT_ABOUT_TITLE = (_FAMILY, 16, "bold")
FONT_ABOUT = (_FAMILY, 10)
FONT_ABOUT_HEADING = (_FAMILY, 11, "bold")
FONT_MONO = ("Courier New" if _plat.system() == "Windows" else "monospace", 9)

W_VAL = 24
W_ARROW = 6
W_METRIC = 26

# ---------------------------------------------------------------------------
# Image paths
# ---------------------------------------------------------------------------
_IMG_DIR = Path(__file__).resolve().parent.parent / "img"
_ICON_PATH = _IMG_DIR / "logo_sm_quarter_green.png"
_ABOUT_LOGO_PATH = _IMG_DIR / "logo_sm_green.png"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_mcap(val: float | None) -> str:
    if val is None:
        return "N/A"
    av = abs(val)
    if av >= 1e12:
        return f"${av / 1e12:,.2f}T"
    if av >= 1e9:
        return f"${av / 1e9:,.2f}B"
    if av >= 1e6:
        return f"${av / 1e6:,.2f}M"
    return f"${av:,.0f}"


def _winner_fg(winner: str, side: str) -> str:
    if winner == "na":
        return FG_DIM
    if winner == "tie":
        return FG_TIE
    if winner == side:
        return FG_WIN
    return FG_LOSE


def _arrow_text(winner: str, side: str) -> tuple[str, str]:
    if winner == side:
        return (ARROW_L if side == "a" else ARROW_R, FG_WIN)
    if winner == "tie":
        return (ARROW_TIE_S, FG_TIE)
    if winner == "na":
        return (ARROW_NA_S, FG_DIM)
    return ("", BG_CARD)


def _make_row(parent: tk.Frame, bg: str,
              val_a: str, fg_a: str,
              arrow_l: str, fg_al: str,
              metric: str, fg_m: str,
              arrow_r: str, fg_ar: str,
              val_b: str, fg_b: str,
              font=None) -> None:
    font = font or FONT
    r = tk.Frame(parent, bg=bg)
    r.pack(fill=tk.X)
    tk.Label(r, text=val_a, font=font, bg=bg, fg=fg_a,
             width=W_VAL, anchor=tk.E).pack(side=tk.LEFT, padx=(4, 0))
    tk.Label(r, text=arrow_l, font=font, bg=bg, fg=fg_al,
             width=W_ARROW, anchor=tk.CENTER).pack(side=tk.LEFT)
    tk.Label(r, text=metric, font=font, bg=bg, fg=fg_m,
             width=W_METRIC, anchor=tk.CENTER).pack(side=tk.LEFT)
    tk.Label(r, text=arrow_r, font=font, bg=bg, fg=fg_ar,
             width=W_ARROW, anchor=tk.CENTER).pack(side=tk.LEFT)
    tk.Label(r, text=val_b, font=font, bg=bg, fg=fg_b,
             width=W_VAL, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 4))


def _styled_btn(parent, text, command, bg=BTN_BG, fg=BTN_FG,
                font=None, padx=14, pady=3, cursor="hand2", **kw):
    """Create a styled flat button with hover effect."""
    font = font or FONT_BOLD
    btn = tk.Button(
        parent, text=text, font=font, bg=bg, fg=fg,
        activebackground=BTN_ACTIVE, activeforeground=fg,
        relief=tk.FLAT, padx=padx, pady=pady, cursor=cursor,
        command=command, **kw,
    )
    # Hover highlight
    _orig_bg = bg
    def _enter(_):
        if btn.cget("state") != "disabled":
            btn.configure(bg=BTN_ACTIVE if bg == BTN_BG else BG_HOVER)
    def _leave(_):
        if btn.cget("state") != "disabled":
            btn.configure(bg=_orig_bg)
    btn.bind("<Enter>", _enter)
    btn.bind("<Leave>", _leave)
    return btn


# ---------------------------------------------------------------------------
# About dialog (centred, license has its own vertical scroll)
# ---------------------------------------------------------------------------

class AboutDialog(tk.Toplevel):
    """Modal About dialog displayed in the centre of the screen.

    The dialog is sized to fit the logo, app info and developer section
    without scrolling.  Only the full BSD-3 license text has its own
    vertical scrollbar.
    """

    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent)
        self.title("About Lynx Compare")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        from lynx_compare import __version__, __year__
        from lynx_compare.about import (
            APP_NAME, APP_DESCRIPTION, DEVELOPER, DEVELOPER_EMAIL,
            LICENSE_NAME, LICENSE_TEXT,
        )

        # -- Logo ------------------------------------------------------------
        self._logo_image = None
        if _ABOUT_LOGO_PATH.exists():
            try:
                self._logo_image = tk.PhotoImage(file=str(_ABOUT_LOGO_PATH))
                tk.Label(
                    self, image=self._logo_image, bg=BG,
                ).pack(pady=(20, 8))
            except tk.TclError:
                pass

        # -- Title -----------------------------------------------------------
        tk.Label(
            self, text=APP_NAME, font=FONT_ABOUT_TITLE, bg=BG, fg=ACCENT,
        ).pack()
        tk.Label(
            self, text=f"v{__version__}", font=FONT_SMALL, bg=BG, fg=FG_DIM,
        ).pack()
        tk.Label(
            self, text=APP_DESCRIPTION, font=FONT_ABOUT, bg=BG, fg=FG,
        ).pack(pady=(4, 14))

        # -- Developer -------------------------------------------------------
        tk.Label(
            self, text="Developer", font=FONT_ABOUT_HEADING, bg=BG, fg=ACCENT,
        ).pack(anchor=tk.W, padx=28)
        tk.Label(
            self, text=f"  {DEVELOPER}", font=FONT_ABOUT, bg=BG, fg=FG,
        ).pack(anchor=tk.W, padx=28)
        tk.Label(
            self, text=f"  {DEVELOPER_EMAIL}", font=FONT_ABOUT, bg=BG, fg=FG_DIM,
        ).pack(anchor=tk.W, padx=28, pady=(0, 14))

        # -- License heading -------------------------------------------------
        tk.Label(
            self, text="License", font=FONT_ABOUT_HEADING, bg=BG, fg=ACCENT,
        ).pack(anchor=tk.W, padx=28)
        tk.Label(
            self, text=f"  {LICENSE_NAME}", font=FONT_ABOUT, bg=BG, fg=FG,
        ).pack(anchor=tk.W, padx=28, pady=(0, 6))

        # -- Close button (pack BEFORE the expanding license area so it
        #    is always visible at the bottom) ---------------------------------
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(side=tk.BOTTOM, pady=(0, 18))
        _styled_btn(
            btn_frame, "Close", self.destroy,
            bg=BTN_BG, fg=BTN_FG, padx=30, pady=6,
        ).pack()

        # -- License text (scrollable, fills remaining space) ----------------
        license_outer = tk.Frame(
            self, bg=BORDER, padx=1, pady=1,
        )
        license_outer.pack(fill=tk.BOTH, expand=True, padx=28, pady=(0, 14))

        license_scroll = ttk.Scrollbar(license_outer, orient=tk.VERTICAL)
        license_text = tk.Text(
            license_outer, font=FONT_MONO, bg=BG_CARD, fg=FG_DIM,
            wrap=tk.WORD, relief=tk.FLAT, borderwidth=0,
            highlightthickness=0, padx=10, pady=8,
            yscrollcommand=license_scroll.set,
        )
        license_scroll.configure(command=license_text.yview)
        license_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        license_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        license_text.insert("1.0", LICENSE_TEXT.strip())
        license_text.configure(state=tk.DISABLED)

        # Mouse-wheel scrolling inside the license text
        def _on_mousewheel(event):
            license_text.yview_scroll(-1 * (event.delta // 120), "units")
        def _on_button4(_):
            license_text.yview_scroll(-3, "units")
        def _on_button5(_):
            license_text.yview_scroll(3, "units")
        license_text.bind("<MouseWheel>", _on_mousewheel)
        license_text.bind("<Button-4>", _on_button4)
        license_text.bind("<Button-5>", _on_button5)

        # -- Size and centre -------------------------------------------------
        # Let Tk compute the natural size, then centre on screen.
        self.update_idletasks()
        w = max(self.winfo_reqwidth(), 540)
        h = max(self.winfo_reqheight(), 640)
        # Cap height so the license area gets a comfortable scroll region
        h = min(h, 720)
        sx = parent.winfo_screenwidth()
        sy = parent.winfo_screenheight()
        x = (sx - w) // 2
        y = (sy - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        # ESC also closes
        self.bind("<Escape>", lambda _: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)


# ---------------------------------------------------------------------------
# Easter egg dialog
# ---------------------------------------------------------------------------

class EasterEggDialog(tk.Toplevel):
    """Hidden easter-egg dialog with ASCII art."""

    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent)
        self.title("You found it!")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        w, h = 440, 460
        sx = parent.winfo_screenwidth()
        sy = parent.winfo_screenheight()
        x = (sx - w) // 2
        y = (sy - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        from lynx_compare.about import easter_egg_text

        tk.Label(
            self, text="Easter Egg!", font=FONT_ABOUT_TITLE, bg=BG, fg=TROPHY_COL,
        ).pack(pady=(16, 4))

        art_text = tk.Text(
            self, font=FONT_MONO, bg=BG_CARD, fg=FG_WIN,
            wrap=tk.NONE, height=20, width=44, relief=tk.FLAT,
            borderwidth=0, highlightthickness=0, padx=8, pady=8,
        )
        art_text.insert("1.0", easter_egg_text().strip())
        art_text.configure(state=tk.DISABLED)
        art_text.pack(padx=16, fill=tk.BOTH, expand=True)

        _styled_btn(
            self, "Nice!", self.destroy,
            bg=BTN_BG, fg=BTN_FG, padx=30, pady=6,
        ).pack(pady=(8, 16))

        self.bind("<Escape>", lambda _: self.destroy())


# ---------------------------------------------------------------------------
# Export dialog (styled, with format picker and smart default path)
# ---------------------------------------------------------------------------

class ExportDialog(tk.Toplevel):
    """Modal export dialog with format selection and default save path."""

    def __init__(self, parent: tk.Tk, cr) -> None:
        super().__init__(parent)
        self.cr = cr
        self.result_path: str | None = None
        self.title("Export Comparison Report")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Centre on screen
        w, h = 540, 380
        sx = parent.winfo_screenwidth()
        sy = parent.winfo_screenheight()
        x = (sx - w) // 2
        y = (sy - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        from lynx_compare.export import default_export_path

        # -- Title -----------------------------------------------------------
        tk.Label(
            self, text="Export Comparison Report",
            font=FONT_ABOUT_TITLE, bg=BG, fg=ACCENT,
        ).pack(pady=(20, 4))
        tk.Label(
            self, text=f"{cr.name_a} ({cr.ticker_a})  vs  {cr.name_b} ({cr.ticker_b})",
            font=FONT_SMALL, bg=BG, fg=FG_DIM,
        ).pack(pady=(0, 16))

        # -- Format selection ------------------------------------------------
        fmt_frame = tk.Frame(self, bg=BG_CARD, padx=20, pady=12)
        fmt_frame.pack(fill=tk.X, padx=24)

        tk.Label(
            fmt_frame, text="Format", font=FONT_ABOUT_HEADING,
            bg=BG_CARD, fg=ACCENT,
        ).pack(anchor=tk.W, pady=(0, 6))

        self._fmt_var = tk.StringVar(value="html")

        formats = [
            ("html", "HTML", "Styled document, best for viewing in browser"),
            ("pdf", "PDF", "Printable document, requires weasyprint"),
            ("text", "Plain Text", "Simple text file, universal compatibility"),
        ]
        for value, label, desc in formats:
            row = tk.Frame(fmt_frame, bg=BG_CARD)
            row.pack(fill=tk.X, pady=1)
            rb = tk.Radiobutton(
                row, text=label, variable=self._fmt_var, value=value,
                font=FONT_BOLD, bg=BG_CARD, fg=FG,
                selectcolor=BG_INPUT, activebackground=BG_CARD,
                activeforeground=FG, highlightthickness=0,
                command=self._on_format_change,
            )
            rb.pack(side=tk.LEFT)
            tk.Label(
                row, text=f"  {desc}", font=FONT_TINY, bg=BG_CARD, fg=FG_DIM,
            ).pack(side=tk.LEFT)

        # -- Save path -------------------------------------------------------
        path_frame = tk.Frame(self, bg=BG, padx=24)
        path_frame.pack(fill=tk.X, pady=(14, 0))

        tk.Label(
            path_frame, text="Save to:", font=FONT_ABOUT_HEADING,
            bg=BG, fg=ACCENT,
        ).pack(anchor=tk.W, pady=(0, 4))

        entry_row = tk.Frame(path_frame, bg=BG)
        entry_row.pack(fill=tk.X)

        self._path_var = tk.StringVar(value=default_export_path(cr, ".html"))
        self._path_entry = tk.Entry(
            entry_row, textvariable=self._path_var, font=FONT_SMALL,
            bg=BG_INPUT, fg=FG, insertbackground=FG,
            relief=tk.FLAT, highlightthickness=2,
            highlightcolor=ACCENT, highlightbackground=BORDER,
        )
        self._path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)

        _styled_btn(
            entry_row, "Browse...", self._on_browse,
            bg=BTN_SUBTLE, fg=BTN_SUBTLE_FG, font=FONT_SMALL,
            padx=10, pady=4,
        ).pack(side=tk.LEFT, padx=(6, 0))

        # -- Buttons ---------------------------------------------------------
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(pady=(20, 16))

        _styled_btn(
            btn_frame, f"{DIAMOND}  Export", self._on_export,
            bg=BTN_BG, fg=BTN_FG, padx=28, pady=6,
        ).pack(side=tk.LEFT, padx=(0, 10))

        _styled_btn(
            btn_frame, "Cancel", self.destroy,
            bg=BTN_SUBTLE, fg=BTN_SUBTLE_FG, padx=20, pady=6,
        ).pack(side=tk.LEFT)

        # Key bindings
        self.bind("<Escape>", lambda _: self.destroy())
        self.bind("<Return>", lambda _: self._on_export())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _on_format_change(self) -> None:
        from lynx_compare.export import default_export_path
        ext_map = {"html": ".html", "pdf": ".pdf", "text": ".txt"}
        ext = ext_map.get(self._fmt_var.get(), ".html")
        self._path_var.set(default_export_path(self.cr, ext))

    def _on_browse(self) -> None:
        ext_map = {"html": ".html", "pdf": ".pdf", "text": ".txt"}
        ext = ext_map.get(self._fmt_var.get(), ".html")
        type_map = {
            ".html": ("HTML files", "*.html"),
            ".pdf": ("PDF files", "*.pdf"),
            ".txt": ("Text files", "*.txt"),
        }
        ftype = type_map.get(ext, ("All files", "*.*"))

        from lynx_compare.export import _default_export_dir
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Save Export As",
            initialdir=str(_default_export_dir()),
            initialfile=Path(self._path_var.get()).name,
            filetypes=[ftype, ("All files", "*.*")],
            defaultextension=ext,
        )
        if path:
            self._path_var.set(path)

    def _on_export(self) -> None:
        path = self._path_var.get().strip()
        if not path:
            return

        fmt = self._fmt_var.get()
        try:
            from lynx_compare.export import export_comparison
            self.result_path = export_comparison(self.cr, path, fmt)
            self.destroy()
            messagebox.showinfo(
                "Export Complete",
                f"Report saved to:\n\n{self.result_path}",
            )
        except RuntimeError as exc:
            messagebox.showwarning("Export", str(exc), parent=self)
        except Exception as exc:
            messagebox.showerror("Export Error", str(exc), parent=self)


# ---------------------------------------------------------------------------
# Splash screen
# ---------------------------------------------------------------------------

class SplashScreen:
    """Animated splash shown briefly on startup."""

    def __init__(self, root: tk.Tk, on_done: callable) -> None:
        self.root = root
        self.on_done = on_done

        self.overlay = tk.Frame(root, bg=SPLASH_BG)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Center content
        center = tk.Frame(self.overlay, bg=SPLASH_BG)
        center.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        self.title_label = tk.Label(
            center, text=f"{LYNX}  LYNX COMPARE",
            font=FONT_SPLASH, bg=SPLASH_BG, fg=ACCENT,
        )
        self.title_label.pack()

        tk.Label(
            center, text="Fundamental Analysis Comparison",
            font=FONT_SPLASH_SUB, bg=SPLASH_BG, fg=FG_DIM,
        ).pack(pady=(8, 0))

        tk.Label(
            center, text="v1.0.0",
            font=FONT_TINY, bg=SPLASH_BG, fg=FG_DIM,
        ).pack(pady=(16, 0))

        # Loading bar
        self.bar_frame = tk.Frame(self.overlay, bg=BORDER, height=3)
        self.bar_frame.place(relx=0.3, rely=0.6, relwidth=0.4, height=3)
        self.bar_fill = tk.Frame(self.bar_frame, bg=ACCENT, height=3)
        self.bar_fill.place(relx=0, rely=0, relwidth=0, relheight=1)

        self._progress = 0.0
        self._animate()

    def _animate(self) -> None:
        self._progress += 0.05
        if self._progress >= 1.0:
            self.overlay.destroy()
            self.on_done()
            return
        self.bar_fill.place(relwidth=self._progress)
        self.root.after(40, self._animate)


# ---------------------------------------------------------------------------
# Collapsible section
# ---------------------------------------------------------------------------

class CollapsibleCard:
    """A card with a header that can be toggled open/closed."""

    def __init__(self, parent: tk.Frame, title: str, start_open: bool = True) -> None:
        self.is_open = start_open

        self.outer = tk.Frame(parent, bg=BG)
        self.outer.pack(fill=tk.X, padx=12, pady=(8, 0))

        # Header bar — clickable
        self.header = tk.Frame(self.outer, bg=BG_SURFACE, cursor="hand2")
        self.header.pack(fill=tk.X)

        self.toggle_label = tk.Label(
            self.header, text=COLLAPSE if start_open else EXPAND,
            font=FONT_SMALL, bg=BG_SURFACE, fg=FG_DIM, width=3,
        )
        self.toggle_label.pack(side=tk.LEFT, padx=(8, 0))

        self.title_label = tk.Label(
            self.header, text=title, font=FONT_SECTION,
            bg=BG_SURFACE, fg=ACCENT, anchor=tk.W,
        )
        self.title_label.pack(side=tk.LEFT, padx=(4, 8), fill=tk.X, expand=True)

        # Bind click on entire header
        for widget in (self.header, self.toggle_label, self.title_label):
            widget.bind("<Button-1>", lambda _: self.toggle())

        # Content frame
        self.content = tk.Frame(
            self.outer, bg=BG_CARD,
            highlightbackground=BORDER, highlightthickness=1,
        )
        if start_open:
            self.content.pack(fill=tk.X)

    def toggle(self) -> None:
        self.is_open = not self.is_open
        if self.is_open:
            self.content.pack(fill=tk.X)
            self.toggle_label.configure(text=COLLAPSE)
        else:
            self.content.pack_forget()
            self.toggle_label.configure(text=EXPAND)

    def set_title(self, title: str) -> None:
        self.title_label.configure(text=title)


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

class LynxCompareGUI:
    """Tkinter GUI application for Lynx Compare."""

    def __init__(self, cli_args) -> None:
        self.cli_args = cli_args
        self.root = tk.Tk()
        self.root.title(f"{DIAMOND} Lynx Compare {DIAMOND}")
        self.root.configure(bg=BG)
        self.root.geometry("1120x820")
        self.root.minsize(920, 620)

        # Set window icon
        self._icon_image = None
        if _ICON_PATH.exists():
            try:
                self._icon_image = tk.PhotoImage(file=str(_ICON_PATH))
                self.root.iconphoto(True, self._icon_image)
            except tk.TclError:
                pass

        self._warning_entries: list[tuple[tk.Label, str]] = []
        self._blink_visible = True
        self._blink_id: str | None = None
        self._section_cards: list[CollapsibleCard] = []
        self._last_result: ComparisonResult | None = None
        self._egg_buffer = ""

        # Build hidden main UI, then show splash
        self.main_frame = tk.Frame(self.root, bg=BG)
        self._build_toolbar()
        self._build_input_panel()
        self._build_result_area()
        self._build_statusbar()

        # Easter-egg key listener
        self.root.bind("<Key>", self._on_keypress)

        # Show splash, which reveals main_frame when done
        SplashScreen(self.root, self._on_splash_done)

    def _on_splash_done(self) -> None:
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.entry_a.focus_set()

    # ---- Easter egg key listener -----------------------------------------

    def _on_keypress(self, event: tk.Event) -> None:
        if event.char and event.char.isalpha():
            self._egg_buffer += event.char.lower()
            # Keep only last 10 chars
            self._egg_buffer = self._egg_buffer[-10:]
            from lynx_compare.about import check_easter_egg
            for trigger in ("lynx", "meow", "paw"):
                if self._egg_buffer.endswith(trigger):
                    self._egg_buffer = ""
                    EasterEggDialog(self.root)
                    return

    # ---- Toolbar ---------------------------------------------------------

    @staticmethod
    def _toolbar_sep(parent) -> None:
        """Add a thin vertical separator to the toolbar."""
        sep = tk.Frame(parent, bg=BORDER, width=1)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=6)

    def _build_toolbar(self) -> None:
        # Outer bar with accent bottom border
        bar_outer = tk.Frame(self.main_frame, bg=ACCENT, height=44)
        bar_outer.pack(fill=tk.X)
        bar_outer.pack_propagate(False)

        bar = tk.Frame(bar_outer, bg=BG_SURFACE)
        bar.pack(fill=tk.BOTH, expand=True, pady=(0, 2))  # 2px accent underline

        # ── Brand (logo + title) ──
        self._toolbar_icon = None
        if _ICON_PATH.exists():
            try:
                self._toolbar_icon = tk.PhotoImage(file=str(_ICON_PATH))
                tk.Label(
                    bar, image=self._toolbar_icon, bg=BG_SURFACE,
                ).pack(side=tk.LEFT, padx=(12, 4))
            except tk.TclError:
                pass

        tk.Label(bar, text="Lynx Compare", font=FONT_SECTION,
                 bg=BG_SURFACE, fg=ACCENT).pack(side=tk.LEFT, padx=(0, 6))

        self._toolbar_sep(bar)

        # ── Actions group ──
        self.btn_new = _styled_btn(
            bar, f"{DIAMOND} New", self._on_reset,
            bg=BTN_SUBTLE, fg=BTN_SUBTLE_FG, font=FONT_SMALL,
            padx=10, pady=3,
        )
        self.btn_new.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_export = _styled_btn(
            bar, "Export", self._on_export,
            bg=BTN_SUBTLE, fg=BTN_SUBTLE_FG, font=FONT_SMALL,
            padx=10, pady=3,
        )
        self.btn_export.pack(side=tk.LEFT, padx=(0, 4))

        self._toolbar_sep(bar)

        # ── View group ──
        self.btn_expand_all = _styled_btn(
            bar, f"{EXPAND} Expand", self._expand_all,
            bg=BTN_SUBTLE, fg=BTN_SUBTLE_FG, font=FONT_SMALL,
            padx=8, pady=3,
        )
        self.btn_expand_all.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_collapse_all = _styled_btn(
            bar, f"{COLLAPSE} Collapse", self._collapse_all,
            bg=BTN_SUBTLE, fg=BTN_SUBTLE_FG, font=FONT_SMALL,
            padx=8, pady=3,
        )
        self.btn_collapse_all.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_top = _styled_btn(
            bar, "Top", lambda: self.canvas.yview_moveto(0),
            bg=BTN_SUBTLE, fg=BTN_SUBTLE_FG, font=FONT_SMALL,
            padx=8, pady=3,
        )
        self.btn_top.pack(side=tk.LEFT, padx=(0, 4))

        # ── Right side ──
        _styled_btn(
            bar, "Quit", self.root.destroy,
            bg=BTN_DANGER, fg=BTN_FG, font=FONT_SMALL,
            padx=12, pady=3,
        ).pack(side=tk.RIGHT, padx=(0, 12))

        self._toolbar_sep(bar)

        _styled_btn(
            bar, f"About", self._on_about,
            bg=BTN_SUBTLE, fg=BTN_SUBTLE_FG, font=FONT_SMALL,
            padx=10, pady=3,
        ).pack(side=tk.RIGHT, padx=(0, 4))

    # ---- Input panel -----------------------------------------------------

    def _build_input_panel(self) -> None:
        # Outer wrapper with accent left border for a modern card look
        panel_border = tk.Frame(self.main_frame, bg=ACCENT)
        panel_border.pack(fill=tk.X, padx=10, pady=(8, 0))

        panel = tk.Frame(panel_border, bg=BG_CARD, pady=14, padx=20)
        panel.pack(fill=tk.BOTH, expand=True, padx=(3, 0))  # 3px accent left stripe

        # Section heading
        tk.Label(
            panel, text=f"{DIAMOND}  Compare two companies",
            font=FONT_SECTION, bg=BG_CARD, fg=ACCENT,
        ).pack(anchor=tk.W, pady=(0, 10))

        # Row 1: inputs
        row1 = tk.Frame(panel, bg=BG_CARD)
        row1.pack(fill=tk.X)

        def _make_entry(parent, label_text: str, width: int = 24) -> tk.Entry:
            """Build a labelled entry field."""
            f = tk.Frame(parent, bg=BG_CARD)
            f.pack(side=tk.LEFT, padx=(0, 16))
            tk.Label(f, text=label_text, font=FONT_SMALL,
                     bg=BG_CARD, fg=FG_DIM).pack(anchor=tk.W, pady=(0, 3))
            entry = tk.Entry(
                f, font=FONT, width=width, bg=BG_INPUT, fg=FG,
                insertbackground=FG, relief=tk.FLAT, highlightthickness=2,
                highlightcolor=ACCENT, highlightbackground=BORDER,
            )
            entry.pack(ipady=3)
            return entry

        self.entry_a = _make_entry(row1, "Company A")
        self.entry_b = _make_entry(row1, "Company B")
        self.entry_timeout = _make_entry(row1, "Timeout (s)", width=6)
        self.entry_timeout.insert(0, str(self.cli_args.timeout))

        # Buttons
        btn_frame = tk.Frame(row1, bg=BG_CARD)
        btn_frame.pack(side=tk.LEFT, padx=(12, 0), anchor=tk.S)

        self.btn_compare = _styled_btn(
            btn_frame, f"{DIAMOND}  Compare", self._on_compare,
            padx=22, pady=6,
        )
        self.btn_compare.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_clear = _styled_btn(
            btn_frame, "Clear", self._on_clear,
            bg=BTN_SUBTLE, fg=BTN_SUBTLE_FG, padx=14, pady=6,
        )
        self.btn_clear.pack(side=tk.LEFT)

        # Status
        self.status_var = tk.StringVar(value="Enter two tickers and press Compare")
        tk.Label(
            panel, textvariable=self.status_var, font=FONT_SMALL,
            bg=BG_CARD, fg=FG_DIM, anchor=tk.W,
        ).pack(fill=tk.X, pady=(10, 0))

        # Key bindings
        self.entry_a.bind("<Return>", lambda _: self.entry_b.focus_set())
        self.entry_b.bind("<Return>", lambda _: self._on_compare())
        self.entry_timeout.bind("<Return>", lambda _: self._on_compare())

    # ---- Scrollable result area ------------------------------------------

    def _build_result_area(self) -> None:
        container = tk.Frame(self.main_frame, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(6, 0))

        self.canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=BG)

        self.scroll_frame.bind(
            "<Configure>",
            lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Mouse-wheel scrolling
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        self.canvas.bind_all(
            "<Button-4>", lambda _: self.canvas.yview_scroll(-3, "units"))
        self.canvas.bind_all(
            "<Button-5>", lambda _: self.canvas.yview_scroll(3, "units"))

    # ---- Status bar ------------------------------------------------------

    def _build_statusbar(self) -> None:
        # Top border line
        tk.Frame(self.main_frame, bg=BORDER, height=1).pack(
            fill=tk.X, side=tk.BOTTOM)

        bar = tk.Frame(self.main_frame, bg=BG_SURFACE, height=26)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        from lynx_compare import __version__
        tk.Label(bar, text=f" {LYNX} Lynx Compare v{__version__}", font=FONT_TINY,
                 bg=BG_SURFACE, fg=FG_DIM).pack(side=tk.LEFT, padx=8)

        self.statusbar_right = tk.Label(
            bar, text="", font=FONT_TINY, bg=BG_SURFACE, fg=FG_DIM)
        self.statusbar_right.pack(side=tk.RIGHT, padx=8)

    # ---- Actions ---------------------------------------------------------

    def _on_about(self) -> None:
        AboutDialog(self.root)

    def _on_export(self) -> None:
        if self._last_result is None:
            messagebox.showinfo("Export", "No comparison results to export.\nRun a comparison first.")
            return
        ExportDialog(self.root, self._last_result)

    def _on_compare(self) -> None:
        a = self.entry_a.get().strip()
        b = self.entry_b.get().strip()
        if not a or not b:
            self.status_var.set("Please enter both company identifiers.")
            return

        try:
            timeout = int(self.entry_timeout.get().strip())
            if timeout > 0:
                self.cli_args.timeout = timeout
        except ValueError:
            pass

        self.btn_compare.configure(state=tk.DISABLED)
        self.status_var.set(f"Analysing {a} vs {b}...")
        self.statusbar_right.configure(text=f"Timeout: {self.cli_args.timeout}s")

        thread = threading.Thread(
            target=self._run_comparison, args=(a, b), daemon=True)
        thread.start()

    def _on_clear(self) -> None:
        self.entry_a.delete(0, tk.END)
        self.entry_b.delete(0, tk.END)
        self.entry_a.focus_set()
        self.status_var.set("Cleared. Enter two tickers and press Compare.")

    def _on_reset(self) -> None:
        """Clear results and inputs for a fresh comparison."""
        self._stop_blink()
        for child in self.scroll_frame.winfo_children():
            child.destroy()
        self._warning_entries.clear()
        self._section_cards.clear()
        self._last_result = None
        self._on_clear()
        self.statusbar_right.configure(text="")

    def _expand_all(self) -> None:
        for card in self._section_cards:
            if not card.is_open:
                card.toggle()

    def _collapse_all(self) -> None:
        for card in self._section_cards:
            if card.is_open:
                card.toggle()

    def _stop_blink(self) -> None:
        if self._blink_id is not None:
            self.root.after_cancel(self._blink_id)
            self._blink_id = None

    def _run_comparison(self, company_a: str, company_b: str) -> None:
        try:
            from lynx_compare.cli import _run_analysis, AnalysisTimeoutError
            from lynx_compare.engine import compare

            self.root.after(0, self.status_var.set, f"Analysing {company_a}...")
            report_a = _run_analysis(company_a, self.cli_args)

            self.root.after(0, self.status_var.set, f"Analysing {company_b}...")
            report_b = _run_analysis(company_b, self.cli_args)

            self.root.after(0, self.status_var.set, "Comparing...")
            result = compare(report_a, report_b)

            self.root.after(0, self._display_result, result)

        except AnalysisTimeoutError as e:
            msg = str(e)
            self.root.after(0, lambda: self._show_error("Timeout", msg))
        except Exception as e:
            msg = str(e)
            self.root.after(0, lambda: self._show_error("Error", msg))

    def _show_error(self, title: str, msg: str) -> None:
        self.status_var.set(f"{title}: see dialog.")
        self.btn_compare.configure(state=tk.NORMAL)
        messagebox.showerror(title, msg)

    # ---- Display results -------------------------------------------------

    def _display_result(self, cr: ComparisonResult) -> None:
        self._last_result = cr
        self.status_var.set(f"Done: {cr.ticker_a} vs {cr.ticker_b}")
        self.btn_compare.configure(state=tk.NORMAL)
        wins_a = cr.total_wins_a
        wins_b = cr.total_wins_b
        self.statusbar_right.configure(
            text=f"Metrics: {cr.ticker_a} {wins_a}  :  {wins_b} {cr.ticker_b}"
        )

        self._stop_blink()

        for child in self.scroll_frame.winfo_children():
            child.destroy()
        self._warning_entries.clear()
        self._section_cards.clear()
        self._blink_visible = True

        self._render_warnings(cr.warnings)
        self._render_profile(cr)
        for section in cr.sections:
            self._render_section(section, cr.ticker_a, cr.ticker_b)
        self._render_scoreboard(cr)
        self._render_verdict(cr)

        # Bottom padding
        tk.Frame(self.scroll_frame, bg=BG, height=12).pack(fill=tk.X)

        self.canvas.yview_moveto(0)

        if self._warning_entries:
            self._blink_id = self.root.after(800, self._blink_warnings)

    # ---- Warnings --------------------------------------------------------

    def _render_warnings(self, warnings: list[Warning]) -> None:
        """Render warnings with blinking tags but steady message text."""
        if not warnings:
            return
        color_map = {"sector": WARN_RED, "industry": WARN_ORANGE, "tier": WARN_YELLOW}
        for w in warnings:
            color = color_map.get(w.level, WARN_YELLOW)
            tag = f" {WARN_ICON} {w.level.upper()} MISMATCH "

            row = tk.Frame(self.scroll_frame, bg=BG)
            row.pack(fill=tk.X, padx=12, pady=(4, 0))

            # Left blinking tag
            tag_l = tk.Label(
                row, text=tag, font=FONT_WARN, bg=BG, fg=color,
            )
            tag_l.pack(side=tk.LEFT)

            # Steady message (always visible)
            tk.Label(
                row, text=f" {w.message} ", font=FONT_WARN, bg=BG, fg=color,
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Right blinking tag
            tag_r = tk.Label(
                row, text=tag, font=FONT_WARN, bg=BG, fg=color,
            )
            tag_r.pack(side=tk.RIGHT)

            # Only tag labels go into the blink list
            self._warning_entries.append((tag_l, color))
            self._warning_entries.append((tag_r, color))

    def _blink_warnings(self) -> None:
        """Toggle only the tag labels; message text stays steady."""
        self._blink_visible = not self._blink_visible
        for lbl, original_fg in self._warning_entries:
            if lbl.winfo_exists():
                lbl.configure(fg=original_fg if self._blink_visible else BG)
        self._blink_id = self.root.after(600, self._blink_warnings)

    # ---- Profile ---------------------------------------------------------

    def _render_profile(self, cr: ComparisonResult) -> None:
        card = CollapsibleCard(self.scroll_frame, "Company Profile")
        self._section_cards.append(card)
        frame = card.content

        rows = [
            ("Company", cr.name_a, cr.name_b),
            ("Tier", cr.tier_a, cr.tier_b),
            ("Market Cap", _fmt_mcap(cr.market_cap_a), _fmt_mcap(cr.market_cap_b)),
            ("Sector", cr.sector_a, cr.sector_b),
            ("Industry", cr.industry_a, cr.industry_b),
        ]
        for i, (label, va, vb) in enumerate(rows):
            bg = BG_INPUT if i % 2 == 0 else BG_CARD
            _make_row(frame, bg,
                      va, FG, "", BG_CARD, label, ACCENT, "", BG_CARD, vb, FG)

    # ---- Section ---------------------------------------------------------

    def _render_section(self, section: SectionResult, ta: str, tb: str) -> None:
        if section.winner == "a":
            badge = f"  {TROPHY} {ta} wins {ARROW_L}"
        elif section.winner == "b":
            badge = f"  {ARROW_R} {tb} wins {TROPHY}"
        else:
            badge = "  Tie"

        card = CollapsibleCard(
            self.scroll_frame, f"{section.name.upper()}{badge}",
        )
        self._section_cards.append(card)
        frame = card.content

        # Header
        _make_row(frame, BG_CARD,
                  ta, ACCENT, "", BG_CARD, "Metric", ACCENT, "", BG_CARD, tb, ACCENT,
                  font=FONT_BOLD)

        # Metrics
        for i, m in enumerate(section.metrics):
            bg = BG_INPUT if i % 2 == 0 else BG_CARD
            fg_a = _winner_fg(m.winner, "a")
            fg_b = _winner_fg(m.winner, "b")
            prefix_a = f"{CHECK} " if m.winner == "a" else "  "
            prefix_b = f"{CHECK} " if m.winner == "b" else "  "
            al_text, al_fg = _arrow_text(m.winner, "a")
            ar_text, ar_fg = _arrow_text(m.winner, "b")
            fg_m = FG if m.winner != "na" else FG_DIM

            _make_row(frame, bg,
                      f"{prefix_a}{m.fmt_a}", fg_a,
                      al_text, al_fg,
                      m.label, fg_m,
                      ar_text, ar_fg,
                      f"{prefix_b}{m.fmt_b}", fg_b)

        # Separator + summary
        tk.Frame(frame, bg=BORDER, height=1).pack(fill=tk.X, padx=4, pady=(4, 2))

        sa = f"{section.wins_a}{CHECK}  {section.wins_b}{CROSS}"
        sb = f"{section.wins_b}{CHECK}  {section.wins_a}{CROSS}"
        fg_sa = FG_WIN if section.winner == "a" else (FG_TIE if section.winner == "tie" else FG_LOSE)
        fg_sb = FG_WIN if section.winner == "b" else (FG_TIE if section.winner == "tie" else FG_LOSE)

        r = tk.Frame(frame, bg=BG_CARD)
        r.pack(fill=tk.X, pady=(0, 4))
        tk.Label(r, text=sa, font=FONT_BOLD, bg=BG_CARD, fg=fg_sa,
                 width=W_VAL, anchor=tk.E).pack(side=tk.LEFT, padx=(4, 0))
        tk.Label(r, text="", font=FONT, bg=BG_CARD,
                 width=W_ARROW).pack(side=tk.LEFT)
        tk.Label(r, text="SECTION RESULT", font=FONT_BOLD, bg=BG_CARD, fg=FG,
                 width=W_METRIC, anchor=tk.CENTER).pack(side=tk.LEFT)
        tk.Label(r, text="", font=FONT, bg=BG_CARD,
                 width=W_ARROW).pack(side=tk.LEFT)
        tk.Label(r, text=sb, font=FONT_BOLD, bg=BG_CARD, fg=fg_sb,
                 width=W_VAL, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 4))

    # ---- Scoreboard ------------------------------------------------------

    def _render_scoreboard(self, cr: ComparisonResult) -> None:
        card = CollapsibleCard(self.scroll_frame, "Section Scoreboard")
        self._section_cards.append(card)
        frame = card.content

        hdr = tk.Frame(frame, bg=BG_CARD)
        hdr.pack(fill=tk.X)
        for text, w in [("Section", 20), (cr.ticker_a, 10), ("Winner", 20), (cr.ticker_b, 10)]:
            tk.Label(hdr, text=text, font=FONT_BOLD, bg=BG_CARD, fg=ACCENT,
                     width=w, anchor=tk.CENTER).pack(side=tk.LEFT, padx=4)

        for i, s in enumerate(cr.sections):
            bg = BG_INPUT if i % 2 == 0 else BG_CARD
            if s.winner == "a":
                wtext, fg_w = f"{ARROW_L} {cr.ticker_a}", FG_WIN
                fg_a, fg_b = FG_WIN, FG_LOSE
            elif s.winner == "b":
                wtext, fg_w = f"{cr.ticker_b} {ARROW_R}", FG_WIN
                fg_a, fg_b = FG_LOSE, FG_WIN
            else:
                wtext, fg_w = "Tie", FG_TIE
                fg_a = fg_b = FG_TIE

            r = tk.Frame(frame, bg=bg)
            r.pack(fill=tk.X)
            tk.Label(r, text=s.name, font=FONT, bg=bg, fg=FG,
                     width=20, anchor=tk.CENTER).pack(side=tk.LEFT, padx=4)
            tk.Label(r, text=f"{s.wins_a}W", font=FONT, bg=bg, fg=fg_a,
                     width=10, anchor=tk.CENTER).pack(side=tk.LEFT, padx=4)
            tk.Label(r, text=wtext, font=FONT_BOLD, bg=bg, fg=fg_w,
                     width=20, anchor=tk.CENTER).pack(side=tk.LEFT, padx=4)
            tk.Label(r, text=f"{s.wins_b}W", font=FONT, bg=bg, fg=fg_b,
                     width=10, anchor=tk.CENTER).pack(side=tk.LEFT, padx=4)

    # ---- Verdict ---------------------------------------------------------

    def _render_verdict(self, cr: ComparisonResult) -> None:
        outer = tk.Frame(self.scroll_frame, bg=BG)
        outer.pack(fill=tk.X, padx=12, pady=(10, 0))

        if cr.overall_winner == "a":
            border_col = FG_WIN
        elif cr.overall_winner == "b":
            border_col = FG_WIN
        else:
            border_col = FG_TIE

        frame = tk.Frame(outer, bg=BG_CARD,
                         highlightbackground=border_col, highlightthickness=2)
        frame.pack(fill=tk.X)

        inner = tk.Frame(frame, bg=BG_CARD, pady=14, padx=20)
        inner.pack(fill=tk.X)

        tk.Label(inner, text=f"{TROPHY} FINAL VERDICT {TROPHY}",
                 font=FONT_SECTION, bg=BG_CARD, fg=TROPHY_COL).pack(pady=(0, 10))

        sw_a = f"{cr.sections_won_a:>2}"
        sw_b = f"{cr.sections_won_b:<2}"
        mw_a = f"{cr.total_wins_a:>2}"
        mw_b = f"{cr.total_wins_b:<2}"

        sec_text = f"Sections Won     {cr.ticker_a} {sw_a}  :  {sw_b} {cr.ticker_b}"
        if cr.sections_tied:
            sec_text += f"   ({cr.sections_tied} tied)"
        tk.Label(inner, text=sec_text, font=FONT, bg=BG_CARD, fg=FG).pack()

        met_text = f"Metrics Won      {cr.ticker_a} {mw_a}  :  {mw_b} {cr.ticker_b}"
        if cr.total_ties:
            met_text += f"   ({cr.total_ties} tied)"
        tk.Label(inner, text=met_text, font=FONT, bg=BG_CARD, fg=FG).pack(pady=(0, 14))

        if cr.overall_winner == "a":
            winner_text = (
                f"{CROWN}  {ARROW_L}  OVERALL WINNER: "
                f"{cr.name_a} ({cr.ticker_a})  {CROWN}"
            )
            fg_color = CROWN_COL
        elif cr.overall_winner == "b":
            winner_text = (
                f"{CROWN}  OVERALL WINNER: "
                f"{cr.name_b} ({cr.ticker_b})  {ARROW_R}  {CROWN}"
            )
            fg_color = CROWN_COL
        else:
            winner_text = "IT'S A TIE"
            fg_color = FG_TIE

        tk.Label(inner, text=winner_text, font=FONT_VERDICT,
                 bg=BG_CARD, fg=fg_color).pack()

    # ---- Run -------------------------------------------------------------

    def run(self) -> None:
        self.root.mainloop()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_gui(args) -> None:
    """Launch the tkinter GUI."""
    app = LynxCompareGUI(cli_args=args)
    app.run()
