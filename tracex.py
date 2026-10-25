"""TraceX — Digital Forensics Workstation (Final Edition 1.0)

Local-first Tkinter application. Uses only Python's standard library.
Features: SHA-256 file integrity, hash comparison, URL pattern inspection,
password composition checks, SQLite evidence cases, and JSON evidence reports.

Important: This is an educational triage tool, not a malware scanner or a
certified forensic suite. File metadata and URL heuristics are best-effort.
"""
import tkinter as tk
from tkinter import filedialog, messagebox
from urllib.parse import urlparse
from datetime import datetime
import hashlib
import re
import os
import sqlite3
import json
import mimetypes
from tkinter import simpledialog

# =====================================================
# TRACEX | DIGITAL FORENSICS WORKSTATION — FINAL EDITION
# Release: 1.0 | Theme: PHANTOM SIGNAL
# =====================================================

root = tk.Tk()
root.title("TraceX | Digital Forensics")
root.geometry("1250x780")
root.minsize(1000, 650)
root.configure(bg="#090C10")

# ---------------- COLOUR PALETTE: "EMBER INK" ----------------
# Orange = active controls, blue = information, mint = success,
# gold = warnings, red = dangerous findings.

BG = "#0A0C10"        # Ink Black
PANEL = "#11151C"     # Carbon
PANEL2 = "#1B2130"    # Slate
BORDER = "#2B3345"    # Steel line
ACCENT = "#FF7A3D"    # Ember Orange  (primary / active)
INFO = "#6CC8FF"      # Ice Blue      (information)
OK = "#4ADE9A"        # Mint          (match / success)
WARN = "#FFD166"      # Gold          (review recommended)
DANGER = "#FF4D6D"    # Signal Red    (dangerous / mismatch)
TEXT = "#F2F5F9"      # Frost White
MUTED = "#8B95A7"     # Fog Grey

# ---------------- FONTS ----------------
# The first installed font in each list is used, so the app still
# runs on any computer.
import tkinter.font as tkfont

_installed = set(tkfont.families(root))


def pick_font(candidates, fallback):
    for name in candidates:
        if name in _installed:
            return name
    return fallback


# Headings: Algerian (decorative capitals, installed with Microsoft Office).
FONT_HEAD = pick_font(
    ["Algerian", "Copperplate Gothic Bold", "Times New Roman"],
    tkfont.nametofont("TkDefaultFont").actual("family")
)
# Normal text, buttons, inputs and reports: Times New Roman.
FONT_BODY = pick_font(
    ["Times New Roman", "Liberation Serif", "Georgia"],
    tkfont.nametofont("TkDefaultFont").actual("family")
)


def head(size, bold=False):
    return (FONT_HEAD, size, "bold" if bold else "normal")


def txt(size, bold=False):
    # Times New Roman looks small at the same point size, so add 1.
    return (FONT_BODY, size + 1, "bold" if bold else "normal")


# Input boxes: thin steel border that turns orange when focused.
for _widget in ("Entry", "Text", "Listbox"):
    root.option_add(f"*{_widget}.highlightThickness", 1)
    root.option_add(f"*{_widget}.highlightBackground", BORDER)
    root.option_add(f"*{_widget}.highlightColor", ACCENT)


# ---------------- APPLICATION DATA ----------------

events = []
file_checks = 0
url_checks = 0
findings = 0
current_page = "Overview"
selected_case_id = None

# Case records persist between app launches in this local SQLite database.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tracex_cases.db")

