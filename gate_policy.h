// SPDX-License-Identifier: LGPL-3.0-or-later
#pragma once
#include <string_view>

inline bool gateAllows(std::string_view boot, std::string_view expected,
                       std::string_view mode, long deadline, long now,
                       std::string_view process) {
    if (boot.empty() || boot != expected) return false;
    if (mode == "wechat-auto") return deadline == 0 && process == "com.tencent.mm";
    if (deadline <= 0 || now > deadline) return false;
    return (mode == "wechat" && process == "com.tencent.mm") ||
           (mode == "probe" && process == "local.surface.identityprobe");
}
