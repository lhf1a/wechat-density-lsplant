# 2026-11-01 清理与自动启用部署

用户授权清理此前工作设备上的实验应用/模块，并替换为独立产出；随后明确要求
开机自动生效，并要求去掉续期开关方式。

已完成清理：DPIS（io.github.kwensiu.dpis）与身份探针
（local.surface.identityprobe）卸载成功。Vector及其modules_update、lspd目录
检查均不存在。设备仅保留生产所需Device Faker、Zygisk Next及本密度模块。
旧Vector/DPIS安装包、多版测试DEX、旧模块ZIP、诊断截图目录和本轮安装暂存文件
已按明确文件列表备份后清理。较早的其它图形实验截图不属于本次微信实验，保留。

清理前备份仅保存在忽略的private/cleanup-20261101，SHA256为
74e1a04f83181600d6cf95283764d1c41d093c90b0c35dee247d6eb75f538cef。
微信/QQ数据、机型伪装配置和root基础模块均保留，配置哈希仍162bfeb3…。

0.2过渡包沿用实测原生库/DEX，以service后台续期门禁；已通过ksud安装更新并启用，
随后执行一次重启。网络稍后恢复，boot9637fd0c…、Android完成启动，Next实际登记
2个模块且errors0。旧续期进程已在安装0.3之前通过卸载脚本停止。
用户在重启期间要求去掉续期，因此0.2不是最终交付方案。

0.3-auto：service.sh仅写入一次本boot的wechat-auto授权，deadline0明确
表示持续授权；原生层仍严格检查boot ID、微信主进程和模块disable/remove标记。
手动wechat/probe模式保留到期判断。没有续期worker或timer。

本地检查已通过：一次性service脚本结束、权限600、disable/remove跳过、卸载清理，
以及12项实际原生gate_policy.h用例。独立构建完成，DEX与原实测版本相同。
0.3包SHA256：7f3e2e8f1404f77ffba89e2c58f69860ca536e941ae6a1bb1b81956eecde1710。
0.3 SO：b480177e5ca923e2cdb0ea8396dd41b564d19f08a7614947c49acb0000fb4292。
0.3已通过重启（boot2399ad79…），开关自动创建为本boot/0/wechat-auto，状态目录
只有gate，无auto.pid或续期service进程。设备启动后先为user0，切换回user10才可
启动微信；没有清除用户数据。初次Activity不存在错误是用户未启动，不是APK丢失。

应用冷启动发现微信启用了Tinker patch-7b34e800，使用DelegateLastClassLoader的
新jf5.f，旧APK类Hook未生效。数值修正也不能代替排版检查。0.3视觉验收失败，
不作为最终交付；原始0.3归档标为失败对照。
曾执行cmd package compile -m verify排除AOT，未解决，已执行compile --reset恢复。

0.4修正：在DelegateLastClassLoader构造后安装该加载器内的密度类Hook，保留
Application创建前和返回后的核验。已在当前实际Tinker补丁上看到类身份变化、
构造器CACHES_SYNCHRONIZED count3/dpi300发生于onCreate之前，头像比例、搜索/
加号和底栏恢复完整。仅在onCreate重装或补同步缓存的中间试验仍有裁切，已淘汰。
截图和日志仅保存在忽略private/cleanup-20261101。

0.4包ddbd9d41…，SO保持b480177e…，DEX35f144f6…；完整包已安装并请求重启。
最终完整包重启通过：boot1edf27d4-8608-4442-9bdb-2f5307a05eb2，Android完成
启动且用户确认桌面；模块0.4-auto enabled、update=false，Next实际登记
device_faker/sq2_density_test、errors0。开关自动创建为本boot/0/wechat-auto，
状态目录仅gate，未发现service续期进程。

重启后的微信冷启动PID21840，日志确认Tinker类切换、3份缓存同步300dpi发生在
onCreate前，实际资源Configuration300dpi；SM-F9560/samsung保留。截图确认列表
头像、搜索/加号、底栏图标及文字完整。SO/DEX/service与0.4归档哈希完全匹配。
此次只复核列表，未重复所有聊天页、窗口尺寸、手机共存或长期稳定性测试。
设备旧安装包、DEX及本轮日志/截图暂存均已清除，私有备份留在本机忽略目录。
微信登录数据保留；正常网络由Android管理，未更改内核/启动入口或实际睡眠保护。
