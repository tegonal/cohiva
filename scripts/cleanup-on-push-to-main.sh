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

if ! [[ -v scriptsDir ]]; then
	scriptsDir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" >/dev/null && pwd 2>/dev/null)"
	readonly scriptsDir
fi

if ! [[ -v projectDir ]]; then
	projectDir="$(realpath "$scriptsDir/../")"
	readonly projectDir
fi

if ! [[ -v dir_of_tegonal_scripts ]]; then
	dir_of_tegonal_scripts="$scriptsDir/../lib/tegonal-scripts/src"
	source "$dir_of_tegonal_scripts/setup.sh" "$dir_of_tegonal_scripts"
fi

sourceOnce "$dir_of_tegonal_scripts/utility/log.sh"

function cleanupOnPushToMain() {
	logSuccess "nothing to cleanup yet"
}

${__SOURCED__:+return}
cleanupOnPushToMain "$@"
