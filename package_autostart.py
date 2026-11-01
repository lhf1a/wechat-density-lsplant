#!/usr/bin/env python3
"""Package the current-boot persistent mode with no renewal worker."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent

def package_module(output, native, dex):
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as target:
        target.write(native, "zygisk/arm64-v8a.so")
        target.write(dex, "classes.dex")
        target.writestr("skip_mount", "")
        target.writestr("module.prop", "id=sq2_density_test\nname=WeChat window density\nversion=0.4-auto\nversionCode=4\nauthor=SQ2 lab\ndescription=WeChat 8.0.79 window density; boot-persistent authorization without renewal; user10 main process only.\n")
        target.writestr("customize.sh", 'SKIPUNZIP=0\nchmod 755 "$MODPATH/service.sh" "$MODPATH/uninstall.sh"\n')
        for name in ("service.sh", "uninstall.sh"):
            target.write(ROOT / name, name)
