#!/usr/bin/env python3
# ============================================================
# COMPILER DESIGN PROJECT - Air University Kamra Campus
# Compiler Construction Lab
# Instructor: Ms. Rubab Hafeez
#
# This project demonstrates all compiler phases:
#   Phase 1: Lexical Analysis  (Lab 3, 4, 8)
#   Phase 2: Syntax Analysis   (Lab 6, 7, 9)
#   Phase 3: Semantic Analysis (Lab 10)
#   + Symbol Table             (Lab 5, 8)
#
# GUI: Modern dark-theme IDE using tkinter
# ============================================================

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import sys
import os

# Add project root to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer.lexer         import Lexer
from parser.parser       import Parser
from semantic.semantic   import SemanticAnalyzer
from examples.examples   import ALL_EXAMPLES

# ─────────────────────────── COLOUR PALETTE ────────────────────────────────
BG        = "#1e1e2e"   # main background (dark navy)
BG2       = "#181825"   # sidebar / panel background
BG3       = "#313244"   # input area / editor background
ACCENT    = "#89b4fa"   # blue accent
ACCENT2   = "#a6e3a1"   # green (success)
ERR       = "#f38ba8"   # red (error)
WARN      = "#fab387"   # orange (warning)
TEXT      = "#cdd6f4"   # main text
TEXT_DIM  = "#6c7086"   # dimmed text
KEYWORD_C = "#cba6f7"   # purple for keywords
NUMBER_C  = "#fab387"   # orange for numbers
STRING_C  = "#a6e3a1"   # green for strings
OP_C      = "#89dceb"   # cyan for operators
BTN_BG    = "#45475a"   # button background
BTN_HOVER = "#585b70"   # button hover


