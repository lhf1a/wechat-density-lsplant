// SPDX-License-Identifier: LGPL-3.0-or-later
#pragma once
#include <string_view>

inline bool userAndProcessAllowed(int uid, std::string_view process) {
    if (uid < 0) return false;
    const int user = uid / 100000;
    return (user == 0 || user == 10) &&
           (process == "com.tencent.mm" || process == "local.surface.identityprobe");
}

inline bool gateAllows(std::string_view boot, std::string_view expected,
                       std::string_view mode, long deadline, long now,
                       std::string_view process) {
    if (boot.empty() || boot != expected) return false;
    if (mode == "wechat-auto") return deadline == 0 && process == "com.tencent.mm";
    if (deadline <= 0 || now > deadline) return false;
    return (mode == "wechat" && process == "com.tencent.mm") ||
           (mode == "probe" && process == "local.surface.identityprobe");
}
