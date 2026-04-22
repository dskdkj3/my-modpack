#!/usr/bin/env bash
set -euo pipefail

instance_dir="${1:-$HOME/.minecraft/versions/1.0.2}"
timestamp="$(date +%Y%m%d-%H%M%S)"
backup_root="$HOME/.minecraft/.mod-config-backups/${timestamp}-startup-opt-1.0.3"

files=(
  "config/modmenu.json"
  "config/euphoria_patcher/settings.toml"
  "config/xaero/lib/common.cfg"
  "config/xaero/minimap/client.cfg"
  "config/xaero/world-map/client.cfg"
)

for rel in "${files[@]}"; do
  if [ ! -f "$instance_dir/$rel" ]; then
    echo "missing required file: $instance_dir/$rel" >&2
    exit 1
  fi
done

backup_file() {
  local rel="$1"
  mkdir -p "$backup_root/$(dirname "$rel")"
  cp "$instance_dir/$rel" "$backup_root/$rel"
}

backup_file "config/modmenu.json"
sed -i \
  -e 's/"update_checker": true/"update_checker": false/' \
  -e 's/"button_update_badge": true/"button_update_badge": false/' \
  "$instance_dir/config/modmenu.json"

backup_file "config/euphoria_patcher/settings.toml"
sed -i \
  -e 's/doUpdateChecking = "important"/doUpdateChecking = "none"/' \
  "$instance_dir/config/euphoria_patcher/settings.toml"

backup_file "config/xaero/lib/common.cfg"
sed -i \
  -e 's/allow_internet_access = true/allow_internet_access = false/' \
  "$instance_dir/config/xaero/lib/common.cfg"

backup_file "config/xaero/minimap/client.cfg"
sed -i \
  -e 's/update_notifications = true/update_notifications = false/' \
  "$instance_dir/config/xaero/minimap/client.cfg"

backup_file "config/xaero/world-map/client.cfg"
sed -i \
  -e 's/update_notifications = true/update_notifications = false/' \
  "$instance_dir/config/xaero/world-map/client.cfg"

echo "Backups written to: $backup_root"
echo "Updated instance: $instance_dir"
