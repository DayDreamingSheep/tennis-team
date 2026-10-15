"""HTTPS that works on any Mac Python.

Python from python.org often has no root certificates until "Install Certificates.command" is run, so urllib fails
with CERTIFICATE_VERIFY_FAILED. When that happens we build an SSL context from certifi (if installed) or from the
Mac's own system root certificates (security find-certificate), cached in a temp file. Standard library only.
"""

import ssl
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

_CTX = None


def _fallback_context():
    global _CTX
    if _CTX:
        return _CTX
    try:
        import certifi  # type: ignore
        _CTX = ssl.create_default_context(cafile=certifi.where())
        return _CTX
    except Exception:
        pass
    pem = Path(tempfile.gettempdir()) / "tennis-team-roots.pem"
    if not pem.exists() or pem.stat().st_size < 1000:
        out = subprocess.run(["/usr/bin/security", "find-certificate", "-a", "-p",
                              "/System/Library/Keychains/SystemRootCertificates.keychain"],
                             capture_output=True, text=True, timeout=20)
        pem.write_text(out.stdout, encoding="utf-8")
    _CTX = ssl.create_default_context(cafile=str(pem))
    return _CTX


def urlopen(req, timeout=30):
    """Like urllib.request.urlopen, retrying with Mac/certifi roots on a certificate error."""
    try:
        return urllib.request.urlopen(req, timeout=timeout, context=_CTX) if _CTX else urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.URLError as exc:
        if isinstance(getattr(exc, "reason", None), ssl.SSLCertVerificationError):
            return urllib.request.urlopen(req, timeout=timeout, context=_fallback_context())
        raise
