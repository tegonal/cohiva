#!/usr/bin/env bash
#
#    __                          __
#   / /____ ___ ____  ___  ___ _/ /       This script is provided to you by https://github.com/ORG_NAME_GITHUB/PROJECT_NAME_GITHUB
#  / __/ -_) _ `/ _ \/ _ \/ _ `/ /        Copyright YEAR ORG_NAME <ORG_EMAIL>
#  \__/\__/\_, /\___/_//_/\_,_/_/         It is licensed under LICENSE_FULL_NAME
#         /___/                           Please report bugs and contribute back your improvements
#
#                                         Version: v0.1.0-SNAPSHOT
###################################
set -euo pipefail
shopt -s inherit_errexit
unset CDPATH
PROJECT_NAME_UPPER_LATEST_VERSION="main"

if ! [[ -v dir_of_tegonal_scripts ]]; then
	dir_of_tegonal_scripts="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" >/dev/null && pwd 2>/dev/null)/../../../lib/tegonal-scripts/src"
	source "$dir_of_tegonal_scripts/setup.sh" "$dir_of_tegonal_scripts"
fi

if ! [[ -v dir_of_github_commons ]]; then
	dir_of_github_commons="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" >/dev/null && pwd 2>/dev/null)/../../../lib/tegonal-gh-commons/src"
	readonly dir_of_github_commons
fi

sourceOnce "$dir_of_github_commons/gt/pull-hook-functions.sh"
sourceOnce "$dir_of_tegonal_scripts/utility/parse-fn-args.sh"

function gt_pullHook_gt_before() {
  local -r _tag=$1 source=$2 _target=$3

  if [[ $source =~ .*/.github/workflows/gt-update.yml ]]; then
    perl -0777 -i -pe "s/(if: github.repository_owner == )'tegonal'/\${1}'ORG_NAME_GITHUB'/" "$source"
  fi
}

function gt_pullHook_gt_after(){
  # no op, nothing to do
  true
}