def initialize_database():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )""")
        connection.execute("""CREATE TABLE IF NOT EXISTS case_findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            finding TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(case_id) REFERENCES cases(id)
        )""")

initialize_database()

# ---------------- HELPER FUNCTIONS ----------------

def make_label(parent, text, size=10, color=TEXT, bold=False, bg=None):
    return tk.Label(
        parent,
        text=text,
        font=head(size, bold) if (bold and size >= 11) else txt(size, bold),
        fg=color,
        bg=bg if bg else PANEL,
        anchor="w"
    )


def make_button(parent, text, command, bg=ACCENT, fg=BG):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=INFO,
        activeforeground=BG,
        relief="flat",
        bd=0,
        highlightthickness=0,
        padx=14,
        pady=10,
        font=txt(10, True),
        cursor="hand2"
    )


def panel(parent, padx=16, pady=16):
    return tk.Frame(
        parent,
        bg=PANEL,
        highlightbackground=BORDER,
        highlightthickness=1,
        padx=padx,
        pady=pady
    )


def clear_content():
    for widget in content.winfo_children():
        widget.destroy()


def clear_root_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


# ---------------- HEADER ----------------

header = tk.Frame(root, bg=BG, height=65)
header.pack(fill="x", padx=24, pady=(15, 8))
header.pack_propagate(False)

brand = tk.Frame(header, bg=BG)
brand.pack(side="left", fill="y")

make_label(brand, "TRACEX", 20, ACCENT, True, BG).pack(side="left")
make_label(
    brand, "  /  DIGITAL FORENSICS", 10, MUTED, True, BG
).pack(side="left", pady=8)

header_right = tk.Frame(header, bg=BG)
header_right.pack(side="right", fill="y")

status_label = make_label(
    header_right, "● LOCAL WORKSTATION", 10, ACCENT, True, BG
)
status_label.pack(side="right", padx=(18, 0), pady=10)

clock_label = make_label(header_right, "", 10, INFO, False, BG)
clock_label.pack(side="right", pady=10)


def update_clock():
    clock_label.config(
        text=datetime.now().strftime("%d %b %Y  |  %H:%M:%S")
    )
    root.after(1000, update_clock)


# ---------------- MAIN LAYOUT ----------------

body = tk.Frame(root, bg=BG)
body.pack(fill="both", expand=True, padx=24, pady=(5, 20))

sidebar = tk.Frame(
    body, bg=PANEL, width=205,
    highlightbackground=BORDER, highlightthickness=1
)
sidebar.pack(side="left", fill="y", padx=(0, 16))
sidebar.pack_propagate(False)

make_label(sidebar, "WORKSPACES", 9, MUTED, True).pack(
    anchor="w", padx=16, pady=(24, 15)
)

content = tk.Frame(body, bg=BG)
content.pack(side="left", fill="both", expand=True)


# ---------------- ACTIVITY FEED ----------------

def refresh_activity():
    if current_page != "Overview":
        return
    if not hasattr(root, "activity_frame"):
        return

    try:
        if not root.activity_frame.winfo_exists():
            return
        clear_root_frame(root.activity_frame)
    except tk.TclError:
        return

    if not events:
        make_label(
            root.activity_frame, "No activity recorded yet.",
            10, MUTED
        ).pack(anchor="w", pady=6)
        return

    for time_text, text, color in events[:7]:
        row = tk.Frame(root.activity_frame, bg=PANEL)
        row.pack(fill="x", pady=4)

        make_label(row, time_text, 9, MUTED).pack(
            side="left", padx=(0, 12)
        )
        make_label(row, "●", 9, color).pack(
            side="left", padx=(0, 9)
        )
        make_label(row, text, 9, TEXT).pack(
            side="left", fill="x", expand=True
        )


def update_dashboard_stats():
    """Refresh overview counters when the dashboard is visible."""
    if not hasattr(root, "stat_value_labels"):
        return
    values = {"FILE CHECKS": file_checks, "URL CHECKS": url_checks,
              "REVIEW FLAGS": findings}
    for title, label in root.stat_value_labels.items():
        try:
            if label.winfo_exists():
                label.config(text=str(values.get(title, 0)))
        except tk.TclError:
            pass  # label belongs to an Overview page that was replaced


def log_event(text, color=INFO):
    events.insert(
        0,
        (datetime.now().strftime("%H:%M:%S"), text, color)
    )
    del events[30:]
    refresh_activity()
    update_dashboard_stats()


# ---------------- FILE INTEGRITY TOOL ----------------

def calculate_sha256(path):
    """Calculate a file's SHA-256 fingerprint."""
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_file():
    global file_checks

    path = filedialog.askopenfilename(
        title="Select a file for integrity analysis"
    )
    if not path:
        return

    try:
        digest = calculate_sha256(path)
        size = os.path.getsize(path)
        file_checks += 1
        update_dashboard_stats()

        result = (
            f"FILE: {os.path.basename(path)}\n\n"
            f"SIZE: {size:,} bytes\n\n"
            f"SHA-256:\n{digest}\n\n"
            "STATUS: HASH GENERATED\n\n"
            "Save this hash and compare it with a later hash "
            "of the same file to detect changes."
        )
        messagebox.showinfo("File Integrity Result", result)
        log_event(f"SHA-256 generated: {os.path.basename(path)}", ACCENT)

    except OSError as error:
        messagebox.showerror(
            "File Error", f"Could not read the selected file:\n{error}"
        )


def show_file_page():
    clear_content()

    make_label(
        content, "01  /  FILE INTEGRITY", 19, ACCENT, True, BG
    ).pack(anchor="w", pady=(8, 5))
    make_label(
        content,
        "Generate a cryptographic fingerprint for a local file.",
        10, MUTED, False, BG
    ).pack(anchor="w", pady=(0, 20))

    box = panel(content, 24, 24)
    box.pack(fill="x", pady=(0, 16))

    make_label(box, "EVIDENCE ACQUISITION", 11, INFO, True).pack(
        anchor="w"
    )
    make_label(
        box, "Select a file. TraceX will calculate its SHA-256 hash.",
        10, MUTED
    ).pack(anchor="w", pady=(12, 18))
    make_button(box, "SELECT FILE  →", inspect_file).pack(anchor="w")

    note = panel(content, 18, 18)
    note.pack(fill="x")
    make_label(note, "ANALYST NOTE", 10, WARN, True).pack(anchor="w")
    make_label(
        note,
        "A hash identifies file contents, but a hash alone does not "
        "prove a file is safe or malicious.",
        10, TEXT
    ).pack(anchor="w", pady=(10, 0))


# ---------------- PROFESSIONAL EVIDENCE ANALYSIS ----------------

