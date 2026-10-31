# Dependencies and source availability

The module and build scripts are LGPL-3.0-or-later. LGPL-3.0 and its incorporated
GPL-3.0 text are included under LICENSE and licenses/. Dependency source archives
are bundled under vendor/sources, with upstream revisions and archive SHA256
values in dependencies.json. The LSPlant compiler patch is included separately.
All module sources and build instructions required to rebuild/relink are retained.

| Dependency | Source | License |
| --- | --- | --- |
| LSPlant | https://github.com/JingMatrix/LSPlant | LGPL-3.0-or-later |
| DexBuilder | https://github.com/JingMatrix/DexBuilder | LGPL-3.0-or-later |
| parallel-hashmap | https://github.com/greg7mdp/parallel-hashmap | Apache-2.0 |
| Dobby | https://github.com/JingMatrix/Dobby | Apache-2.0 |
| xDL | https://github.com/hexhacking/xDL | MIT |
| Zygisk public API header | https://github.com/topjohnwu/zygisk-module-sample | ISC |

Each original archive includes its upstream notices. A copy of the Zygisk public
API header's permission notice is in licenses/Zygisk-ISC.txt. No proprietary
WeChat APK or decompiled WeChat source is distributed in this repository.
