#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo_root=$(cd -- "${script_dir}/.." && pwd)
asset_name="${ASSET_NAME:-I18nUpdateMod-3.7.0-hmclfix1-all.jar}"
output_dir="${OUTPUT_DIR:-${repo_root}/dist}"
upstream_repo="${UPSTREAM_REPO:-https://github.com/CFPAOrg/I18nUpdateMod3.git}"
upstream_ref="${UPSTREAM_REF:-v3.7.0}"
patch_path="${repo_root}/patches/i18nupdatemod-3.7.0-hmclfix1.patch"

cleanup_work_root=0
if [ -n "${WORK_ROOT:-}" ]; then
  work_root="${WORK_ROOT}"
else
  work_root=$(mktemp -d)
  cleanup_work_root=1
fi

cleanup() {
  if [ "${cleanup_work_root}" -eq 1 ]; then
    rm -rf "${work_root}"
  fi
}
trap cleanup EXIT

build_dir="${work_root}/I18nUpdateMod3"
rm -rf "${build_dir}"

git clone --depth 1 --branch "${upstream_ref}" "${upstream_repo}" "${build_dir}"
git -C "${build_dir}" apply "${patch_path}"

(
  cd "${build_dir}"
  IS_SNAPSHOT=false ./gradlew --no-daemon shadowJar
)

mkdir -p "${output_dir}"
repack_dir="${work_root}/repack"
rm -rf "${repack_dir}"
mkdir -p "${repack_dir}"
(
  cd "${repack_dir}"
  jar xf "${build_dir}/build/libs/I18nUpdateMod-3.7.0-all.jar"
)

python3 - "${repack_dir}" "${output_dir}/${asset_name}" <<'PY'
import sys
import zipfile
from pathlib import Path

root = Path(sys.argv[1])
output = Path(sys.argv[2])
fixed_dt = (2020, 1, 1, 0, 0, 0)

files = sorted(path for path in root.rglob("*") if path.is_file())

with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for path in files:
        rel = path.relative_to(root).as_posix()
        info = zipfile.ZipInfo(rel, fixed_dt)
        info.create_system = 3
        info.external_attr = 0o100644 << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(info, path.read_bytes())
PY

(
  cd "${output_dir}"
  sha256sum "${asset_name}" > "${asset_name}.sha256"
  sha512sum "${asset_name}" > "${asset_name}.sha512"
)

printf 'Built %s\n' "${output_dir}/${asset_name}"
printf 'sha256=%s\n' "$(cut -d' ' -f1 "${output_dir}/${asset_name}.sha256")"
printf 'sha512=%s\n' "$(cut -d' ' -f1 "${output_dir}/${asset_name}.sha512")"
