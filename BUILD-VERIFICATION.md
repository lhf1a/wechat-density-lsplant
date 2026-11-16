# 独立构建检查

2026-11-01，在本仓库全新 build/ 目录中，从随仓库保存的依赖归档展开源码，
校验各归档 SHA256，应用 LSPlant 编译补丁，完成132项原生编译/链接、javac、
D8 和模块 ZIP 打包。未读取原项目的源码、依赖展开目录或 CMake 缓存。

- NDK r28c / 28.2.13676358，Clang19.0.1，API35 android.jar。
- 新 DEX：591d608519e3b77522b904b3cb1e8ba15622f2c4fb626ec1efeba84e6f09aced，与实机载荷一致。
- 新 SO：07b65cddb936e95d3da5503350244cd2945dee3bb5560c7c28ea339ad328a03d。
- 新 ZIP：957aad6c32c817b95c5f06dbc96d449bbf87c84fcb400111a81841e08d0df7f7。

新 SO/ZIP 保存在忽略的 build/，构建审计为 build/build-audit.json。
原生库包含源路径/调试元数据，源路径改变后哈希不同；没有据此宣称与原库逐字节
一致，也未将新库部署到设备。实机确认的原 ZIP/SO/DEX 已另外原样保存在
artifacts/2026-11-01-validated，并由 SHA256SUMS 和 manifest.json 记录。

## 2026-11-16：0.6-auto

在子仓库独立build/完成132项原生编译/链接、Java/D8与ZIP打包，NDK r28c、API35。
- ZIP SHA256：f5bc2672987a8731d2bb75f3e47cd99a6e7e095eca3250b4a2efd40c8c3d64fb。
- DEX SHA256：f12c0d2cbedf650023866ba2d76545e63d546691c992d6771c28e9551e77bf15，与本轮已部署DEX逐字节一致。
- 新SO SHA256：17088bf4ab3254dafffdd24978cd341c7b5f7fd57e778b5e13854e2c64d1f97e，未替换设备原生库。
- 类加载器回归、一次性service/授权门禁与三组历史归档/六组依赖完整性检查通过。

ZIP内version=0.6-auto、versionCode=6；产物仍保存在ignored build/，未覆盖历史归档。
完整新ZIP/新SO没有系统重启验收；实际设备验证限于替换DEX后的微信冷启动和当前列表界面。
