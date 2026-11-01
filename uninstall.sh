#!/system/bin/sh
STATE=/data/adb/sq2-density-test
rm -f "$STATE/gate" "$STATE/gate.new" "$STATE/auto.pid"
rmdir "$STATE" 2>/dev/null
exit 0