def detect_file_type(path):
    """Identify common formats from file signatures; extension alone is not trusted."""
    with open(path, "rb") as file:
        header = file.read(32)

    signatures = [
        (b"%PDF-", "PDF document"),
        (b"\x89PNG\r\n\x1a\n", "PNG image"),
        (b"\xff\xd8\xff", "JPEG image"),
        (b"GIF87a", "GIF image"),
        (b"GIF89a", "GIF image"),
        (b"PK\x03\x04", "ZIP archive / Office Open XML / other ZIP-based file"),
        (b"\x7fELF", "ELF executable or shared object"),
        (b"MZ", "Windows PE executable or DOS-compatible executable"),
        (b"ID3", "MP3 audio (ID3-tagged)"),
        (b"OggS", "Ogg media container"),
        (b"RIFF", "RIFF container (e.g. WAV or AVI)"),
    ]
    for signature, label in signatures:
        if header.startswith(signature):
            return label
    if header.startswith(b"\x1f\x8b"):
        return "GZIP compressed file"
    if header.startswith(b"BZh"):
        return "BZIP2 compressed file"
    if header.startswith(b"7z\xbc\xaf\x27\x1c"):
        return "7-Zip archive"
    if header.startswith(b"Rar!\x1a\x07"):
        return "RAR archive"
    return "Unknown / text / unrecognized signature"


def collect_file_metadata(path):
    """Collect local filesystem metadata and a SHA-256 digest for a selected file."""
    stat = os.stat(path)
    guessed_mime, _ = mimetypes.guess_type(path)
    return {
        "file_name": os.path.basename(path),
        "full_path": os.path.abspath(path),
        "extension": os.path.splitext(path)[1].lower() or "(none)",
        "size_bytes": stat.st_size,
        "size_kb": round(stat.st_size / 1024, 3),
        "created_or_metadata_time": datetime.fromtimestamp(stat.st_ctime).isoformat(sep=" ", timespec="seconds"),
        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(sep=" ", timespec="seconds"),
        "last_accessed": datetime.fromtimestamp(stat.st_atime).isoformat(sep=" ", timespec="seconds"),
        "mime_type_guess_from_extension": guessed_mime or "Unknown",
        "detected_signature_type": detect_file_type(path),
        "sha256": calculate_sha256(path),
        "analysis_time": datetime.now().isoformat(sep=" ", timespec="seconds"),
    }