class CompilerIDE(tk.Tk):
    """
    Main application window.
    Designed to look like a lightweight IDE with:
    - Left panel: buttons + examples
    - Center: code editor with line numbers
    - Right/bottom tabs: output panels for each compiler phase
    """

    def __init__(self):
        super().__init__()
        self.title("Mini Compiler — Air University Kamra Campus")
        self.geometry("1280x780")
        self.minsize(900, 600)
        self.configure(bg=BG)

        # Backend objects (one per session)
        self.lexer    = Lexer()
        self.parser   = Parser()
        self.semantic = SemanticAnalyzer()

        # Storage for last run results
        self._last_tokens = []

        self._setup_fonts()
        self._build_ui()
        self._load_example("Example 1: Basic Arithmetic")

    # ─────────────────── FONTS ──────────────────────────────────────────────

    def _setup_fonts(self):
        self.font_code  = font.Font(family="Courier New", size=11)
        self.font_ui    = font.Font(family="Segoe UI",    size=10)
        self.font_bold  = font.Font(family="Segoe UI",    size=10, weight="bold")
        self.font_title = font.Font(family="Segoe UI",    size=13, weight="bold")
        self.font_small = font.Font(family="Segoe UI",    size=9)

    # ─────────────────── UI LAYOUT ──────────────────────────────────────────

    def _build_ui(self):
        # ── Title bar ──────────────────────────────────────────────────────
        self._build_titlebar()

        # ── Main content (sidebar + editor + output) ───────────────────────
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=0, pady=0)

        # Left sidebar
        self._build_sidebar(main)

        # Center + right split
        center = tk.Frame(main, bg=BG)
        center.pack(side="left", fill="both", expand=True)

        # Editor (top half)
        self._build_editor(center)

        # Output tabs (bottom half)
        self._build_output_tabs(center)

        # ── Status bar ─────────────────────────────────────────────────────
        self._build_statusbar()

    def _build_titlebar(self):
        bar = tk.Frame(self, bg=BG2, height=46)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Logo dot
        dot = tk.Label(bar, text="●", fg=ACCENT, bg=BG2,
                        font=font.Font(size=18))
        dot.pack(side="left", padx=(14, 4), pady=6)

        title = tk.Label(bar,
                          text="Mini Compiler  |  Air University Kamra Campus",
                          fg=TEXT, bg=BG2, font=self.font_title)
        title.pack(side="left", pady=6)

        subtitle = tk.Label(bar,
                             text="Compiler Construction Lab  —  Ms. Rubab Hafeez",
                             fg=TEXT_DIM, bg=BG2, font=self.font_small)
        subtitle.pack(side="right", padx=16, pady=6)

    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=BG2, width=210)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        # Section: Run Phases
        self._sidebar_section(sb, "▶  RUN PHASES")

        btn_data = [
            ("🔍  Lexical Analysis",  ACCENT,  self._run_lexer),
            ("🌿  Syntax Analysis",   "#cba6f7", self._run_parser),
            ("🔬  Semantic Analysis", "#fab387", self._run_semantic),
            ("📋  Symbol Table",      ACCENT2,  self._run_symbol_table),
        ]
        for label, color, cmd in btn_data:
            self._sidebar_btn(sb, label, color, cmd)

        # Section: File
        self._sidebar_section(sb, "📁  FILE")
        self._sidebar_btn(sb, "📂  Open File",   TEXT_DIM, self._open_file)
        self._sidebar_btn(sb, "💾  Save File",   TEXT_DIM, self._save_file)
        self._sidebar_btn(sb, "🗑️  Clear All",   ERR,       self._clear_all)

        # Section: Examples
        self._sidebar_section(sb, "📚  EXAMPLES")
        for name in ALL_EXAMPLES:
            short = name.split(":")[0]
            btn = tk.Button(sb, text=f"  {short}",
                            bg=BG2, fg=TEXT_DIM,
                            font=self.font_small,
                            relief="flat", anchor="w",
                            activebackground=BG3, activeforeground=TEXT,
                            cursor="hand2",
                            command=lambda n=name: self._load_example(n))
            btn.pack(fill="x", padx=8, pady=1)
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg=ACCENT))
            btn.bind("<Leave>", lambda e, b=btn: b.config(fg=TEXT_DIM))

        # ── Phase legend ───────────────────────────────────────────────────
        self._sidebar_section(sb, "ℹ️  PHASES")
        legends = [
            ("1. Lexical  (Lab 3,4,8)", ACCENT),
            ("2. Syntax   (Lab 6,7,9)", "#cba6f7"),
            ("3. Semantic (Lab 10)",    WARN),
            ("4. Sym.Table(Lab 5,8)",  ACCENT2),
        ]
        for txt, col in legends:
            lbl = tk.Label(sb, text=txt, fg=col, bg=BG2,
                           font=self.font_small, anchor="w")
            lbl.pack(fill="x", padx=12, pady=1)

    def _sidebar_section(self, parent, title):
        f = tk.Frame(parent, bg=BG2)
        f.pack(fill="x", padx=8, pady=(12, 2))
        tk.Label(f, text=title, fg=TEXT_DIM, bg=BG2,
                 font=self.font_small).pack(anchor="w")
        tk.Frame(parent, bg=BTN_BG, height=1).pack(fill="x", padx=8, pady=2)

    def _sidebar_btn(self, parent, text, color, cmd):
        btn = tk.Button(parent, text=text,
                        bg=BTN_BG, fg=color,
                        font=self.font_ui,
                        relief="flat", anchor="w",
                        padx=10, pady=6,
                        activebackground=BTN_HOVER, activeforeground=color,
                        cursor="hand2",
                        command=cmd)
        btn.pack(fill="x", padx=8, pady=3)
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=BTN_HOVER))
        btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BTN_BG))

    def _build_editor(self, parent):
        """Code editor with line numbers."""
        hdr = tk.Frame(parent, bg=BG3, height=28)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=" 📝  Source Code Editor",
                 fg=ACCENT, bg=BG3, font=self.font_bold).pack(side="left", padx=8)
        tk.Label(hdr, text="TINY-C  |  UTF-8",
                 fg=TEXT_DIM, bg=BG3, font=self.font_small).pack(side="right", padx=10)

        editor_frame = tk.Frame(parent, bg=BG3)
        editor_frame.pack(fill="both", expand=True)

        # Line numbers
        self.line_numbers = tk.Text(
            editor_frame, width=4, bg=BG2, fg=TEXT_DIM,
            font=self.font_code, state="disabled",
            relief="flat", padx=4, pady=4,
            highlightthickness=0, selectbackground=BG2
        )
        self.line_numbers.pack(side="left", fill="y")

        # Separator
        tk.Frame(editor_frame, bg=BTN_BG, width=1).pack(side="left", fill="y")

        # Main code area
        self.code_editor = tk.Text(
            editor_frame, bg=BG3, fg=TEXT,
            insertbackground=ACCENT,
            font=self.font_code,
            relief="flat", padx=10, pady=4,
            wrap="none",
            highlightthickness=0,
            selectbackground=BTN_HOVER,
            undo=True
        )
        self.code_editor.pack(side="left", fill="both", expand=True)

        # Scrollbar
        vscroll = tk.Scrollbar(editor_frame, orient="vertical",
                                command=self._sync_scroll, bg=BG2)
        vscroll.pack(side="right", fill="y")
        self.code_editor.config(yscrollcommand=vscroll.set)

        # Syntax highlight tags
        self.code_editor.tag_config("keyword", foreground=KEYWORD_C)
        self.code_editor.tag_config("number",  foreground=NUMBER_C)
        self.code_editor.tag_config("string",  foreground=STRING_C)
        self.code_editor.tag_config("comment", foreground=TEXT_DIM, font=self.font_code)
        self.code_editor.tag_config("operator",foreground=OP_C)
        self.code_editor.tag_config("error_line", background="#3d1a1a")

        # Bind events
        self.code_editor.bind("<KeyRelease>", self._on_code_change)
        self.code_editor.bind("<MouseWheel>", self._on_mousewheel)

    def _build_output_tabs(self, parent):
        """Bottom tab notebook with output panels."""
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.TNotebook",
                        background=BG, borderwidth=0)
        style.configure("Dark.TNotebook.Tab",
                        background=BG2, foreground=TEXT_DIM,
                        padding=[12, 6], borderwidth=0,
                        font=("Segoe UI", 9))
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", BG3)],
                  foreground=[("selected", ACCENT)])

        self.notebook = ttk.Notebook(parent, style="Dark.TNotebook", height=260)
        self.notebook.pack(fill="both", padx=0, pady=0)

        self.tab_tokens   = self._make_tab("🔍 Tokens")
        self.tab_parse    = self._make_tab("🌿 Parse Steps")
        self.tab_semantic = self._make_tab("🔬 Semantic")
        self.tab_symtable = self._make_tab("📋 Symbol Table")
        self.tab_console  = self._make_tab("🖥️ Console")

        self.notebook.add(self.tab_tokens,   text="  🔍 Tokens   ")
        self.notebook.add(self.tab_parse,    text="  🌿 Parse Steps   ")
        self.notebook.add(self.tab_semantic, text="  🔬 Semantic   ")
        self.notebook.add(self.tab_symtable, text="  📋 Symbol Table   ")
        self.notebook.add(self.tab_console,  text="  🖥️ Console   ")

        # Tokens tab: treeview table
        self._build_token_table()
        # Other tabs: plain text output
        self.parse_text    = self._text_output(self.tab_parse)
        self.semantic_text = self._text_output(self.tab_semantic)
        self.symtable_text = self._text_output(self.tab_symtable)
        self.console_text  = self._text_output(self.tab_console)

        # Console welcome
        self._console_log("Mini Compiler ready. Load an example or type your code.", ACCENT2)
        self._console_log("Based on Air University Compiler Construction Lab (Labs 3–10).", TEXT_DIM)

    def _make_tab(self, title):
        frame = tk.Frame(self.notebook, bg=BG)
        return frame

    def _text_output(self, parent):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="both", expand=True)
        txt = tk.Text(frame, bg=BG, fg=TEXT,
                      font=self.font_code, relief="flat",
                      padx=10, pady=6,
                      wrap="word", state="disabled",
                      highlightthickness=0,
                      selectbackground=BTN_BG)
        vsb = tk.Scrollbar(frame, bg=BG2, command=txt.yview)
        vsb.pack(side="right", fill="y")
        txt.config(yscrollcommand=vsb.set)
        txt.pack(fill="both", expand=True)
        # Color tags
        txt.tag_config("ok",      foreground=ACCENT2)
        txt.tag_config("err",     foreground=ERR)
        txt.tag_config("warn",    foreground=WARN)
        txt.tag_config("info",    foreground=ACCENT)
        txt.tag_config("dim",     foreground=TEXT_DIM)
        txt.tag_config("heading", foreground=ACCENT, font=self.font_bold)
        return txt

    def _build_token_table(self):
        """Treeview table for token output."""
        frame = tk.Frame(self.tab_tokens, bg=BG)
        frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.configure("Dark.Treeview",
                        background=BG, foreground=TEXT,
                        fieldbackground=BG, rowheight=22,
                        borderwidth=0, font=("Courier New", 10))
        style.configure("Dark.Treeview.Heading",
                        background=BG2, foreground=ACCENT,
                        font=("Segoe UI", 9, "bold"),
                        borderwidth=0)
        style.map("Dark.Treeview",
                  background=[("selected", BTN_BG)],
                  foreground=[("selected", TEXT)])

        cols = ("Line", "Token", "Type")
        self.token_tree = ttk.Treeview(frame, columns=cols,
                                        show="headings",
                                        style="Dark.Treeview")
        for col in cols:
            self.token_tree.heading(col, text=col)
        self.token_tree.column("Line",  width=60,  anchor="center")
        self.token_tree.column("Token", width=200, anchor="w")
        self.token_tree.column("Type",  width=150, anchor="w")

        vsb = ttk.Scrollbar(frame, orient="vertical",
                             command=self.token_tree.yview)
        self.token_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.token_tree.pack(fill="both", expand=True)

    def _build_statusbar(self):
        bar = tk.Frame(self, bg=BG2, height=22)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self.status_var = tk.StringVar(value="  Ready")
        lbl = tk.Label(bar, textvariable=self.status_var,
                        fg=TEXT_DIM, bg=BG2, font=self.font_small, anchor="w")
        lbl.pack(side="left", padx=8)

        self.line_col_var = tk.StringVar(value="Ln 1, Col 1")
        tk.Label(bar, textvariable=self.line_col_var,
                  fg=TEXT_DIM, bg=BG2, font=self.font_small).pack(side="right", padx=8)

    # ─────────────────── COMPILER ACTIONS ───────────────────────────────────

    def _run_lexer(self):
        """Run lexical analysis and display tokens."""
        source = self.code_editor.get("1.0", "end-1c")
        if not source.strip():
            self._set_status("⚠  No source code.", WARN)
            return

        tokens, errors = self.lexer.tokenize(source)
        self._last_tokens = tokens

        # Clear token table
        for row in self.token_tree.get_children():
            self.token_tree.delete(row)

        # Populate with alternating row colors
        for i, tok in enumerate(tokens):
            tag = tok.token_type.lower()
            self.token_tree.insert("", "end",
                                    values=(tok.line, tok.value, tok.token_type),
                                    tags=(tag,))

        # Color rows by token type
        self.token_tree.tag_configure("keyword",    foreground=KEYWORD_C)
        self.token_tree.tag_configure("integer",    foreground=NUMBER_C)
        self.token_tree.tag_configure("float",      foreground=NUMBER_C)
        self.token_tree.tag_configure("identifier", foreground=TEXT)
        self.token_tree.tag_configure("operator",   foreground=OP_C)
        self.token_tree.tag_configure("string",     foreground=STRING_C)
        self.token_tree.tag_configure("separator",  foreground=TEXT_DIM)

        self.notebook.select(0)  # switch to tokens tab

        # Console log
        self._console_log(f"\n─── Lexical Analysis ───", ACCENT)
        self._console_log(f"  Tokens found: {len(tokens)}", ACCENT2 if not errors else WARN)
        for err in errors:
            self._console_log(f"  {err}", ERR)
        if not errors:
            self._console_log("  ✓  No lexical errors.", ACCENT2)

        self._set_status(
            f"✓  Lexical: {len(tokens)} tokens" + (f"  |  {len(errors)} error(s)" if errors else ""),
            ACCENT2 if not errors else ERR
        )
        self._apply_syntax_highlight(source)

    def _run_parser(self):
        """Run syntax analysis."""
        if not self._last_tokens:
            self._run_lexer()

        success, steps, errors = self.parser.parse(self._last_tokens)

        out = self.parse_text
        self._clear_text(out)

        self._write(out, "─── Syntax Analysis (SLR Shift-Reduce) ───\n", "heading")
        self._write(out, "Based on Lab 7: TINY C grammar\n\n", "dim")

        for step in steps:
            if step.startswith("SHIFT"):
                self._write(out, f"  {step}\n", "info")
            elif step.startswith("REDUCE"):
                self._write(out, f"  {step}\n", "ok")
            else:
                self._write(out, f"  {step}\n", "dim")

        self._write(out, "\n", "dim")
        if errors:
            self._write(out, "✗  Syntax Errors:\n", "err")
            for e in errors:
                self._write(out, f"   {e}\n", "err")
        else:
            self._write(out, "✓  Syntax is VALID.\n", "ok")

        self.notebook.select(1)
        self._console_log(f"\n─── Syntax Analysis ───", "#cba6f7")
        self._console_log(
            f"  {'✓  Valid syntax.' if success else '✗  Syntax errors found.'} ({len(steps)} steps)",
            ACCENT2 if success else ERR
        )
        for e in errors:
            self._console_log(f"  {e}", ERR)

        self._set_status(
            "✓  Syntax valid" if success else f"✗  Syntax: {len(errors)} error(s)",
            ACCENT2 if success else ERR
        )

    def _run_semantic(self):
        """Run semantic analysis."""
        if not self._last_tokens:
            self._run_lexer()

        sym_table, errors, warnings = self.semantic.analyze(self._last_tokens)

        out = self.semantic_text
        self._clear_text(out)

        self._write(out, "─── Semantic Analysis ───\n", "heading")
        self._write(out, "Based on Lab 10: type checking, undeclared vars, div by zero\n\n", "dim")

        if warnings:
            for w in warnings:
                self._write(out, f"⚠  {w}\n", "warn")

        if errors:
            self._write(out, f"✗  Semantic Errors ({len(errors)}):\n", "err")
            for e in errors:
                self._write(out, f"   {e}\n", "err")
        else:
            self._write(out, "✓  No semantic errors found.\n", "ok")

        self.notebook.select(2)
        self._console_log(f"\n─── Semantic Analysis ───", WARN)
        self._console_log(
            f"  {len(errors)} error(s), {len(warnings)} warning(s).",
            ACCENT2 if not errors else ERR
        )

        self._set_status(
            f"✓  Semantic OK" if not errors else f"✗  Semantic: {len(errors)} error(s)",
            ACCENT2 if not errors else ERR
        )

    def _run_symbol_table(self):
        """Display symbol table."""
        if not self._last_tokens:
            self._run_lexer()

        sym_table, _, _ = self.semantic.analyze(self._last_tokens)
        entries = sym_table.get_all()

        out = self.symtable_text
        self._clear_text(out)

        self._write(out, "─── Symbol Table ───\n", "heading")
        self._write(out, "Based on Lab 5 (arrays) and Lab 8 (lexer integration)\n\n", "dim")

        if not entries:
            self._write(out, "  (No symbols found. Run analysis first.)\n", "dim")
        else:
            # Header
            header = f"{'Name':<16} {'Type':<10} {'Scope':<10} {'Value':<12} {'Address'}\n"
            sep    = "─" * 60 + "\n"
            self._write(out, header, "info")
            self._write(out, sep,    "dim")
            for e in entries:
                row = (f"  {e['name']:<14} {e['type']:<10} "
                       f"{e['scope']:<10} {str(e['value']):<12} {e['address']}\n")
                self._write(out, row, "ok")

        self.notebook.select(3)
        self._console_log(f"\n─── Symbol Table ───", ACCENT2)
        self._console_log(f"  {len(entries)} symbol(s) found.", ACCENT2)
        self._set_status(f"Symbol Table: {len(entries)} entry/entries", ACCENT2)

    # ─────────────────── HELPERS ────────────────────────────────────────────

    def _write(self, widget, text, tag=""):
        widget.config(state="normal")
        widget.insert("end", text, tag)
        widget.config(state="disabled")
        widget.see("end")

    def _clear_text(self, widget):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.config(state="disabled")

    def _console_log(self, msg, color=None):
        self.console_text.config(state="normal")
        if color:
            tag = f"col_{color.replace('#', '')}"
            self.console_text.tag_config(tag, foreground=color)
            self.console_text.insert("end", msg + "\n", tag)
        else:
            self.console_text.insert("end", msg + "\n")
        self.console_text.config(state="disabled")
        self.console_text.see("end")

    def _set_status(self, msg, color=TEXT_DIM):
        self.status_var.set(f"  {msg}")
        # Rebuild status label with color — simpler: just update text
        # (full colour change needs a reference, kept simple here)

    def _clear_all(self):
        self.code_editor.delete("1.0", "end")
        self._last_tokens = []
        for w in [self.parse_text, self.semantic_text,
                   self.symtable_text, self.console_text]:
            self._clear_text(w)
        for row in self.token_tree.get_children():
            self.token_tree.delete(row)
        self._console_log("All cleared.", TEXT_DIM)
        self._set_status("Cleared.")

    def _open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Text/Code files", "*.txt *.c *.py *.tc"), ("All files", "*.*")]
        )
        if path:
            with open(path, "r") as f:
                code = f.read()
            self.code_editor.delete("1.0", "end")
            self.code_editor.insert("1.0", code)
            self._console_log(f"Opened: {path}", ACCENT)

    def _save_file(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".tc",
            filetypes=[("TINY-C files", "*.tc"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            code = self.code_editor.get("1.0", "end-1c")
            with open(path, "w") as f:
                f.write(code)
            self._console_log(f"Saved: {path}", ACCENT2)

    def _load_example(self, name):
        code = ALL_EXAMPLES.get(name, "")
        self.code_editor.delete("1.0", "end")
        self.code_editor.insert("1.0", code)
        self._last_tokens = []
        self._console_log(f"Loaded: {name}", ACCENT)
        self._update_line_numbers()
        self._apply_syntax_highlight(code)

    # ─────────────────── EDITOR FEATURES ────────────────────────────────────

    def _on_code_change(self, event=None):
        self._update_line_numbers()
        code = self.code_editor.get("1.0", "end-1c")
        self._apply_syntax_highlight(code)
        # Update cursor position in status bar
        pos = self.code_editor.index("insert")
        line, col = pos.split(".")
        self.line_col_var.set(f"Ln {line}, Col {int(col)+1}")

    def _update_line_numbers(self):
        """Refresh the line number gutter."""
        code = self.code_editor.get("1.0", "end")
        lines = code.count("\n")
        nums = "\n".join(str(i + 1) for i in range(lines))
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", nums)
        self.line_numbers.config(state="disabled")

    def _sync_scroll(self, *args):
        self.code_editor.yview(*args)
        self.line_numbers.yview(*args)

    def _on_mousewheel(self, event):
        self.line_numbers.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _apply_syntax_highlight(self, code):
        """
        Basic syntax highlighting using the same regex patterns
        as the lexer (Lab 3 concept).
        """
        import re
        editor = self.code_editor

        # Remove all existing highlight tags
        for tag in ("keyword", "number", "string", "comment", "operator"):
            editor.tag_remove(tag, "1.0", "end")

        patterns = [
            ("comment",  r'//[^\n]*'),
            ("string",   r'"[^"]*"'),
            ("keyword",  r'\b(?:int|float|char|if|else|while|for|return|print|begin|end)\b'),
            ("number",   r'\b\d+\.?\d*\b'),
            ("operator", r'[+\-*/=<>!]=?|&&|\|\|'),
        ]

        for tag, pattern in patterns:
            for match in re.finditer(pattern, code):
                start_idx = f"1.0 + {match.start()} chars"
                end_idx   = f"1.0 + {match.end()} chars"
                editor.tag_add(tag, start_idx, end_idx)


# ─────────────────────────── ENTRY POINT ────────────────────────────────────

if __name__ == "__main__":
    app = CompilerIDE()
    app.mainloop()
