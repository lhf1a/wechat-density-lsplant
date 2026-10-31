# Working agreement

- Read README.md and VALIDATION.md first. This repository is independent of the Surface OS port.
- Preserve the exact user10/main-process filter, versionCode3200 check, and boot-bound expiring gate.
- Preserve the Z Fold6 identity supplied by the existing Device Faker module; do not change global density or app data.
- Keep the hook before Application creation and synchronize the cached density fields. Late getter-only variants failed visual testing.
- Do not auto-install, auto-reboot, or add persistent injection while building. Current artifacts are a manually gated lab experiment.
- Keep original APKs, screenshots, chat content, credentials and raw device logs outside Git.
- artifacts/2026-11-01-validated contains the exact device-tested bytes. Never overwrite it with a rebuild. New builds go to ignored build/.
- Rebuilt native binaries may differ because of source paths/debug metadata. Do not claim device verification for a rebuilt binary without testing it.
- Preserve the existing device screen-only suspend guard and rescue entry during any separately authorized device work.
