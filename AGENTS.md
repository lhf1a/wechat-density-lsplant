# Working agreement

- Read README.md and VALIDATION.md first. This repository is independent of the Surface OS port.
- Preserve the current user0/user10 main-process filter and current-boot authorization. VersionCode gating was removed in 0.5; do not reintroduce the historical user10/versionCode3200-only restriction.
- The user authorized automatic startup on 2026-11-01: wechat-auto with deadline0 lasts for the current boot; manual wechat/probe modes retain expiration. Keep startup one-shot, without a renewal worker.
- Preserve the Z Fold6 identity supplied by the existing Device Faker module; do not change global density or app data.
- Keep the hook before Application creation and synchronize the cached density fields. Late getter-only variants failed visual testing.
- Preserve DelegateLastClassLoader constructor handling: Tinker can define a replacement jf5.f (8.0.79) or bf5.f (8.0.80). Install on that class before its density constructor executes; onCreate-only reinstallation still clips icons.
- Building must not install or reboot the device. Deployment and reboot were separately authorized in the device-cleanup task; report actual device verification independently of build checks.
- Keep original APKs, screenshots, chat content, credentials and raw device logs outside Git.
- artifacts/2026-11-01-validated contains the exact device-tested bytes. Never overwrite it with a rebuild. New builds go to ignored build/.
- Rebuilt native binaries may differ because of source paths/debug metadata. Do not claim device verification for a rebuilt binary without testing it.
- Preserve the existing device screen-only suspend guard and rescue entry during any separately authorized device work.
