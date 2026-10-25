```python
import hashlib
import re
import socket
from urllib.parse import urlparse

import streamlit as st

st.set_page_config(
    page_title="TraceX | Security Toolkit",
    page_icon="🛡️",
    layout="wide",
)

st.markdown("""
<style>
.stApp {
    background-color: #0b1020;
    color: #edf2ff;
}
section[data-testid="stSidebar"] {
    background-color: #111a2e;
}
h1, h2, h3 {
    color: #7dd3fc;
}
div[data-testid="stMetric"] {
    background: #151f35;
    padding: 18px;
    border-radius: 12px;
}
.stButton button {
    background-color: #0e7490;
    color: white;
    border-radius: 8px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ TraceX")
st.caption("CYBERSECURITY TOOLKIT | WEB EDITION")

st.sidebar.title("TraceX Navigation")
page = st.sidebar.radio(
    "Select a security tool",
    [
        "Dashboard",
        "File Integrity Lab",
        "Password Lab",
        "Host Risk Analyzer",
        "About TraceX",
    ],
)

if page == "Dashboard":
    st.subheader("Security Operations Dashboard")
    st.write(
        "A lightweight security toolkit for file verification, "
        "password assessment, and basic hostname checks."
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Security Modules", "3")
    col2.metric("Deployment", "Cloud Web")
    col3.metric("Status", "Ready")

    st.info(
        "Choose a tool from the sidebar to begin. "
        "This web edition is separate from the original desktop app."
    )

elif page == "File Integrity Lab":
    st.subheader("🔐 File Integrity Lab")
    st.write(
        "Compare SHA-256 hashes to determine whether two uploaded "
        "files contain identical bytes."
    )

    file1 = st.file_uploader(
        "Upload the original file",
        key="original",
    )
    file2 = st.file_uploader(
        "Upload the file to compare",
        key="comparison",
    )

    if st.button("Compare Files"):
        if file1 is None or file2 is None:
            st.warning("Upload both files before comparing.")
        else:
            data1 = file1.getvalue()
            data2 = file2.getvalue()

            hash1 = hashlib.sha256(data1).hexdigest()
            hash2 = hashlib.sha256(data2).hexdigest()

            st.write("**Original SHA-256**")
            st.code(hash1)

            st.write("**Comparison SHA-256**")
            st.code(hash2)

            if hash1 == hash2:
                st.success("MATCH: Both files have identical contents.")
            else:
                st.error("MISMATCH: The file contents are different.")

elif page == "Password Lab":
    st.subheader("🔑 Password Strength Lab")
    st.write(
        "Assess password characteristics locally within this app. "
        "Do not enter a real password that you currently use."
    )

    password = st.text_input(
        "Enter a test password",
        type="password",
        help="Use a fictional password for demonstration.",
    )

    if st.button("Analyze Password"):
        if not password:
            st.warning("Enter a test password.")
        else:
            checks = {
                "At least 12 characters": len(password) >= 12,
                "Contains uppercase letters": bool(re.search(r"[A-Z]", password)),
                "Contains lowercase letters": bool(re.search(r"[a-z]", password)),
                "Contains numbers": bool(re.search(r"\d", password)),
                "Contains symbols": bool(re.search(r"[^A-Za-z0-9]", password)),
            }

            score = sum(checks.values())

            for label, passed in checks.items():
                st.write(
                    f"{'✅' if passed else '❌'} {label}"
                )

            if score == 5:
                st.success("Good characteristics across all five checks.")
            elif score >= 3:
                st.warning("Some useful characteristics are present. Improve the missing checks.")
            else:
                st.error("Several basic strength characteristics are missing.")

            st.caption(
                "This is a basic educational heuristic, not a guarantee "
                "of password security. It does not check leaked-password databases."
            )

elif page == "Host Risk Analyzer":
    st.subheader("🌐 Host Risk Analyzer")
    st.write(
        "Inspect URL formatting and optionally test DNS resolution. "
        "This is a basic diagnostic, not a malware or phishing detector."
    )

    address = st.text_input(
        "Enter a hostname or URL",
        placeholder="https://example.com",
    )

    if st.button("Analyze Host"):
        if not address.strip():
            st.warning("Enter a hostname or URL.")
        else:
            candidate = address.strip()

            if "://" not in candidate:
                candidate = "https://" + candidate

            parsed = urlparse(candidate)
            hostname = parsed.hostname

            if not hostname:
                st.error("The input is not a valid hostname or URL.")
            else:
                st.write(f"**Hostname:** `{hostname}`")
                st.write(
                    f"**HTTPS scheme:** "
                    f"{'Yes' if parsed.scheme == 'https' else 'No'}"
                )

                if parsed.scheme != "https":
                    st.warning(
                        "The URL does not specify HTTPS. "
                        "This alone does not establish that the host is malicious."
                    )

                try:
                    ip_address = socket.getaddrinfo(
                        hostname,
                        None,
                        type=socket.SOCK_STREAM,
                    )[0][4][0]

                    st.success("DNS resolution succeeded.")
                    st.write(f"**Resolved IP:** `{ip_address}`")
                except (socket.gaierror, OSError):
                    st.warning(
                        "DNS resolution failed or the host could not be reached "
                        "from the hosting environment."
                    )

                st.caption(
                    "DNS resolution and HTTPS formatting cannot establish "
                    "whether a website is safe or malicious."
                )

elif page == "About TraceX":
    st.subheader("About the Project")
    st.write("""
    **TraceX — Cybersecurity Toolkit**

    TraceX is a student project that demonstrates basic cybersecurity
    concepts through a desktop application and a separate web interface.

    **Web modules**
    - SHA-256 file-integrity comparison
    - Password-characteristic assessment
    - Basic hostname and URL diagnostics

    **Limitations**

    The web edition is an educational demonstration. It is not a full
    vulnerability scanner, malware detector, or professional security
    auditing platform.
    """)

st.divider()
st.caption("TraceX | Educational Cybersecurity Project")
```
