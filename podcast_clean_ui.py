"""
PodcastClean — Beautiful Desktop UI
=====================================
Run with: py -3.11 podcast_clean_ui.py

First install customtkinter:
  py -3.11 -m pip install customtkinter
"""

import base64
import os
import sys
import math
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

# ── Windows HiDPI fix — must run before any UI is created ──────────────────
if sys.platform == "win32":
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

import warnings
warnings.filterwarnings("ignore", message=".*Triton.*")
warnings.filterwarnings("ignore", message=".*triton.*")
warnings.filterwarnings("ignore", message=".*ffmpeg.*")
import customtkinter as ctk
from PIL import Image as PILImage, ImageDraw as PILImageDraw

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")

# ── Profanity lists ──────────────────────────────────────────────────────────

def _decode_word_blob(blob):
    return base64.b64decode(blob.encode("ascii")).decode("utf-8").split("|")

_CURSE_WORDS_B64 = (
    "YXBlc2hpdHxhcnNlfGFyc2Vob2xlfGFzc2Nsb3dufGFzc2VzfGFzc2ZhY2V8YXNzaGF0fGFzc2hvbGV8YXNzd2lwZXxiYWRhc3N8"
    "YmFzdGFyZHxiYXN0YXJkc3xiaXRjaHxiaXRjaGFzc3xiaXRjaGVzfGJpdGNoaW5nfGJpdGNoeXxib2xsb2Nrc3xidWxsb2Nrc3xidWxs"
    "c2hpdHxjb2NraGVhZHxjb2Nrc3Vja2VyfGNvY2t3b21ibGV8Y3JhcHxjcmFwcHl8Y3JvdGNofGN1bnR8Y3VudHN8ZGlja2ZhY2V8ZGlj"
    "a2hlYWR8ZGlja3dhZHxkaWNrd2VlZHxkaXBzaGl0fGRvdWNoZXxkb3VjaGViYWd8ZG91Y2hlYmFnZ2VyeXxkdW1iYXNzfGZ1Y2t8ZnVj"
    "a2VkfGZ1Y2tlcnxmdWNrZmFjZXxmdWNraGVhZHxmdWNraW58ZnVja2luZ3xmdWNrc3xmdWNrdXB8ZnVja3dpdHxob3JzZXNoaXR8amFj"
    "a2Fzc3xtb3RoZXJmdWNrfG1vdGhlcmZ1Y2tlcnxtb3RoZXJmdWNraW5nfG5pbmNvbXBvb3B8bnVtYm51dHN8cGlzc2VkfHBpc3NoZWFk"
    "fHBpc3Npbmd8cGlzc29mZnxwcmlja3xwcmlja3N8c2hpdHxzaGl0c3xzaGl0c3Rvcm18c2hpdHRlZHxzaGl0dGluZ3xzaGl0dHl8c2th"
    "bmt8c2thbmt5fHNsYWd8c2xhZ3N8c21hcnRhc3N8dG9zc2VyfHRvc3NlcnN8dHdhdHx0d2F0c3x0d2F0d2FmZmxlc3x3YW5rZXJ8d2Fu"
    "a2Vyc3x3YW5raW5nfHdob3JlfHdob3JlaG91c2V8d2hvcmVz"
)
_RELIGIOUS_WORDS_B64 = (
    "Y2hyaXNzYWtlfGNocmlzdHxjaHJpc3RzYWtlfGRhbW1pdHxkYW1ufGRhbW5lZHxkYW1uaXR8Z29kfGdvZGF3ZnVsfGdvZGRhbXxnb2Rk"
    "YW1taXR8Z29kZGFtbnxnb2RkYW1uZWR8Z29kZGFtbml0fGdvZGZvcnNha2VufGhlbGx8aG9seWNyYXB8aG9seWhlbGx8aG9seXNoaXR8"
    "amVzdXN8amVzdXNjaHJpc3R8amVzdXNmfGxvcmR8c29ub2ZhfHNvbm9mYWJpdGNofHNvbm9mYWd1bnxzd2VldGplc3Vz"
)

CURSE_WORDS = _decode_word_blob(_CURSE_WORDS_B64)
RELIGIOUS_WORDS = _decode_word_blob(_RELIGIOUS_WORDS_B64)

