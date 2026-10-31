# 实机验证记录

2026-11-01，用户确认：“已确认没问题了”。本仓库从系统移植项目中独立迁出，
迁出时未更改设备模块、系统密度或注入策略。

## 验证对象

- Android 17 / arm64，KernelSU Next33129、Zygisk Next1.5.2。
- 微信8.0.79/versionCode3200、Android user10 主进程。
- 微信身份仍为 SM-F9560 / samsung（现有 Device Faker）；系统窗口密度300dpi。
- 原生库 SHA256：9aefadb39902e3fe814a60e07f161f939f4422e09691a22ad724e22ca1c77243。
- DEX SHA256：591d608519e3b77522b904b3cb1e8ba15622f2c4fb626ec1efeba84e6f09aced。
- ZIP SHA256：8e49d6f4b983e79e074c9f3771834dcb5ca0aebf10b3a57e75917958c52fb741。

## 结果

LSPlant 探针原值7、Hook后11、backup为7，UnHook后恢复7。
最终微信初始化顺序在实时日志中观察到：

```text
INSTALL_STAGE newApplication class=com.tencent.mm.app.Application
WECHAT_HOOKS_READY variant=pre-application-cache-sync windowDpi=300 model=SM-F9560 brand=samsung class=jf5.f
CACHES_SYNCHRONIZED count=3 dpi=300
```

日志缓冲区随后被其它系统日志覆盖，后来导出的空日志不作为独立证据。
设备截图在原实验私有输出中保留，不纳入本仓库。

已检查列表头像与行高比例、完整搜索/加号图标、完整底栏标签，以及聊天文字、
头像、图片、表情和输入栏。全屏、大自由窗口、1103px宽双栏、903px宽单栏
以及放大回双栏的采样画面未再出现原先裁切，Configuration保持300dpi。
测试期间 boot ID、system_server和SurfaceFlinger PID保持不变。

## 已否决方案

- 关闭 h() 并只修改 d/e 返回值：头像比例、图标和底栏异常。
- 保留 h() 但只修改 d/e：右上角图标仍裁切。
- 在 attach/onCreate 后才加构造器同步：安装太晚，没有拦到已完成的初始化。

最终方案在 Application 实例化前安装，并在构造器后同步缓存。

## 当前状态与限制

结束测试时 gate 已删除，下次开机的模块加载已禁用；当前已运行的微信进程
保留 Hook 供用户观察。结束该进程后再启动即恢复原行为，没有开机持久策略。

用户确认的是本轮显示效果。尚未验证所有微信页面、手机端登录共存、
多次重启与长期稳定性。首次登记出现过黑屏，根因未明；后续进程内成功
不能证明启动问题已解决。新目录重新构建的二进制另记为未实机验证。
