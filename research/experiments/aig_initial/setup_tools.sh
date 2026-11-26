#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
tools="${AIG_TOOLS_DIR:-$repo/../circuit-tools}"
mkdir -p "$tools"
clone_pinned() {
    local url="$1" path="$2" revision="$3"
    if [[ ! -d "$path/.git" ]]; then
        git clone "$url" "$path"
        git -C "$path" checkout --detach "$revision"
    fi
    [[ "$(git -C "$path" rev-parse HEAD)" == "$revision" ]]
}
clone_pinned https://github.com/berkeley-abc/abc.git "$tools/abc" cd837e9fada8d483b3729569b1b61faa24c5ee5d
clone_pinned https://github.com/lsils/benchmarks.git "$tools/epfl-benchmarks" 82d8cc6910419298e713a46644ed59fd3df53038
make -C "$tools/abc" -j "${AIG_BUILD_JOBS:-8}" ABC_USE_NO_READLINE=1
"$tools/abc/abc" -c "version"
python3 -m unittest discover -s "$repo/research/experiments/aig_initial"
