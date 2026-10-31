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

base = "artifacts/2026-11-01-validated/"
manifest = json.loads(read(base + "manifest.json"))
payloads = {name: checked(base + name, expected)
            for name, expected in manifest["files"].items()}
with zipfile.ZipFile(io.BytesIO(payloads["sq2-density-test.zip"])) as archive:
    if archive.read("classes.dex") != payloads["classes.dex"]:
        raise SystemExit("ZIP DEX differs from saved DEX")
    if archive.read("zygisk/arm64-v8a.so") != payloads["arm64-v8a.so"]:
        raise SystemExit("ZIP native library differs from saved SO")
    if "disable" not in archive.namelist():
        raise SystemExit("ZIP is missing its default-disable marker")
for entry in json.loads(read("dependencies.json")).values():
    checked(entry["archive"], entry["archive_sha256"])
print("PASS: saved ZIP/DEX/SO, embedded payloads, disable marker and six dependency archives"
      + (" (Git index)" if USE_INDEX else " (working tree)"))
