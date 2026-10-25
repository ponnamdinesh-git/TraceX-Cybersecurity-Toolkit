# Build TraceX.exe on Windows

Run these commands from the folder containing `tracex.py`.

## 1. Create a virtual environment

```powershell
py -m venv .venv
```

## 2. Install the build tool

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install pyinstaller
```

## 3. Build the executable

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --onefile --name TraceX tracex.py
```

The executable should be created at `dist\TraceX.exe`.

## 4. Test before publishing

- Launch `dist\TraceX.exe` from File Explorer.
- Test file hashing and hash comparison.
- Test URL inspection and Password Lab.
- Create a dummy evidence case and verify it persists after closing/reopening.
- Test JSON export and report generation.
- Confirm where the database and exports are written.

## Notes

- Build the executable on Windows for Windows distribution.
- Antivirus tools may flag newly built unsigned executables. This does not automatically mean the file is malicious, but users should download only from the repository you control and inspect warnings carefully.
- Do not publish real evidence files, private reports, or a database containing personal data.
- If the app uses a relative path for its SQLite database, inspect and test that behavior in the packaged build.