def show_evidence_analysis_page():
    clear_content()
    make_label(content, "05  /  PROFESSIONAL EVIDENCE ANALYSIS", 19, ACCENT, True, BG).pack(anchor="w", pady=(8, 5))
    make_label(content, "Inspect local file metadata, identify common signatures, verify SHA-256, and export JSON.", 10, MUTED, False, BG).pack(anchor="w", pady=(0, 18))

    select_box = panel(content, 18, 18)
    select_box.pack(fill="x", pady=(0, 12))
    make_label(select_box, "SELECT EVIDENCE FILE", 10, INFO, True).pack(anchor="w", pady=(0, 10))
    selected_path = tk.StringVar()
    path_entry = tk.Entry(select_box, textvariable=selected_path, state="readonly", bg=BG, fg=TEXT, readonlybackground=BG, relief="flat", font=txt(9))
    path_entry.pack(fill="x", pady=(0, 10))

    output_box = panel(content, 16, 16)
    output_box.pack(fill="both", expand=True)
    make_label(output_box, "ANALYSIS REPORT", 10, INFO, True).pack(anchor="w", pady=(0, 8))
    report_text = tk.Text(output_box, bg=BG, fg=TEXT, insertbackground=ACCENT, font=txt(9), wrap="word", relief="flat", padx=12, pady=12, height=15)
    report_text.pack(fill="both", expand=True)
    report_text.insert("1.0", "Select a file to view its metadata and SHA-256 fingerprint.\n\nSignature detection supports common formats and is not a malware scan.")

    expected_hash = tk.StringVar()
    verify_row = tk.Frame(output_box, bg=PANEL)
    verify_row.pack(fill="x", pady=(12, 0))
    make_label(verify_row, "EXPECTED SHA-256:", 9, WARN, True).pack(side="left", padx=(0, 8))
    hash_entry = tk.Entry(verify_row, textvariable=expected_hash, bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", font=txt(9))
    hash_entry.pack(side="left", fill="x", expand=True, ipady=7)

    current_metadata = {"value": None}

    def select_and_analyze():
        path = filedialog.askopenfilename(title="Select a file for evidence analysis")
        if not path:
            return
        try:
            metadata = collect_file_metadata(path)
            current_metadata["value"] = metadata
            selected_path.set(path)
            expected_hash.set("")
            report_text.delete("1.0", tk.END)
            report_text.insert(tk.END, "TRACEX EVIDENCE ANALYSIS\n" + "=" * 58 + "\n")
            labels = [
                ("File name", "file_name"), ("Full path", "full_path"),
                ("Extension", "extension"), ("Size", "size_bytes"),
                ("Created / metadata time*", "created_or_metadata_time"),
                ("Last modified", "last_modified"), ("Last accessed", "last_accessed"),
                ("MIME guess (extension-based)", "mime_type_guess_from_extension"),
                ("Signature identification", "detected_signature_type"),
                ("SHA-256", "sha256"), ("Analysis time", "analysis_time")
            ]
            for label, key in labels:
                value = metadata[key]
                if key == "size_bytes":
                    value = f"{value:,} bytes ({metadata['size_kb']:,} KB)"
                report_text.insert(tk.END, f"{label}:\n{value}\n\n")
            report_text.insert(tk.END, "* Filesystem timestamp labels can vary by operating system.\n")
            report_text.insert(tk.END, "Note: signature and MIME results are best-effort identification, not proof that a file is safe or genuine.\n")
            log_event(f"Evidence analyzed: {metadata['file_name']}", INFO)
        except (OSError, ValueError) as error:
            messagebox.showerror("Analysis Failed", str(error))

    def verify_integrity():
        metadata = current_metadata["value"]
        expected = expected_hash.get().strip().lower()
        if not metadata:
            messagebox.showwarning("No File", "Select and analyze a file first.")
            return
        if not re.fullmatch(r"[0-9a-f]{64}", expected):
            messagebox.showwarning("Invalid SHA-256", "Enter a complete 64-character hexadecimal SHA-256 value.")
            return
        actual = calculate_sha256(metadata["full_path"])
        if actual == expected:
            messagebox.showinfo("Integrity Verification", "MATCH — the current file hash matches the expected SHA-256.")
            log_event("Integrity verification: MATCH", OK)
        else:
            messagebox.showwarning("Integrity Verification", "MISMATCH — the current file hash does not match the expected SHA-256.")
            log_event("Integrity verification: MISMATCH", DANGER)

    def export_json_report():
        metadata = current_metadata["value"]
        if not metadata:
            messagebox.showwarning("No Analysis", "Select and analyze a file before exporting.")
            return
        path = filedialog.asksaveasfilename(title="Export Evidence Analysis JSON", defaultextension=".json", initialfile="TraceX_Evidence_Report.json", filetypes=[("JSON report", "*.json")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as report:
                json.dump({"application": "TraceX", "report_type": "local_file_evidence_analysis", "metadata": metadata, "limitations": ["File signature identification is best-effort and is not a malware scan.", "Filesystem timestamps may vary by operating system.", "This report is not a certified forensic report."]}, report, indent=2, ensure_ascii=False)
            log_event("Evidence analysis JSON exported", ACCENT)
            messagebox.showinfo("Report Exported", f"Structured report saved to:\n{path}")
        except OSError as error:
            messagebox.showerror("Export Failed", str(error))

    button_row = tk.Frame(select_box, bg=PANEL)
    button_row.pack(fill="x")
    make_button(button_row, "ANALYZE FILE  →", select_and_analyze).pack(side="left", padx=(0, 8))
    make_button(button_row, "EXPORT JSON", export_json_report, bg=PANEL2, fg=ACCENT).pack(side="left", padx=(0, 8))
    make_button(button_row, "VERIFY HASH", verify_integrity, bg=PANEL2, fg=INFO).pack(side="left")


# ---------------- HASH COMPARISON LAB ----------------

def show_hash_compare_page():
    clear_content()

    make_label(
        content, "04  /  HASH COMPARISON LAB", 19, ACCENT, True, BG
    ).pack(anchor="w", pady=(8, 5))
    make_label(
        content,
        "Compare two files using cryptographic fingerprints.",
        10, MUTED, False, BG
    ).pack(anchor="w", pady=(0, 22))

    comparison = panel(content, 22, 22)
    comparison.pack(fill="x", pady=(0, 16))

    make_label(comparison, "EVIDENCE A", 11, INFO, True).grid(
        row=0, column=0, sticky="w", pady=(0, 10)
    )
    make_label(comparison, "EVIDENCE B", 11, ACCENT, True).grid(
        row=0, column=1, sticky="w", padx=(20, 0), pady=(0, 10)
    )

    file_a = tk.StringVar()
    file_b = tk.StringVar()

    def choose_file(variable, title):
        path = filedialog.askopenfilename(title=title)
        if path:
            variable.set(path)

    tk.Entry(
        comparison, textvariable=file_a, state="readonly",
        bg=BG, fg=TEXT, readonlybackground=BG,
        relief="flat", font=txt(9)
    ).grid(row=1, column=0, sticky="ew", pady=5)

    tk.Entry(
        comparison, textvariable=file_b, state="readonly",
        bg=BG, fg=TEXT, readonlybackground=BG,
        relief="flat", font=txt(9)
    ).grid(row=1, column=1, sticky="ew", padx=(20, 0), pady=5)

    make_button(
        comparison, "SELECT FILE A",
        lambda: choose_file(file_a, "Select Evidence A"),
        bg=PANEL2, fg=INFO
    ).grid(row=2, column=0, sticky="w", pady=10)

    make_button(
        comparison, "SELECT FILE B",
        lambda: choose_file(file_b, "Select Evidence B"),
        bg=PANEL2, fg=ACCENT
    ).grid(row=2, column=1, sticky="w", padx=(20, 0), pady=10)

    comparison.columnconfigure(0, weight=1)
    comparison.columnconfigure(1, weight=1)

    output = panel(content, 20, 20)
    output.pack(fill="both", expand=True)

    make_label(output, "COMPARISON OUTPUT", 11, INFO, True).pack(
        anchor="w", pady=(0, 12)
    )

    result = tk.Label(
        output, text="Select two files to begin.",
        bg=BG, fg=MUTED, justify="left", anchor="w",
        wraplength=750, font=txt(10),
        padx=14, pady=14
    )
    result.pack(fill="both", expand=True)

    def compare_files():
        if not file_a.get() or not file_b.get():
            messagebox.showwarning(
                "Missing Evidence", "Please select both files."
            )
            return

        try:
            digest_a = calculate_sha256(file_a.get())
            digest_b = calculate_sha256(file_b.get())
            identical = digest_a == digest_b

            if identical:
                status = "MATCH — IDENTICAL CONTENTS"
                color = OK
            else:
                status = "DIFFERENT — CONTENTS DO NOT MATCH"
                color = WARN

            result.config(
                fg=color,
                text=(
                    f"RESULT: {status}\n\n"
                    f"FILE A: {os.path.basename(file_a.get())}\n"
                    f"SHA-256:\n{digest_a}\n\n"
                    f"FILE B: {os.path.basename(file_b.get())}\n"
                    f"SHA-256:\n{digest_b}\n\n"
                    "A match means the SHA-256 fingerprints match. "
                    "A difference means the fingerprints differ."
                )
            )
            log_event(
                "Hash comparison: " + ("MATCH" if identical else "DIFFERENT"),
                color
            )

        except OSError as error:
            messagebox.showerror("Comparison Error", str(error))

    make_button(
        output, "COMPARE FINGERPRINTS  →", compare_files
    ).pack(anchor="w", pady=(14, 0))


# ---------------- URL INSPECTOR ----------------

def inspect_url():
    global url_checks, findings

    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Missing URL", "Enter a URL to inspect.")
        return

    candidate = url
    if "://" not in candidate:
        candidate = "https://" + candidate

    try:
        parsed = urlparse(candidate)
        if not parsed.hostname:
            raise ValueError("The hostname is missing.")

        host = parsed.hostname.lower()
        issues = []

        if parsed.scheme != "https":
            issues.append("Connection does not use HTTPS")
        if "@" in parsed.netloc:
            issues.append("URL contains an @ symbol in its authority")
        if host.startswith("xn--") or ".xn--" in host:
            issues.append("Internationalized domain requires review")
        if re.fullmatch(r"\d+\.\d+\.\d+\.\d+", host):
            issues.append("URL uses an IP address as its host")
        if len(url) > 150:
            issues.append("Unusually long URL")

        suspicious_terms = [
            "login", "verify", "account", "password",
            "urgent", "free-gift", "wallet"
        ]
        if any(term in url.lower() for term in suspicious_terms):
            issues.append("Contains a term sometimes used in phishing")

        url_checks += 1

        if issues:
            findings += 1
            result = "REVIEW RECOMMENDED\n\n" + "\n".join(
                "• " + issue for issue in issues
            )
            result_color = WARN
        else:
            result = (
                "NO BASIC WARNING PATTERN DETECTED\n\n"
                "This limited local check found no configured warning "
                "patterns. The URL is NOT confirmed safe."
            )
            result_color = OK

        result_text.config(state="normal", fg=result_color)
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, f"HOST: {host}\n\n{result}")
        result_text.config(state="disabled")

        log_event(f"URL inspected: {host}", result_color)

    except ValueError as error:
        messagebox.showerror("Invalid URL", f"Please enter a valid URL.\n{error}")


def show_url_page():
    clear_content()

    make_label(
        content, "02  /  URL INSPECTOR", 19, ACCENT, True, BG
    ).pack(anchor="w", pady=(8, 5))
    make_label(
        content,
        "Inspect basic URL patterns locally. No website is opened.",
        10, MUTED, False, BG
    ).pack(anchor="w", pady=(0, 20))

    box = panel(content, 22, 22)
    box.pack(fill="x", pady=(0, 16))

    make_label(box, "TARGET ADDRESS", 10, INFO, True).pack(anchor="w")

    global url_entry
    url_entry = tk.Entry(
        box, bg=BG, fg=TEXT, insertbackground=ACCENT,
        relief="flat", font=txt(12)
    )
    url_entry.pack(fill="x", ipady=12, pady=(12, 15))

    make_button(box, "INSPECT URL  →", inspect_url).pack(anchor="w")

    result_box = panel(content, 18, 18)
    result_box.pack(fill="both", expand=True)

    make_label(
        result_box, "ANALYSIS OUTPUT", 10, INFO, True
    ).pack(anchor="w", pady=(0, 12))

    global result_text
    result_text = tk.Text(
        result_box, height=8, bg=BG, fg=TEXT,
        insertbackground=ACCENT, relief="flat", wrap="word",
        font=txt(10), padx=12, pady=12
    )
    result_text.pack(fill="both", expand=True)
    result_text.insert("1.0", "Waiting for a URL to inspect...")
    result_text.config(state="disabled")


# ---------------- PASSWORD STRENGTH TOOL ----------------

def check_password():
    password = password_entry.get()

    if not password:
        messagebox.showwarning(
            "Missing Input", "Enter a password to test."
        )
        return

    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if re.search(r"[a-z]", password) and re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 1
    if re.search(r"[^a-zA-Z0-9]", password):
        score += 1

    if score <= 2:
        level, color = "WEAK", DANGER
    elif score <= 4:
        level, color = "MODERATE", WARN
    else:
        level, color = "STRONGER PATTERN", OK

    password_result.config(text=f"{level}  /  RULE SCORE {score}/5", fg=color)
    log_event("Password strength rules evaluated", color)


def show_password_page():
    clear_content()

    make_label(
        content, "03  /  PASSWORD LAB", 19, ACCENT, True, BG
    ).pack(anchor="w", pady=(8, 5))
    make_label(
        content,
        "Check basic password composition on your own device.",
        10, MUTED, False, BG
    ).pack(anchor="w", pady=(0, 20))

    box = panel(content, 22, 22)
    box.pack(fill="x")

    make_label(box, "PASSWORD INPUT", 10, INFO, True).pack(anchor="w")

    global password_entry, password_result
    password_entry = tk.Entry(
        box, show="●", bg=BG, fg=TEXT,
        insertbackground=ACCENT, relief="flat",
        font=txt(12)
    )
    password_entry.pack(fill="x", ipady=12, pady=(12, 16))

    make_button(
        box, "CHECK COMPOSITION", check_password
    ).pack(anchor="w")

    password_result = make_label(
        box, "WAITING FOR INPUT", 12, MUTED, True
    )
    password_result.pack(anchor="w", pady=(22, 10))

    make_label(
        box,
        "This is a simple rules-based estimate, not a complete "
        "password security assessment. Use a made-up test password, "
        "not your real password.",
        10, WARN
    ).pack(anchor="w", pady=(8, 0))


# ---------------- OVERVIEW PAGE ----------------

def show_overview():
    clear_content()

    heading = tk.Frame(content, bg=BG)
    heading.pack(fill="x", pady=(8, 20))

    make_label(
        heading, "INVESTIGATION", 19, TEXT, True, BG
    ).pack(anchor="w")
    make_label(
        heading, "LOCAL SECURITY ANALYSIS  /  WORKSPACE 01",
        9, MUTED, True, BG
    ).pack(anchor="w", pady=(6, 0))

    stats = tk.Frame(content, bg=BG)
    stats.pack(fill="x", pady=(0, 18))

    values = [
        ("FILE CHECKS", lambda: str(file_checks), ACCENT),
        ("URL CHECKS", lambda: str(url_checks), INFO),
        ("REVIEW FLAGS", lambda: str(findings), WARN)
    ]

    root.stat_value_labels = {}
    for title, getter, color in values:
        card = panel(stats, 14, 14)
        card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        make_label(card, title, 9, MUTED, True).pack(anchor="w")
        value_label = make_label(card, getter(), 24, color, True)
        value_label.pack(anchor="w", pady=(8, 0))
        root.stat_value_labels[title] = value_label

    work = tk.Frame(content, bg=BG)
    work.pack(fill="both", expand=True)

    left = tk.Frame(work, bg=BG)
    left.pack(side="left", fill="both", expand=True, padx=(0, 12))

    right = panel(work, 15, 15)
    right.pack(side="right", fill="y")

    console = panel(left, 20, 20)
    console.pack(fill="x", pady=(0, 14))

    make_label(
        console, "◈  INVESTIGATION CONSOLE", 11, ACCENT, True
    ).pack(anchor="w")
    make_label(
        console, "Select an instrument to begin local analysis.",
        10, MUTED
    ).pack(anchor="w", pady=(10, 18))

    make_button(console, "01  /  HASH A FILE", lambda: show_page("File Integrity")).pack(
        fill="x", pady=(0, 9)
    )
    make_button(
        console, "02  /  INSPECT A URL",
        lambda: show_page("URL Inspector"), bg=PANEL2, fg=INFO
    ).pack(fill="x", pady=(0, 9))
    make_button(
        console, "03  /  TEST PASSWORD RULES",
        lambda: show_page("Password Lab"), bg=PANEL2, fg=TEXT
    ).pack(fill="x", pady=(0, 9))
    make_button(
        console, "04  /  COMPARE TWO FILES",
        lambda: show_page("Hash Compare"), bg=PANEL2, fg=ACCENT
    ).pack(fill="x")

    activity = panel(left, 15, 15)
    activity.pack(fill="both", expand=True)
    make_label(activity, "ACTIVITY STREAM", 10, INFO, True).pack(
        anchor="w", pady=(0, 12)
    )

    root.activity_frame = tk.Frame(activity, bg=PANEL)
    root.activity_frame.pack(fill="both", expand=True)

    make_label(right, "EVIDENCE", 11, ACCENT, True).pack(anchor="w")
    make_label(right, "LOCAL WORKSPACE", 9, MUTED).pack(
        anchor="w", pady=(5, 18)
    )

    for name, description, color in [
        ("SHA-256", "File fingerprinting", ACCENT),
        ("URL RULES", "Pattern inspection", INFO),
        ("PASSWORD", "Composition rules", WARN),
        ("HASH COMPARE", "Fingerprint comparison", ACCENT)
    ]:
        tk.Frame(right, bg=BORDER, height=1).pack(fill="x", pady=7)
        make_label(right, "● " + name, 10, color, True).pack(anchor="w")
        make_label(right, description, 9, MUTED).pack(
            anchor="w", pady=(5, 0)
        )

    make_label(
        right,
        "NOTE\n\nNo external threat-intelligence\nservice is connected.",
        9, MUTED
    ).pack(anchor="w", pady=(12, 0))



# ---------------- EVIDENCE CASE MANAGER ----------------

def get_cases():
    with sqlite3.connect(DB_PATH) as connection:
        return connection.execute(
            "SELECT id, title, created_at FROM cases ORDER BY id DESC"
        ).fetchall()


def create_evidence_case():
    title = simpledialog.askstring("New Evidence Case", "Case title:", parent=root)
    if not title or not title.strip():
        return
    description = simpledialog.askstring(
        "Case Description", "Short description (optional):", parent=root
    ) or ""
    created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            "INSERT INTO cases(title, description, created_at) VALUES (?, ?, ?)",
            (title.strip(), description.strip(), created)
        )
        new_id = cursor.lastrowid
    log_event(f"Evidence case created: {title.strip()}", ACCENT)
    refresh_case_list(new_id)


def refresh_case_list(select_id=None):
    if not hasattr(root, "case_listbox"):
        return
    root.case_listbox.delete(0, tk.END)
    cases = get_cases()
    chosen_index = None
    for index, (case_id, title, created) in enumerate(cases):
        root.case_listbox.insert(tk.END, f"#{case_id:03d}  {title}  ·  {created[:10]}")
        if case_id == (select_id if select_id is not None else selected_case_id):
            chosen_index = index
    if chosen_index is not None:
        root.case_listbox.selection_set(chosen_index)
        root.case_listbox.activate(chosen_index)
        load_selected_case()
    elif cases:
        root.case_listbox.selection_set(0)
        load_selected_case()
    else:
        root.case_details.config(state="normal")
        root.case_details.delete("1.0", tk.END)
        root.case_details.insert(tk.END, "No cases yet. Create a case to start documenting evidence.")
        root.case_details.config(state="disabled")


def load_selected_case(_event=None):
    global selected_case_id
    if not hasattr(root, "case_listbox"):
        return
    selection = root.case_listbox.curselection()
    if not selection:
        return
    cases = get_cases()
    index = selection[0]
    if index >= len(cases):
        return
    selected_case_id, _, _ = cases[index]
    with sqlite3.connect(DB_PATH) as connection:
        case = connection.execute(
            "SELECT title, description, created_at FROM cases WHERE id = ?",
            (selected_case_id,)
        ).fetchone()
        findings_rows = connection.execute(
            "SELECT finding, created_at FROM case_findings WHERE case_id = ? ORDER BY id DESC",
            (selected_case_id,)
        ).fetchall()
    root.case_details.config(state="normal")
    root.case_details.delete("1.0", tk.END)
    if case:
        title, description, created = case
        root.case_details.insert(tk.END, f"CASE #{selected_case_id:03d}  /  {title}\n")
        root.case_details.insert(tk.END, f"CREATED: {created}\n")
        root.case_details.insert(tk.END, f"DESCRIPTION: {description or '—'}\n")
        root.case_details.insert(tk.END, "\n" + "─" * 58 + "\nFINDINGS / NOTES\n\n")
        if findings_rows:
            for finding, timestamp in findings_rows:
                root.case_details.insert(tk.END, f"[{timestamp}]\n{finding}\n\n")
        else:
            root.case_details.insert(tk.END, "No findings recorded for this case yet.\n")
    root.case_details.config(state="disabled")


def add_case_finding():
    if selected_case_id is None:
        messagebox.showwarning("Select a Case", "Create or select an evidence case first.")
        return
    finding = simpledialog.askstring(
        "Add Finding", "Enter finding / evidence note:", parent=root
    )
    if not finding or not finding.strip():
        return
    created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "INSERT INTO case_findings(case_id, finding, created_at) VALUES (?, ?, ?)",
            (selected_case_id, finding.strip(), created)
        )
    log_event(f"Finding added to case #{selected_case_id:03d}", WARN)
    load_selected_case()


