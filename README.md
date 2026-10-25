# TraceX — Cybersecurity & Digital Forensics Workstation

TraceX is a Python desktop application built with Tkinter for basic file-integrity checks, hash comparison, evidence review, URL risk indicators, password-composition checks, and evidence-case organization.

> **Important:** TraceX is an educational triage tool. Its results are indicators for review, not definitive proof that a file, URL, or password is safe or malicious. Do not use it as a replacement for professional incident-response tools.

## Features

- **Overview dashboard** — entry point for the available tools.
- **File Integrity** — calculate a file's SHA-256 hash to support integrity checks.
- **Evidence Analysis** — inspect available file information and hash details.
- **Hash Compare** — compare hash values or file hashes to identify differences.
- **URL Inspector** — flag selected URL patterns and connection-security indicators for manual review.
- **Password Lab** — assess basic password composition; this is not a password-cracking tool.
- **Evidence Cases** — organize cases and findings using local storage.
- **Exports and reports** — export supported analysis data as JSON and generate case reports.

Feature availability and exact labels depend on the included application version.

## Technology

- Python 3
- Tkinter / ttk for the desktop interface
- `hashlib` for hashing
- `sqlite3` for local case storage
- `json`, `urllib.parse`, and other Python standard-library modules

The project is designed to use Python's standard library only. No third-party packages are required to run the source code. Tkinter is normally included with standard Windows Python installations.

## Requirements

- Windows 10/11
- Python 3.10 or newer recommended for running from source
- A local copy of this repository

## Run from source

1. Install Python from the official Python website: https://www.python.org/downloads/windows/
2. During installation, enable **Add Python to PATH**.
3. Download or clone this repository.
4. Open the project folder in VS Code.
5. Open Terminal → New Terminal.
6. Run:

   ```powershell
   python --version
   python tracex.py
   ```

If the `python` command is unavailable, try `py --version` and `py tracex.py`.

## Build a Windows executable

The PyInstaller package is needed only to build the executable; it is not a runtime dependency of the TraceX source code.

1. Open PowerShell or the VS Code terminal in the project directory.
2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the build tool:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install pyinstaller
   ```

4. Build a single-file Windows executable:

   ```powershell
   python -m PyInstaller --noconfirm --clean --windowed --onefile --name TraceX tracex.py
   ```

5. Find the executable at `dist\TraceX.exe`.
6. Test it by opening it from File Explorer. Check that case saving and report/export functions work as expected.

If Windows PowerShell blocks virtual-environment activation, run the build commands with `.venv\Scripts\python.exe` directly, or use Command Prompt and `.venv\Scripts\activate.bat`.

### Local data and database

TraceX may create a local SQLite database (for example, `tracex_cases.db`) while running. Keep user-generated case data separate from the source repository. Do not upload real, private, or sensitive evidence, reports, passwords, or personal data to a public repository. If the app currently expects the database beside the script, test the packaged executable carefully before distributing it; a PyInstaller build can change path behavior.

## Repository contents

```text
TraceX/
├── tracex.py
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
├── screenshots/
└── dist/                 # generated locally; usually not committed to source
```

This is the recommended layout. Keep your existing application files and folder structure; add the documentation/configuration files as appropriate.

## Security and privacy notes

- Use TraceX only on files and URLs you are authorized to inspect.
- Treat findings as preliminary indicators and verify them independently.
- Do not enter real or reused passwords into demonstrations, screenshots, or public issue reports.
- Do not commit private evidence, exported reports, databases containing personal data, API keys, tokens, or other secrets.
- A hash match supports byte-for-byte integrity comparison only when the reference hash is trustworthy.
- URL checks based on patterns can produce false positives and false negatives.

## Limitations

TraceX is a learning and demonstration project. It does not provide a full malware sandbox, antivirus verdict, forensic chain-of-custody certification, or guaranteed phishing detection.

## Author

Add your preferred name, college/course, and contact/profile links here before publishing.

## License

See [LICENSE](LICENSE).
