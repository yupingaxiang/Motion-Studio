#!/usr/bin/env bash
# Author: Codex | Created: 2026-11-24 21:27:52 +08:00 | Switch images after upload and restore the previous healthy release on failure.
set -euo pipefail
version=${1:?Commit SHA required}
[[ $version =~ ^[0-9a-f]{40}$ ]] || exit 2
cd "$HOME/motion-studio-deploy"
image="motion-studio:$version"
active="$(docker inspect --format '{{.Config.Image}}' motion-studio-workbench-1 2>/dev/null || true)"

# Start one image and wait until Compose reports it healthy.
activate() {
  MOTION_STUDIO_IMAGE="$1" docker compose -p motion-studio -f "compose.$2.yaml" up -d --pull never --wait --wait-timeout 60
}

old_version=${active#motion-studio:}
if activate "$image" "$version"; then
  # Keep current and previous images for rollback without accumulating releases on a small disk.
  while IFS= read -r tag; do
    [[ $tag =~ ^[0-9a-f]{40}$ && $tag != "$version" && $tag != "$old_version" ]] || continue
    docker image rm "motion-studio:$tag" >/dev/null || true
  done < <(docker image ls motion-studio --format '{{.Tag}}')
else
  if [[ $old_version =~ ^[0-9a-f]{40}$ && -f compose.$old_version.yaml ]]; then
    activate "$active" "$old_version" || true
  else
    MOTION_STUDIO_IMAGE="$image" docker compose -p motion-studio -f "compose.$version.yaml" stop workbench || true
  fi
  exit 1
fi