def export_case_report():
    if selected_case_id is None:
        messagebox.showwarning("Select a Case", "Select a case before exporting a report.")
        return
    with sqlite3.connect(DB_PATH) as connection:
        case = connection.execute(
            "SELECT title, description, created_at FROM cases WHERE id = ?",
            (selected_case_id,)
        ).fetchone()
        findings_rows = connection.execute(
            "SELECT finding, created_at FROM case_findings WHERE case_id = ? ORDER BY id",
            (selected_case_id,)
        ).fetchall()
    if not case:
        messagebox.showerror("Export Failed", "The selected case could not be found.")
        return
    path = filedialog.asksaveasfilename(
        title="Export Evidence Case Report",
        defaultextension=".txt",
        initialfile=f"TraceX_Case_{selected_case_id:03d}_Report.txt",
        filetypes=[("Text report", "*.txt")]
    )
    if not path:
        return
    title, description, created = case
    lines = [
        "TRACEX | DIGITAL FORENSICS WORKSTATION",
        "EVIDENCE CASE REPORT",
        "=" * 60,
        f"Case ID: {selected_case_id:03d}",
        f"Title: {title}",
        f"Created: {created}",
        f"Description: {description or '—'}",
        "",
        "FINDINGS / NOTES",
        "-" * 60,
    ]
    if findings_rows:
        for finding, timestamp in findings_rows:
            lines.extend([f"Timestamp: {timestamp}", finding, ""])
    else:
        lines.append("No findings recorded.")
    lines.extend(["", "Generated locally by TraceX.",
                  "This report contains user-entered notes and is not a certified forensic report."])
    try:
        with open(path, "w", encoding="utf-8") as report:
            report.write("\n".join(lines))
        log_event(f"Case report exported: #{selected_case_id:03d}", ACCENT)
        messagebox.showinfo("Report Exported", f"Report saved to:\n{path}")
    except OSError as error:
        messagebox.showerror("Export Failed", str(error))