def obfuscate_word(word):
    """Mask most alphabetic characters while keeping punctuation intact."""
    chars = list(word)
    alpha_positions = [idx for idx, ch in enumerate(chars) if ch.isalpha()]
    if not alpha_positions:
        return word
    if len(alpha_positions) == 1:
        chars[alpha_positions[0]] = "*"
        return "".join(chars)
    if len(alpha_positions) == 2:
        chars[alpha_positions[1]] = "*"
        return "".join(chars)
    for idx in alpha_positions[1:-1]:
        chars[idx] = "*"
    return "".join(chars)

# ── Colors ──────────────────────────────────────────────────────────────────

DARK_BG    = "#e4e4e4"
CARD_BG    = "#f5f5f5"
CARD2_BG   = "#e0e0e0"
CARD2_H    = "#d4d4d4"
ACCENT     = "#505050"
ACCENT_H   = "#3a3a3a"
GREEN      = "#4a9e6b"
YELLOW     = "#b07030"
TEXT       = "#1e1e1e"
TEXT_RGB   = (30, 30, 30)
WHITE      = "#ffffff"
MUTED      = "#808080"
BORDER     = "#b0b0b0"
INPUT_BG   = "#f0f0f0"
LOG_BG     = "#eaeaea"
LOG_TEXT   = "#404040"
ERROR      = "#ff6b6b"

# ── Icons (drawn vector-like for crisp scaling) ─────────────────────────────
def _mode_icon(kind, color, size=24):
    """Render a high-quality mode icon and return a CTkImage."""
    # Keep a high-res source image so CTk can resample cleanly on DPI scaling.
    scale = 10
    canvas = size * scale
    stroke = max(8, int(canvas * 0.075))

    if isinstance(color, str):
        color_rgba = color
    else:
        color_rgba = (*color, 255) if len(color) == 3 else tuple(color)

    img = PILImage.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    d = PILImageDraw.Draw(img)

    # Shared speaker body used by bleep/mute.
    speaker = [
        (int(canvas * 0.14), int(canvas * 0.38)),
        (int(canvas * 0.33), int(canvas * 0.38)),
        (int(canvas * 0.54), int(canvas * 0.22)),
        (int(canvas * 0.54), int(canvas * 0.78)),
        (int(canvas * 0.33), int(canvas * 0.62)),
        (int(canvas * 0.14), int(canvas * 0.62)),
    ]

    if kind in ("bleep", "mute"):
        d.polygon(speaker, fill=color_rgba)

    if kind == "bleep":
        d.arc(
            (int(canvas * 0.50), int(canvas * 0.20), int(canvas * 0.88), int(canvas * 0.80)),
            start=-45, end=45, fill=color_rgba, width=stroke
        )
        d.arc(
            (int(canvas * 0.58), int(canvas * 0.30), int(canvas * 0.84), int(canvas * 0.70)),
            start=-45, end=45, fill=color_rgba, width=stroke
        )
    elif kind == "mute":
        d.line(
            (int(canvas * 0.58), int(canvas * 0.22), int(canvas * 0.88), int(canvas * 0.80)),
            fill=color_rgba, width=stroke + 2
        )
    elif kind == "cut":
        x_off = 0
        d.ellipse(
            (int(canvas * 0.12) + x_off, int(canvas * 0.18), int(canvas * 0.40) + x_off, int(canvas * 0.46)),
            outline=color_rgba, width=stroke
        )
        d.ellipse(
            (int(canvas * 0.12) + x_off, int(canvas * 0.54), int(canvas * 0.40) + x_off, int(canvas * 0.82)),
            outline=color_rgba, width=stroke
        )
        d.line(
            (int(canvas * 0.34) + x_off, int(canvas * 0.32), int(canvas * 0.48) + x_off, int(canvas * 0.50)),
            fill=color_rgba, width=stroke
        )
        d.line(
            (int(canvas * 0.34) + x_off, int(canvas * 0.68), int(canvas * 0.48) + x_off, int(canvas * 0.50)),
            fill=color_rgba, width=stroke
        )
        d.line(
            (int(canvas * 0.48) + x_off, int(canvas * 0.50), int(canvas * 0.88) + x_off, int(canvas * 0.20)),
            fill=color_rgba, width=stroke
        )
        d.line(
            (int(canvas * 0.48) + x_off, int(canvas * 0.50), int(canvas * 0.88) + x_off, int(canvas * 0.80)),
            fill=color_rgba, width=stroke
        )
        d.ellipse(
            (int(canvas * 0.43) + x_off, int(canvas * 0.45), int(canvas * 0.53) + x_off, int(canvas * 0.55)),
            fill=color_rgba
        )

    return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))

