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

以下是0.1结束测试时的状态。用户随后要求清理实验残留并开机自动启用。
当前0.4增加一次性持续授权和Tinker类加载器适配，已完成完整包重启及微信冷启动
密度/身份/列表排版复核；本地12项原生开关用例及一次性启动/禁用/移除/卸载检查
通过。0.3为未处理Tinker的失败对照。详细结果见DEPLOYMENT.md。

结束测试时 gate 已删除，下次开机的模块加载已禁用；当前已运行的微信进程
保留 Hook 供用户观察。结束该进程后再启动即恢复原行为，没有开机持久策略。

用户确认的是本轮显示效果。尚未验证所有微信页面、手机端登录共存、
多次重启与长期稳定性。首次登记出现过黑屏，根因未明；后续进程内成功
不能证明启动问题已解决。新目录重新构建的二进制另记为未实机验证。

## 2026-11-16：0.6 / 微信8.0.80类名适配

实际故障设备已升级微信8.0.80/versionCode3220、Android user0，活动Tinker为
patch-40d098e8。只读核对本boot gate有效，原生模块已加载；已安装旧DEX只有
jf5.f查找，当前基础APK和活动Tinker DEX的密度类均为bf5.f，且保留static d()、
instance e()返回DisplayMetrics、DisplayMetrics构造器和3份静态缓存的接口形状。

Hooks.resolveDensity按传入ClassLoader支持jf5.f/bf5.f，普通安装和patchLoader
回调共同使用。原生过滤/授权/服务、机型伪装、h()/i()及缓存同步时机保持。
主机类查找原/改/回滚退出码1/0/1；旧版查找保留，新版及独立Tinker类身份通过。

用户授权部署后，仅原子替换活跃模块classes.dex并重启微信，保留原生SO、service.sh
与module.prop；设备显示的模块版本仍为旧0.5-auto，不能据此认为DEX未更新。
新DEX SHA256 f12c0d2cbedf650023866ba2d76545e63d546691c992d6771c28e9551e77bf15。
保留原生SO SHA256 fa3e156b5a01dcd84a6881c1a16867a9b1f2f124de85cc36bc44abcbd268cd32。

实时日志确认LSPLANT_INIT_OK、基础包/Tinker两次WECHAT_HOOKS_READY(class=bf5.f)，
CACHES_SYNCHRONIZED count=3 dpi=300早于onCreate。SM-F9560/samsung身份保留，
wm physical density保持300；当前自由窗口列表截图中头像/行高、搜索/加号及底栏
图标文字完整。首张截图为原设备休眠黑屏；唤醒屏幕后才作上述视觉检查。

boot ID、system_server、SurfaceFlinger均未改变。未清除聊天/热更新数据，未重启系统。
未复测所有聊天页、全部窗口尺寸、长时或完整系统重启；新构建SO和0.6完整ZIP仍只作
构建候选，不宣称已部署整包。APK、截图和原始日志仅在ignored本地证据目录保存。