def show_evidence_cases_page():
    clear_content()
    heading = tk.Frame(content, bg=BG)
    heading.pack(fill="x", pady=(8, 18))
    make_label(heading, "EVIDENCE CASE MANAGER", 19, TEXT, True, BG).pack(anchor="w")
    make_label(heading, "CREATE CASES  /  RECORD FINDINGS  /  EXPORT LOCAL REPORTS",
               9, MUTED, True, BG).pack(anchor="w", pady=(6, 0))

    toolbar = tk.Frame(content, bg=BG)
    toolbar.pack(fill="x", pady=(0, 14))
    make_button(toolbar, "+ NEW CASE", create_evidence_case).pack(side="left", padx=(0, 8))
    make_button(toolbar, "+ ADD FINDING", add_case_finding, bg=PANEL2, fg=INFO).pack(side="left", padx=(0, 8))
    make_button(toolbar, "EXPORT REPORT", export_case_report, bg=PANEL2, fg=ACCENT).pack(side="left")

    workspace = tk.Frame(content, bg=BG)
    workspace.pack(fill="both", expand=True)
    left = panel(workspace, 12, 12)
    left.pack(side="left", fill="y", padx=(0, 12))
    left.configure(width=300)
    left.pack_propagate(False)
    make_label(left, "SAVED CASES", 10, ACCENT, True).pack(anchor="w", pady=(0, 10))
    list_frame = tk.Frame(left, bg=PANEL)
    list_frame.pack(fill="both", expand=True)
    root.case_listbox = tk.Listbox(
        list_frame, bg=PANEL2, fg=TEXT, selectbackground=ACCENT,
        selectforeground=BG, font=txt(9), relief="flat",
        highlightthickness=0, activestyle="none"
    )
    scrollbar = tk.Scrollbar(list_frame, command=root.case_listbox.yview)
    root.case_listbox.configure(yscrollcommand=scrollbar.set)
    root.case_listbox.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    root.case_listbox.bind("<<ListboxSelect>>", load_selected_case)

    right = panel(workspace, 15, 15)
    right.pack(side="left", fill="both", expand=True)
    make_label(right, "CASE FILE / ACTIVITY LOG", 10, INFO, True).pack(anchor="w", pady=(0, 10))
    root.case_details = tk.Text(
        right, bg=PANEL2, fg=TEXT, insertbackground=ACCENT,
        font=txt(10), wrap="word", relief="flat",
        padx=14, pady=14, height=20
    )
    root.case_details.pack(fill="both", expand=True)
    root.case_details.config(state="disabled")
    make_label(right, "Stored locally in tracex_cases.db. Avoid entering sensitive personal data.",
               8, MUTED).pack(anchor="w", pady=(9, 0))
    refresh_case_list()