# ── App ─────────────────────────────────────────────────────────────────────

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PodcastClean")
        self.configure(fg_color=DARK_BG)
        self.resizable(True, True)

        # Size window to fit content, centred on screen
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w = 640
        h = min(sh - 80, 920)
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(580, 780)

        self.audio_path = None
        self.mode_var   = tk.StringVar(value="bleep")
        self.model_var  = tk.StringVar(value="base")
        self.processing = False
        self.custom_words = []

        self._build()
        threading.Thread(target=self._check_deps, daemon=True).start()

    # ── Build UI ────────────────────────────────────────────────────────────

    def _build(self):
        # Simple frame — no scrolling needed
        s = ctk.CTkFrame(self, fg_color=DARK_BG)
        s.pack(fill="both", expand=True)

        # Header
        hdr = ctk.CTkFrame(s, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(28, 0))

        ctk.CTkLabel(hdr, text="  🔇 PODCASTCLEAN  ",
                     font=ctk.CTkFont("Helvetica", 15, "bold"),
                     text_color=ACCENT, fg_color=CARD_BG,
                     corner_radius=4).pack(anchor="w")

        ctk.CTkLabel(hdr, text="Auto Bleep",
                     font=ctk.CTkFont("Helvetica", 42, "bold"),
                     text_color=TEXT).pack(anchor="w", pady=(6, 0))

        # Drop zone
        self.drop_card = ctk.CTkFrame(
            s, fg_color=CARD_BG, corner_radius=10,
            border_width=2, border_color=BORDER)
        self.drop_card.pack(fill="x", padx=28, pady=(14, 0))

        drop_inner = ctk.CTkFrame(self.drop_card, fg_color="transparent")
        drop_inner.pack(fill="x", padx=16, pady=12)
        drop_inner.grid_columnconfigure(1, weight=1)

        self.drop_emoji = ctk.CTkLabel(drop_inner, text="🎙️",
            font=ctk.CTkFont("Helvetica", 22))
        self.drop_emoji.grid(row=0, column=0, padx=(0, 10))

        self.drop_title = ctk.CTkLabel(drop_inner,
            text="Click or drag & drop a podcast file",
            font=ctk.CTkFont("Helvetica", 13, "bold"), text_color=TEXT, anchor="w")
        self.drop_title.grid(row=0, column=1, sticky="ew")

        self.drop_hint = ctk.CTkLabel(drop_inner,
            text="MP3 · M4A · WAV · OGG · FLAC",
            font=ctk.CTkFont("Helvetica", 11), text_color=MUTED, anchor="w")
        self.drop_hint.grid(row=1, column=1, sticky="ew")

        for w in [self.drop_card, drop_inner, self.drop_emoji, self.drop_title, self.drop_hint]:
            w.bind("<Button-1>", lambda e: self._choose_file())
            w.configure(cursor="hand2")

        # Drag and drop support
        self._register_drop(self.drop_card)
        self._register_drop(drop_inner)
        self._register_drop(self.drop_title)
        self._register_drop(self.drop_hint)

        # Options
        opts = ctk.CTkFrame(s, fg_color=CARD_BG, corner_radius=14)
        opts.pack(fill="x", padx=28, pady=(10, 0))
        opts.grid_columnconfigure(0, weight=1)

        # — Mode —
        self._section(opts, "CENSORING MODE", row=0)
        mr = ctk.CTkFrame(opts, fg_color="transparent")
        mr.grid(row=1, column=0, sticky="ew", padx=16, pady=(8, 0))
        mr.grid_columnconfigure((0, 1, 2), weight=1)

        # Pre-load crisp icons in active (white) + inactive (dark) tints.
        icon_size = 24
        self._ico_bleep_w = _mode_icon("bleep", (255, 255, 255), size=icon_size)
        self._ico_mute_w  = _mode_icon("mute",  (255, 255, 255), size=icon_size)
        self._ico_cut_w   = _mode_icon("cut",   (255, 255, 255), size=icon_size)
        self._ico_bleep_d = _mode_icon("bleep", TEXT_RGB, size=icon_size)
        self._ico_mute_d  = _mode_icon("mute",  TEXT_RGB, size=icon_size)
        self._ico_cut_d   = _mode_icon("cut",   TEXT_RGB, size=icon_size)

        def _mode_btn(parent, ico_w, ico_d, label, mode, active=False):
            fg   = ACCENT   if active else CARD2_BG
            hov  = ACCENT_H if active else CARD2_H
            tcol = WHITE    if active else TEXT
            ico_img = ico_w if active else ico_d
            return ctk.CTkButton(
                parent, text=label, image=ico_img, compound="left",
                font=ctk.CTkFont("Helvetica", 15, "bold"),
                fg_color=fg, hover_color=hov, text_color=tcol,
                corner_radius=6, height=46, border_spacing=10, anchor="center",
                command=lambda m=mode: self._set_mode(m))

        self.btn_bleep = _mode_btn(
            mr, self._ico_bleep_w, self._ico_bleep_d, "Bleep Sound", "bleep", active=True)
        self.btn_bleep.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.btn_mute = _mode_btn(
            mr, self._ico_mute_w, self._ico_mute_d, "Mute / Silence", "mute")
        self.btn_mute.grid(row=0, column=1, sticky="ew", padx=(0, 6))

        self.btn_cut = _mode_btn(
            mr, self._ico_cut_w, self._ico_cut_d, "Cut Out", "cut")
        self.btn_cut.grid(row=0, column=2, sticky="ew")

        # — Model —
        self._section(opts, "WHISPER MODEL", row=2, top=18)
        mdl = ctk.CTkFrame(opts, fg_color="transparent")
        mdl.grid(row=3, column=0, sticky="ew", padx=16, pady=(8, 0))
        mdl.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.model_btns = {}
        for i, (lbl, val) in enumerate([("Tiny", "tiny"), ("Base ✓", "base"),
                                         ("Small", "small"), ("Medium", "medium")]):
            active = val == "base"
            b = ctk.CTkButton(
                mdl, text=lbl,
                font=ctk.CTkFont("Helvetica", 15, "bold"),
                fg_color=ACCENT if active else CARD2_BG,
                hover_color=ACCENT_H if active else CARD2_H,
                text_color=WHITE if active else TEXT,
                corner_radius=6, height=46,
                command=lambda v=val: self._set_model(v))
            b.grid(row=0, column=i, sticky="ew", padx=(0, 6) if i < 3 else 0)
            self.model_btns[val] = b

        # — Religious filter toggle —
        rel_frame = ctk.CTkFrame(opts, fg_color="transparent")
        rel_frame.grid(row=4, column=0, sticky="ew", padx=16, pady=(14, 0))

        self.religious_var = ctk.BooleanVar(value=True)
        self.religious_switch = ctk.CTkSwitch(
            rel_frame, text="Filter religious words",
            font=ctk.CTkFont("Helvetica", 13),
            text_color=TEXT, fg_color=CARD2_BG,
            progress_color=ACCENT, button_color=ACCENT,
            button_hover_color=ACCENT_H,
            variable=self.religious_var)
        self.religious_switch.pack(anchor="w")

        # — Custom words —
        self._section(opts, "EXTRA WORDS TO BLEEP", row=5, top=18)
        wr = ctk.CTkFrame(opts, fg_color="transparent")
        wr.grid(row=6, column=0, sticky="ew", padx=16, pady=(8, 0))
        wr.grid_columnconfigure(0, weight=1)

        self.word_entry = ctk.CTkEntry(
            wr, placeholder_text="Type a word and press Add...",
            font=ctk.CTkFont("Helvetica", 13),
            fg_color=INPUT_BG, border_color=BORDER,
            text_color=TEXT, height=38, corner_radius=6)
        self.word_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.word_entry.bind("<Return>", lambda e: self._add_word())

        ctk.CTkButton(wr, text="+ Add", width=72, height=38,
                      font=ctk.CTkFont("Helvetica", 12, "bold"),
                      fg_color=CARD2_BG, hover_color=CARD2_H,
                      text_color=TEXT, corner_radius=6,
                      command=self._add_word
                      ).grid(row=0, column=1)

        self.words_label = ctk.CTkLabel(opts, text="",
                                        font=ctk.CTkFont("Courier", 10),
                                        text_color=ACCENT,
                                        wraplength=520, justify="left")
        self.words_label.grid(row=7, column=0, sticky="w", padx=16, pady=(6, 16))

        # Export filename
        export_frame = ctk.CTkFrame(s, fg_color="transparent")
        export_frame.pack(fill="x", padx=28, pady=(14, 0))

        self._section_label(export_frame, "OUTPUT FILENAME")
        
        fn_row = ctk.CTkFrame(export_frame, fg_color="transparent")
        fn_row.pack(fill="x", pady=(6, 0))
        fn_row.grid_columnconfigure(0, weight=1)

        self.filename_entry = ctk.CTkEntry(
            fn_row,
            placeholder_text="Output filename (e.g. clean-ep42.mp3)",
            font=ctk.CTkFont("Helvetica", 13),
            fg_color=INPUT_BG, border_color=BORDER,
            text_color=TEXT, height=40, corner_radius=6)
        self.filename_entry.pack(fill="x")

        # Process button
        self.process_btn = ctk.CTkButton(
            s, text="🔇   PROCESS & SAVE",
            font=ctk.CTkFont("Helvetica", 16, "bold"),
            fg_color=ACCENT, hover_color=ACCENT_H,
            text_color=WHITE, text_color_disabled=WHITE, corner_radius=10, height=62,
            state="disabled", command=self._start)
        self.process_btn.pack(fill="x", padx=28, pady=(18, 0))

        # Progress
        pf = ctk.CTkFrame(s, fg_color="transparent")
        pf.pack(fill="x", padx=28, pady=(10, 0))

        self.status_lbl = ctk.CTkLabel(
            pf, text="Ready — choose a podcast file to get started",
            font=ctk.CTkFont("Helvetica", 13),
            text_color=MUTED, anchor="w")
        self.status_lbl.pack(fill="x")

        self.pbar = ctk.CTkProgressBar(pf, height=6, corner_radius=3,
                                        fg_color=CARD2_BG, progress_color=ACCENT)
        self.pbar.pack(fill="x", pady=(8, 0))
        self.pbar.set(0)

        # Log
        self.log_box = ctk.CTkTextbox(
            s, font=ctk.CTkFont("Helvetica", 12),
            fg_color=LOG_BG, text_color=LOG_TEXT,
            corner_radius=10, border_width=0,
            height=115, wrap="word")
        self.log_box.pack(fill="x", padx=28, pady=(10, 16))
        self.log_box.configure(state="disabled")

    def _section_label(self, parent, text):
        ctk.CTkLabel(parent, text=text,
                     font=ctk.CTkFont("Helvetica", 12, "bold"),
                     text_color=MUTED, anchor="w").pack(anchor="w")

    def _section(self, parent, text, row, top=0):
        ctk.CTkLabel(parent, text=text,
                     font=ctk.CTkFont("Helvetica", 12, "bold"),
                     text_color=MUTED, anchor="w"
                     ).grid(row=row, column=0, sticky="ew", padx=16, pady=(top, 4))

    # ── Interactions ────────────────────────────────────────────────────────

    def _set_mode(self, mode):
        self.mode_var.set(mode)
        combos = [
            (self.btn_bleep, self._ico_bleep_w, self._ico_bleep_d, "bleep"),
            (self.btn_mute,  self._ico_mute_w,  self._ico_mute_d,  "mute"),
            (self.btn_cut,   self._ico_cut_w,   self._ico_cut_d,   "cut"),
        ]
        for btn, ico_w, ico_d, val in combos:
            if val == mode:
                btn.configure(fg_color=ACCENT, hover_color=ACCENT_H,
                              text_color=WHITE, image=ico_w)
            else:
                btn.configure(fg_color=CARD2_BG, hover_color=CARD2_H,
                              text_color=TEXT, image=ico_d)

    def _set_model(self, val):
        self.model_var.set(val)
        for v, b in self.model_btns.items():
            if v == val:
                b.configure(fg_color=ACCENT, hover_color=ACCENT_H, text_color=WHITE)
            else:
                b.configure(fg_color=CARD2_BG, hover_color=CARD2_H, text_color=TEXT)

    def _register_drop(self, widget):
        """Register drag and drop on a widget using tkinter DnD."""
        try:
            widget.drop_target_register('*')
            widget.dnd_bind('<<Drop>>', self._on_drop)
            widget.dnd_bind('<<DragEnter>>', lambda e: self.drop_card.configure(border_color=ACCENT))
            widget.dnd_bind('<<DragLeave>>', lambda e: self.drop_card.configure(border_color=BORDER))
        except Exception:
            pass  # tkinterdnd2 not installed, drag+drop silently disabled

    def _on_drop(self, event):
        self.drop_card.configure(border_color=BORDER)
        path = event.data.strip().strip('{}')  # Windows wraps paths in {}
        if os.path.isfile(path):
            self._set_file(path)

    def _choose_file(self):
        path = filedialog.askopenfilename(
            title="Choose podcast",
            filetypes=[("Audio", "*.mp3 *.m4a *.wav *.ogg *.flac *.aac"), ("All", "*.*")])
        if path:
            self._set_file(path)

    def _set_file(self, path):
        self.audio_path = path
        name = os.path.basename(path)
        size = os.path.getsize(path) / 1024 / 1024
        self.drop_emoji.configure(text="✅")
        self.drop_title.configure(text=name, text_color=TEXT)
        self.drop_hint.configure(text=f"{size:.1f} MB · ready to process")
        self.drop_card.configure(border_color=GREEN)
        self.process_btn.configure(state="normal")
        # Pre-fill output filename based on input
        base, _ = os.path.splitext(name)
        self.filename_entry.delete(0, "end")
        self.filename_entry.insert(0, base + "-clean.mp3")
        self._log(f"Loaded: {name}")

    def _add_word(self):
        w = self.word_entry.get().strip().lower()
        if w and len(w) >= 2 and w not in self.custom_words:
            self.custom_words.append(w)
            self.word_entry.delete(0, "end")
            self.words_label.configure(text="Extra: " + "  ·  ".join(self.custom_words))

    def _log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _status(self, txt, color=None):
        self.status_lbl.configure(text=txt, text_color=color or MUTED)

    def _progress(self, v):
        self.pbar.set(min(v, 1.0))
        if v >= 1.0:
            self.pbar.configure(progress_color=GREEN)

    # ── Processing ──────────────────────────────────────────────────────────

    def _start(self):
        if self.processing or not self.audio_path: return
        self.processing = True
        self.pbar.configure(progress_color=ACCENT)
        self.process_btn.configure(state="disabled", text="⏳  Processing...")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            self._process()
        except Exception as e:
            self.after(0, self._log, f"❌ Error: {e}")
            self.after(0, self._status, f"❌ {e}", ERROR)
        finally:
            self.processing = False
            self.after(0, self.process_btn.configure,
                       {"state": "normal", "text": "🔇   PROCESS & SAVE"})

    def _process(self):
        import numpy as np
        from pydub import AudioSegment
        import whisper

        self.after(0, self._status, "Loading audio...")
        self.after(0, self._progress, 0.05)
        self.after(0, self._log, f"▶ Loading audio...")

        audio = AudioSegment.from_file(self.audio_path)
        dur = len(audio) / 1000
        self.after(0, self._log, f"  {int(dur//60)}m {int(dur%60)}s · {audio.channels}ch · {audio.frame_rate}Hz")

        # Write temp WAV for Whisper
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False, mode="wb")
        audio.set_channels(1).set_frame_rate(16000).export(tmp.name, format="wav")
        tmp.close()

        # Load Whisper model
        self.after(0, self._status, f"Loading Whisper model '{self.model_var.get()}'...")
        self.after(0, self._progress, 0.15)
        self.after(0, self._log, f"▶ Loading Whisper '{self.model_var.get()}' model...")
        model = whisper.load_model(self.model_var.get())

        # Transcribe
        self.after(0, self._status, "Transcribing audio... ☕ grab a coffee")
        self.after(0, self._progress, 0.25)
        self.after(0, self._log, "▶ Transcribing (this takes a while)...")

        result = model.transcribe(tmp.name, word_timestamps=True, verbose=False)
        self._last_result = result
        try: os.unlink(tmp.name)
        except: pass

        self.after(0, self._progress, 0.65)
        self.after(0, self._log, f"  ✓ Done — {len(result['segments'])} segments")

        # Find curse words - comprehensive detection
        self.after(0, self._status, "Scanning for curse words...")
        word_list = CURSE_WORDS + (RELIGIOUS_WORDS if self.religious_var.get() else [])
        bad = set(word_list + self.custom_words)
        ranges, found = [], []

        def is_bad(word_str):
            clean = "".join(c for c in word_str.lower() if c.isalpha())
            if not clean:
                return False
            for b in bad:
                # Exact, starts-with, or partial match at segment boundary
                if clean == b or clean.startswith(b):
                    return True
            return False

        for seg in result.get("segments", []):
            for wi in seg.get("words", []):
                if is_bad(wi.get("word", "")):
                    # Extra padding to make sure full word is covered
                    s = max(0, wi["start"] - 0.1)
                    e = wi["end"] + 0.1
                    found.append((wi["word"].strip(), s, e))
                    # Merge ranges within 0.3s of each other
                    if ranges and s <= ranges[-1][1] + 0.3:
                        ranges[-1] = (ranges[-1][0], max(ranges[-1][1], e))
                    else:
                        ranges.append((s, e))

        self.after(0, self._log, f"▶ {len(found)} word(s) found")
        for word, s, e in found:
            self.after(0, self._log, f"  [{s:.1f}s – {e:.1f}s]  \"{obfuscate_word(word)}\"")

        # Apply effect
        mode = self.mode_var.get()
        self.after(0, self._status, f"Applying {mode} effect...")
        self.after(0, self._progress, 0.80)

        sr, ch = audio.frame_rate, audio.channels

        if mode == "cut":
            # Build list of kept segments and concatenate
            self.after(0, self._log, f"▶ Cutting out {len(ranges)} segment(s)...")
            from pydub import AudioSegment as AS
            kept = []
            prev_end_ms = 0
            for s0s, e0s in sorted(ranges):
                s0_ms = int(s0s * 1000)
                e0_ms = int(e0s * 1000)
                if prev_end_ms < s0_ms:
                    kept.append(audio[prev_end_ms:s0_ms])
                prev_end_ms = e0_ms
            # Add remainder after last cut
            if prev_end_ms < len(audio):
                kept.append(audio[prev_end_ms:])
            out_audio = kept[0]
            for seg in kept[1:]:
                out_audio = out_audio + seg
            orig_dur = len(audio) / 1000
            new_dur = len(out_audio) / 1000
            saved = orig_dur - new_dur
            self.after(0, self._log, f"  ✓ Cut {saved:.1f}s of audio — {int(new_dur//60)}m {int(new_dur%60)}s remaining")
        else:
            samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
            if ch == 2: samples = samples.reshape((-1, 2))

            for s0s, e0s in ranges:
                s0 = int(s0s * sr)
                s1 = min(len(samples), int(e0s * sr))
                d  = s1 - s0
                if mode == "mute":
                    fade = min(200, d // 10)
                    for i in range(d):
                        idx = s0 + i
                        if idx >= len(samples): break
                        v = 0.02
                        if i < fade: v = (1 - i/fade) * 0.02
                        elif i > d - fade: v = ((d-i)/fade) * 0.02
                        samples[idx] = samples[idx] * v
                else:
                    ds = d / sr
                    for i in range(d):
                        idx = s0 + i
                        if idx >= len(samples): break
                        t = i / sr
                        t = i / sr
                        # Raised-cosine envelope — completely smooth, no clicks
                        env = 0.5 * (1 - math.cos(2 * math.pi * t / ds)) if ds > 0 else 0
                        b = math.sin(2 * math.pi * 440 * t) * 0.15 * env * 32767
                        samples[idx] = [b, b] if ch == 2 else b

            import array as arr
            raw = arr.array("h", np.clip(samples, -32768, 32767).astype(np.int16).flatten().tolist())
            out_audio = audio._spawn(raw.tobytes())

        # Save
        self.after(0, self._status, "Saving...")
        self.after(0, self._progress, 0.93)

        custom_name = self.filename_entry.get().strip()
        base_path, _ = os.path.splitext(self.audio_path)
        if custom_name:
            if not custom_name.lower().endswith(".mp3"):
                custom_name += ".mp3"
            out_path = os.path.join(os.path.dirname(self.audio_path), custom_name)
        else:
            out_path = base_path + "-clean.mp3"
        # Match original file bitrate
        try:
            from mutagen.mp3 import MP3
            orig_bitrate = int(MP3(self.audio_path).info.bitrate / 1000)
            orig_bitrate = max(64, min(320, orig_bitrate))  # clamp to sane range
            bitrate = f"{orig_bitrate}k"
        except Exception:
            bitrate = "128k"  # safe fallback
        out_audio.export(out_path, format="mp3", bitrate=bitrate)
        self.after(0, self._log, f"  Exported at {bitrate}")

        # Generate report
        base_path, _ = os.path.splitext(self.audio_path)
        report_path = base_path + "-report.txt"
        self._write_report(report_path, found, ranges, mode, dur, out_path)

        self.after(0, self._progress, 1.0)
        self.after(0, self._status, f"✅ Done! {len(found)} word(s) censored", GREEN)
        self.after(0, self._log, f"✅ Saved: {out_path}")
        self.after(0, self._log, f"📄 Report: {report_path}")
        self.after(500, lambda: self._done(out_path, report_path, len(found), mode))

    def _write_report(self, report_path, found, ranges, mode, orig_dur, out_path):
        mode_label = {"bleep": "Bleep Sound", "mute": "Mute / Silence", "cut": "Cut Out"}[mode]
        lines = []
        lines.append("=" * 60)
        lines.append("  PODCASTCLEAN — CENSOR REPORT")
        lines.append("=" * 60)
        lines.append(f"  Input file : {os.path.basename(self.audio_path)}")
        lines.append(f"  Output file: {os.path.basename(out_path)}")
        lines.append(f"  Mode       : {mode_label}")
        lines.append(f"  Duration   : {int(orig_dur//60)}m {int(orig_dur%60)}s")
        lines.append(f"  Words found: {len(found)}")
        lines.append("=" * 60)
        lines.append("")

        if not found:
            lines.append("  ✅ No curse words detected.")
        else:
            lines.append("  CENSORED WORDS:")
            lines.append("")
            for i, (word, start, end) in enumerate(found, 1):
                mm_s = int(start // 60)
                ss_s = int(start % 60)
                mm_e = int(end // 60)
                ss_e = int(end % 60)
                safe_word = obfuscate_word(word)
                lines.append(f'  {i:>3}.  [{mm_s:02d}:{ss_s:02d} - {mm_e:02d}:{ss_e:02d}]  "{safe_word}"')

            lines.append("")
            lines.append("=" * 60)
            lines.append("  FULL TRANSCRIPT:")
            lines.append("=" * 60)
            lines.append("")

            # Write full transcript with censored words marked
            try:
                import whisper
                # Re-use already loaded result stored on self if available
                result = getattr(self, '_last_result', None)
                if result:
                    word_list = CURSE_WORDS + (RELIGIOUS_WORDS if self.religious_var.get() else [])
                    bad = set(word_list + self.custom_words)
                    for seg in result.get("segments", []):
                        ts = seg.get("start", 0)
                        mm = int(ts // 60)
                        ss = int(ts % 60)
                        text = seg.get("text", "").strip()
                        # Mark bad words in transcript
                        words_in_seg = text.split()
                        marked = []
                        for w in words_in_seg:
                            clean = "".join(c for c in w.lower() if c.isalpha())
                            is_bad = any(clean == b or clean.startswith(b) for b in bad)
                            masked = obfuscate_word(w).upper()
                            marked.append(f"[{masked}]" if is_bad else w)
                        lines.append(f"  [{mm:02d}:{ss:02d}]  {' '.join(marked)}")
                    lines.append("")
            except Exception:
                pass

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _done(self, out_path, report_path, count, mode):
        extra = "\nSwear-free and shorter! ✂️" if mode == "cut" else ""
        if messagebox.askyesno("✅ Done!", f"Clean file saved!\n\n{os.path.basename(out_path)}\n\n{count} word(s) censored.{extra}\n\nA report was saved next to the audio file.\n\nOpen folder?"):
            import subprocess
            subprocess.Popen(["explorer", "/select,", os.path.normpath(out_path)])

    def _check_deps(self):
        missing = []
        for pkg, name in [("whisper","openai-whisper"), ("numpy","numpy"), ("pydub","pydub")]:
            try: __import__(pkg)
            except: missing.append(name)
        if missing:
            self.after(0, messagebox.showerror, "Missing packages",
                       "Run:\n  py -3.11 -m pip install " + " ".join(missing))
        else:
            self.after(0, self._log, "✓ All packages ready")
            self.after(0, self._log, "✓ Click the drop zone above to load a podcast")


if __name__ == "__main__":
    app = App()
    app.mainloop()
