#!/usr/bin/env python3
"""Check one-shot startup, disable/remove, uninstall and the native gate policy."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as temp:
    base = Path(temp)
    module = base / "sq2_density_test"
    module.mkdir()
    state = base / "state"
    boot = base / "boot"
    boot.write_text("fixture-boot\n")
    for name in ("service.sh", "uninstall.sh"):
        script = (ROOT / name).read_text().replace("STATE=/data/adb/sq2-density-test", "STATE=" + str(state))
        script = script.replace("BOOT_FILE=/proc/sys/kernel/random/boot_id", "BOOT_FILE=" + str(boot))
        (module / name).write_text(script)
        subprocess.run(["sh", "-n", str(module / name)], check=True)
    subprocess.run(["sh", str(module / "service.sh")], check=True, timeout=2)
    assert (state / "gate").read_text().split() == ["fixture-boot", "0", "wechat-auto"]
    assert (state / "gate").stat().st_mode & 0o777 == 0o600
    assert not (state / "auto.pid").exists()
    for flag in ("disable", "remove"):
        (state / "gate").unlink()
        (module / flag).touch()
        subprocess.run(["sh", str(module / "service.sh")], check=True, timeout=2)
        assert not (state / "gate").exists()
        (module / flag).unlink()
        subprocess.run(["sh", str(module / "service.sh")], check=True, timeout=2)
    subprocess.run(["sh", str(module / "uninstall.sh")], check=True, timeout=2)
    assert not state.exists()
    source = base / "gate_test.cpp"
    source.write_text('''#include "gate_policy.h"
#include <cassert>
int main() {
  assert(gateAllows("b", "b", "wechat-auto", 0, 999999, "com.tencent.mm"));
  assert(!gateAllows("b", "old", "wechat-auto", 0, 1, "com.tencent.mm"));
  assert(!gateAllows("", "", "wechat-auto", 0, 1, "com.tencent.mm"));
  assert(!gateAllows("b", "b", "wechat-auto", 10, 1, "com.tencent.mm"));
  assert(!gateAllows("b", "b", "wechat-auto", 0, 1, "com.tencent.mm:tools"));
  assert(!gateAllows("b", "b", "wechat-auto", 0, 1, "local.surface.identityprobe"));
  assert(gateAllows("b", "b", "wechat", 10, 10, "com.tencent.mm"));
  assert(!gateAllows("b", "b", "wechat", 10, 11, "com.tencent.mm"));
  assert(!gateAllows("b", "b", "wechat", 0, 1, "com.tencent.mm"));
  assert(gateAllows("b", "b", "probe", 10, 1, "local.surface.identityprobe"));
  assert(!gateAllows("b", "b", "probe", 10, 1, "com.tencent.mm"));
  assert(!gateAllows("b", "b", "unknown", 10, 1, "com.tencent.mm"));
  assert(userAndProcessAllowed(10123, "com.tencent.mm"));
  assert(userAndProcessAllowed(1010123, "com.tencent.mm"));
  assert(userAndProcessAllowed(10124, "local.surface.identityprobe"));
  assert(!userAndProcessAllowed(-1, "com.tencent.mm"));
  assert(!userAndProcessAllowed(1110123, "com.tencent.mm"));
  assert(!userAndProcessAllowed(10123, "com.tencent.mm:tools"));
  assert(!userAndProcessAllowed(10123, "com.tencent.mobileqq"));
}
''')
    executable = base / "gate_test"
    subprocess.run(["c++", "-std=c++17", "-I", str(ROOT), str(source), "-o", str(executable)], check=True)
    subprocess.run([str(executable)], check=True)
    print("PASS: one-shot startup, permissions, disable/remove, uninstall and 12 native gate cases")
