#!/usr/bin/env python3
"""Expand checksum-locked bundled source archives; no parent-project dependency."""
from pathlib import Path
import hashlib
import json
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parent

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def prepare():
    lock = ROOT / "dependencies.json"
    patch = ROOT / "lsplant-clang19.patch"
    expected = {"lock_sha256": sha256(lock), "patch_sha256": sha256(patch)}
    build = ROOT / "build"
    build.mkdir(exist_ok=True)
    dest = build / "deps"
    if dest.exists():
        stamp = dest / ".source-stamp.json"
        if stamp.exists() and json.loads(stamp.read_text()) == expected:
            return dest
        raise RuntimeError("build/deps exists with a different source stamp; use a fresh checkout/build directory")
    dependencies = json.loads(lock.read_text())
    with tempfile.TemporaryDirectory(prefix="deps-", dir=build) as temporary:
        staged = Path(temporary) / "deps"
        staged.mkdir()
        for name, item in dependencies.items():
            archive = ROOT / item["archive"]
            if sha256(archive) != item["archive_sha256"]:
                raise RuntimeError("Archive checksum mismatch: " + name)
            unpack = Path(temporary) / name
            unpack.mkdir()
            with tarfile.open(archive) as source:
                source.extractall(unpack, filter="data")
            children = list(unpack.iterdir())
            if len(children) != 1 or not children[0].is_dir():
                raise RuntimeError("Expected one source root in " + name)
            target = staged / item["destination"]
            if target.exists() and (not target.is_dir() or any(target.iterdir())):
                raise RuntimeError("Dependency destination is not empty: " + str(target))
            if target.exists():
                target.rmdir()
            target.parent.mkdir(parents=True, exist_ok=True)
            children[0].rename(target)
        subprocess.run(["patch", "-p1", "--batch", "--forward", "-i", str(patch)],
                       cwd=staged / "lsplant", check=True)
        (staged / ".source-stamp.json").write_text(json.dumps(expected, indent=2) + "\n")
        staged.rename(dest)
    return dest

if __name__ == "__main__":
    print(prepare())
