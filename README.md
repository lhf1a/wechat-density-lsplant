# WeChat density LSPlant lab module

微信密度修正的独立实验仓库。2026-11-01 用户确认修正后排版没有问题。
源码、依赖源码包、原实机验证产物和构建入口均在本仓库内；不属于系统移植默认构建。

当前源码为 `0.6-auto`：开机一次性授权、本次开机持续启用，没有续期循环。
同时处理微信Tinker热更新切换类加载器，避免旧Hook失效。原0.1实测包保留；
0.3仅作为失败对照，不用于交付。0.4完整包重启、开机自动启用、热更新后的
密度同步及列表视觉检查通过，详见DEPLOYMENT.md。

## 实现与范围

Zygisk 在 Android user0/user10 的 `com.tencent.mm` 主进程中加载 LSPlant。
兼容已核对的微信 8.0.79 / versionCode3200（`jf5.f`）和
8.0.80 / versionCode3220（`bf5.f`）；不以版本号代替实际方法形状校验。探针模式只接受
`local.surface.identityprobe`。不向 system_server、QQ 或微信子进程安装 Hook。

在 `Instrumentation.newApplication(ClassLoader,String,Context)` 原方法前，
按当前类加载器查找 `jf5.f` 或 `bf5.f`，安装其构造器及 d/e 方法 Hook。构造器原逻辑完成后，同步三份
DisplayMetrics 缓存和直接改写的主题资源；读取方法沿用原像素尺寸，使用实际
窗口的 densityDpi、density、scaledDensity。保留微信 h()/i() 路径，使位图
默认密度与资源同步。既有 Device Faker 提供的 Z Fold6 身份保持不变。

Tinker启用时，在DelegateLastClassLoader构造后按新类安装同样的密度Hook，
并在Application创建后核对类身份；不清除微信热更新数据。

此前仅修改密度读取结果、或等到 Application.attach/onCreate 才安装的版本，
都出现过头像比例不一致及图标裁切。不要恢复这些已失败的方案。

## 0.6 修复与验证

微信升级到8.0.80后，基础APK和活动Tinker补丁的密度类均改名为`bf5.f`；
旧DEX仍硬编码`jf5.f`。故障设备的本boot授权有效、原生库已加载，问题不是续期丢失。
普通安装和Tinker加载器回调现在共用`resolveDensity`，按传入加载器查找两种已知类名，
保留不提前初始化类、Application创建前安装及构造器后同步缓存的行为。

2026-11-16已仅部署新DEX并重启微信，观察到基础/Tinker两次Hook成功，
3份缓存在onCreate之前同步300dpi；当前自由窗口列表的头像、搜索/加号与底栏完整。
未重启系统，未清数据或改全局密度。该结果不等于新SO/完整ZIP经过系统重启验收。
详细边界见VALIDATION.md。0.6包从源码构建到ignored build/，不覆盖历史归档。

主机回归：`python3 test_density_lookup.py`、`python3 test_service.py`；
历史归档完整性：`python3 verify.py`。前者运行实际查找方法的Java类加载器夹具，
覆盖旧/新类名、Tinker不同类身份、未知类拒绝及不提前初始化，不冒充Android Hook测试。

## 已验证产物

历史完整重启验收包为 `artifacts/2026-11-01-autostart-0.4/wechat-density-autostart-0.4.zip`，
同目录保存原生库、DEX、校验、构建审计及实机验证manifest。

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

输出 `build/wechat-density-autostart-0.6.zip`、`build/dex/classes.dex`、
`build/native/libsq2_density_test.so` 和 `build/build-audit.json`。
新构建默认标为未经过实机验证；源路径、调试信息和打包时间可造成哈希变化。

## 开机启用与回退

此模块按设备现有 KernelSU/Zygisk Next 链路使用，无需 Vector 或 Meta 模块。
当前安装包启用后，KernelSU在开机时执行一次service.sh，写入仅匹配本次boot ID的
`0 wechat-auto`授权。它不计时续期，也不保留后台进程。Java层沿用原密度逻辑并
增加Tinker类加载器适配；原生层在每次目标进程创建前检查disable/remove。
关闭或卸载模块即阻止后续注入，当前已运行微信的Hook要结束进程才能撤销。

若需手动限时测试，仍可在Android root shell写入原格式开关：

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

手动probe/wechat模式绑定boot ID和BOOTTIME截止值；wechat-auto模式要求deadline=0，
且只接受微信主进程。开关缺失、手动模式过期或boot ID不匹配时不初始化LSPlant；
这不能隔离SO自身加载故障。删除开关只阻止新进程注入，当前进程Hook会继续运行。

完整回退：

```sh
rm -f /data/adb/sq2-density-test/gate
/data/adb/ksud module disable sq2_density_test
am force-stop --user 10 com.tencent.mm
```

原0.1归档安装包仍默认禁用并使用限时gate；不要将其与当前0.4开机版本混淆。
保留现有Device Faker、Zygisk Next和微信数据。
首次登记曾发生黑屏，后来同一原生库在用户手动启动后工作；原因仍未确定，
不能把本轮应用内检查视为启动稳定性已经验证。

## 许可证

本仓库模块源码及其构建脚本采用 LGPL-3.0-or-later。依赖许可证及来源见
[THIRD_PARTY.md](THIRD_PARTY.md)；相应原始源码包、编译兼容补丁及重建入口
一并保留。微信 APK、聊天内容、原始截图、凭据和设备原始日志不在仓库中。
