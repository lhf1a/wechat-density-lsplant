# WeChat density LSPlant lab module

微信密度修正的独立实验仓库。2026-11-01 用户确认修正后排版没有问题。
源码、依赖源码包、原实机验证产物和构建入口均在本仓库内；不属于系统移植默认构建。

## 实现与范围

Zygisk 在 Android user10 的 `com.tencent.mm` 主进程中加载 LSPlant。
仅支持实测微信 8.0.79 / versionCode3200；探针模式只接受
`local.surface.identityprobe`。不向 system_server、QQ 或微信子进程安装 Hook。

在 `Instrumentation.newApplication(ClassLoader,String,Context)` 原方法前，
安装 `jf5.f` 的构造器及 d/e 方法 Hook。构造器原逻辑完成后，同步三份
DisplayMetrics 缓存和直接改写的主题资源；读取方法沿用原像素尺寸，使用实际
窗口的 densityDpi、density、scaledDensity。保留微信 h()/i() 路径，使位图
默认密度与资源同步。既有 Device Faker 提供的 Z Fold6 身份保持不变。

此前仅修改密度读取结果、或等到 Application.attach/onCreate 才安装的版本，
都出现过头像比例不一致及图标裁切。不要恢复这些已失败的方案。

## 已验证产物

`artifacts/2026-11-01-validated/` 原样保留实测文件：

- `sq2-density-test.zip`：可安装模块包，默认含 disable 标记。
- `classes.dex`：实测 Java Hook 载荷。
- `arm64-v8a.so`：实测原生库，包含调试信息，未重新 strip。
- `SHA256SUMS`、`manifest.json`：校验与来源记录。

实机检查结果和限制见 [VALIDATION.md](VALIDATION.md)。构建不会自动安装、
启用模块或重启设备。不要用新构建覆盖原样保存的实测产物。

## 独立构建

需要 Linux/WSL、Python 3.12+、JDK 17+、CMake 3.28+、Ninja、patch，
以及 Android SDK 的 API35 android.jar、D8 和 Android NDK r28c。
依赖源码包已随仓库保存在 `vendor/sources/`，构建不需要联网。
`prepare_deps.py` 核验归档 SHA256，再展开到忽略的 build/deps 并应用兼容补丁。

标准 SDK 布局：

```sh
python3 build.py --sdk /path/to/android-sdk --ndk /path/to/android-ndk-r28c
```

也可设置 `ANDROID_SDK_ROOT`、`ANDROID_NDK_HOME`。非标准 SDK 布局可显式指定：

```sh
python3 build.py --sdk /path/to/sdk --ndk /path/to/ndk \
  --android-jar /path/to/android.jar --d8 /path/to/d8
```

输出 `build/sq2-density-test.zip`、`build/dex/classes.dex`、
`build/native/libsq2_density_test.so` 和 `build/build-audit.json`。
新构建默认标为未经过实机验证；源路径、调试信息和打包时间可造成哈希变化。

## 临时测试与回退

此模块按设备现有 KernelSU/Zygisk Next 链路使用，无需 Vector 或 Meta 模块。
安装后默认禁用；新登记可能需要另行授权重启，不自动改变现有启动入口。
开启 Hook 还需要 Android root shell 中的显式限时 gate：

```sh
mkdir -p /data/adb/sq2-density-test
chmod 700 /data/adb/sq2-density-test
boot=$(cat /proc/sys/kernel/random/boot_id)
up=$(cut -d. -f1 /proc/uptime)
echo "$boot $((up+600)) wechat" > /data/adb/sq2-density-test/gate
chmod 600 /data/adb/sq2-density-test/gate
# 仅在模块已实际登记且设备允许重启微信时：
am force-stop --user 10 com.tencent.mm
am start --user 10 -n com.tencent.mm/.ui.LauncherUI
```

gate 的模式可为 probe/wechat，且绑定 boot ID 和 BOOTTIME 截止值。
gate 缺失、过期或跨重启时不初始化 LSPlant；这不能隔离 SO 自身加载故障。
到期或删除 gate 只阻止新进程注入，当前进程的 Hook 仍会继续运行。

完整回退：

```sh
rm -f /data/adb/sq2-density-test/gate
/data/adb/ksud module disable sq2_density_test
am force-stop --user 10 com.tencent.mm
```

保留现有 Device Faker、Zygisk Next 和微信数据。没有配置开机持久 gate。
首次登记曾发生黑屏，后来同一原生库在用户手动启动后工作；原因仍未确定，
不能把本轮应用内检查视为启动稳定性已经验证。

## 许可证

本仓库模块源码及其构建脚本采用 LGPL-3.0-or-later。依赖许可证及来源见
[THIRD_PARTY.md](THIRD_PARTY.md)；相应原始源码包、编译兼容补丁及重建入口
一并保留。微信 APK、聊天内容、原始截图、凭据和设备原始日志不在仓库中。
