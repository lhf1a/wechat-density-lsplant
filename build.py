#!/usr/bin/env python3
"""Build an arm64 lab module in this checkout. Never deploy or enable it."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
from prepare_deps import prepare
from package_autostart import package_module

ROOT = Path(__file__).resolve().parent

def run(*args):
    subprocess.run(list(map(str, args)), check=True)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk", default=os.environ.get("ANDROID_SDK_ROOT"))
    parser.add_argument("--ndk", default=os.environ.get("ANDROID_NDK_HOME"))
    parser.add_argument("--android-jar", help="Override SDK platforms/android-35/android.jar")
    parser.add_argument("--d8", help="Override SDK build-tools/35.0.0/d8")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    if not args.sdk or not args.ndk:
        parser.error("provide --sdk and --ndk, or ANDROID_SDK_ROOT and ANDROID_NDK_HOME")
    sdk, ndk = Path(args.sdk).resolve(), Path(args.ndk).resolve()
    android_jar = Path(args.android_jar).resolve() if args.android_jar else sdk / "platforms/android-35/android.jar"
    d8 = Path(args.d8).resolve() if args.d8 else sdk / "build-tools/35.0.0/d8"
    toolchain = ndk / "build/cmake/android.toolchain.cmake"
    for path in (android_jar, d8, toolchain):
        if not path.is_file():
            parser.error("missing build input: " + str(path))
    for tool in ("javac", "cmake", "ninja", "patch"):
        if not shutil.which(tool):
            parser.error("required command not found: " + tool)
    deps = prepare()
    out = ROOT / "build"
    native = out / "native"
    run("cmake", "-S", ROOT, "-B", native, "-G", "Ninja",
        "-DCMAKE_TOOLCHAIN_FILE=" + str(toolchain),
        "-DANDROID_ABI=arm64-v8a", "-DANDROID_PLATFORM=android-28",
        "-DANDROID_STL=c++_static", "-DCMAKE_BUILD_TYPE=Release", "-DDEPS=" + str(deps))
    run("cmake", "--build", native, "--target", "sq2_density_test", "-j", max(1, args.jobs))
    # Fresh temporary Java class directory prevents old nested classes entering the DEX.
    import tempfile
    dex = out / "dex"
    dex.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="java-", dir=out) as classes:
        run("javac", "--release", "8", "-classpath", android_jar, "-d", classes, ROOT / "Hooks.java")
        run(d8, "--min-api", "28", "--lib", android_jar, "--output", dex,
            *sorted(Path(classes).rglob("*.class")))
    module = out / "wechat-density-autostart-0.4.zip"
    package_module(module, native / "libsq2_density_test.so", dex / "classes.dex")
    audit = {
        "outputs": {str(p.relative_to(ROOT)): digest(p) for p in
                    (module, native / "libsq2_density_test.so", dex / "classes.dex")},
        "sources": {name: digest(ROOT / name) for name in
                    ("module.cpp", "gate_policy.h", "Hooks.java", "CMakeLists.txt", "dependencies.json", "lsplant-clang19.patch", "service.sh", "uninstall.sh", "package_autostart.py")},
        "sdk_input_sha256": digest(android_jar),
        "ndk_revision": (ndk / "source.properties").read_text(),
        "device_verified": False,
        "note": "Fresh build only. Exact device-validated files are separately preserved under artifacts/."
    }
    (out / "build-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))

if __name__ == "__main__":
    main()
