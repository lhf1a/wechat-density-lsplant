#!/system/bin/sh
MODDIR=${0%/*}
STATE=/data/adb/sq2-density-test
BOOT_FILE=/proc/sys/kernel/random/boot_id
[ -f "$MODDIR/disable" ] && exit 0
[ -f "$MODDIR/remove" ] && exit 0
boot=$(cat "$BOOT_FILE") || exit 1
mkdir -p "$STATE" && chmod 700 "$STATE" || exit 1
# One current-boot authorization; no renewal worker or timer.
printf '%s 0 wechat-auto\n' "$boot" > "$STATE/gate.new" || exit 1
chmod 600 "$STATE/gate.new" && mv -f "$STATE/gate.new" "$STATE/gate" || exit 1
rm -f "$STATE/auto.pid"