# ---------------- NAVIGATION ----------------

nav_buttons = {}


def show_page(page):
    global current_page
    current_page = page

    for name, button in nav_buttons.items():
        if name == page:
            button.config(
                bg=ACCENT, fg=BG,
                activebackground=ACCENT, activeforeground=BG
            )
        else:
            button.config(
                bg=PANEL, fg=MUTED,
                activebackground=PANEL2, activeforeground=TEXT
            )

    if page == "Overview":
        show_overview()
        refresh_activity()
    elif page == "File Integrity":
        show_file_page()
    elif page == "Hash Compare":
        show_hash_compare_page()
    elif page == "Evidence Analysis":
        show_evidence_analysis_page()
    elif page == "URL Inspector":
        show_url_page()
    elif page == "Password Lab":
        show_password_page()
    elif page == "Evidence Cases":
        show_evidence_cases_page()


navigation = [
    ("◈", "Overview"),
    ("⌕", "File Integrity"),
    ("⌗", "Evidence Analysis"),
    ("⇄", "Hash Compare"),
    ("⬡", "URL Inspector"),
    ("⚿", "Password Lab"),
    ("▣", "Evidence Cases"),
]

for icon, name in navigation:
    button = tk.Button(
        sidebar,
        text=f"  {icon}   {name}",
        command=lambda p=name: show_page(p),
        bg=PANEL, fg=MUTED,
        activebackground=PANEL2, activeforeground=TEXT,
        anchor="w", relief="flat", bd=0, highlightthickness=0,
        padx=12, pady=13, font=txt(10),
        cursor="hand2"
    )
    button.pack(fill="x", padx=8, pady=3)
    nav_buttons[name] = button

tk.Frame(sidebar, bg=BORDER, height=1).pack(
    fill="x", padx=14, pady=18
)
make_label(sidebar, "SYSTEM", 9, MUTED, True).pack(
    anchor="w", padx=16, pady=(0, 8)
)
make_label(sidebar, "● LOCAL MODE", 9, ACCENT, True).pack(
    anchor="w", padx=16
)
make_label(sidebar, "No API required", 9, MUTED).pack(
    anchor="w", padx=16, pady=(5, 0)
)
make_label(
    sidebar, "TRACEX\nFINAL EDITION\nv1.0\n\nDIGITAL\nEVIDENCE LAB",
    9, MUTED
).pack(side="bottom", anchor="w", padx=16, pady=20)


# ---------------- START ----------------

log_event("TraceX workstation initialized", ACCENT)
update_clock()
show_page("Overview")

root.mainloop()