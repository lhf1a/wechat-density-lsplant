#!/usr/bin/env python3
"""Verify saved artifacts, embedded ZIP payloads and bundled dependency archives."""
from pathlib import Path
import hashlib
import io
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
USE_INDEX = "--index" in sys.argv[1:]

def read(relative):
    if USE_INDEX:
        return subprocess.check_output(["git", "show", ":" + relative], cwd=ROOT)
    return (ROOT / relative).read_bytes()

def checked(relative, expected):
    data = read(relative)
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise SystemExit("SHA256 mismatch: " + relative)
    return data

for release in ("2026-11-01-validated", "2026-11-01-autostart-0.3", "2026-11-01-autostart-0.4"):
    base = "artifacts/" + release + "/"
    manifest = json.loads(read(base + "manifest.json"))
    payloads = {name: checked(base + name, expected)
                for name, expected in manifest["files"].items()}
    package = manifest.get("package", "sq2-density-test.zip")
    with zipfile.ZipFile(io.BytesIO(payloads[package])) as archive:
        if archive.read("classes.dex") != payloads["classes.dex"]:
            raise SystemExit("ZIP DEX differs from saved DEX: " + release)
        if archive.read("zygisk/arm64-v8a.so") != payloads["arm64-v8a.so"]:
            raise SystemExit("ZIP native library differs from saved SO: " + release)
        if manifest.get("default_enabled", False):
            if "disable" in archive.namelist():
                raise SystemExit("Automatic package unexpectedly disabled")
            if hashlib.sha256(archive.read("service.sh")).hexdigest() != manifest["service_sha256"]:
                raise SystemExit("Automatic startup script checksum mismatch")
        elif "disable" not in archive.namelist():
            raise SystemExit("Lab ZIP is missing its default-disable marker")
for entry in json.loads(read("dependencies.json")).values():
    checked(entry["archive"], entry["archive_sha256"])
print("PASS: three saved releases, embedded ZIP payloads, startup modes and six dependency archives"
      + (" (Git index)" if USE_INDEX else " (working tree)"))
