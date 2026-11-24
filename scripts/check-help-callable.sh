#!/usr/bin/env bash
#
#    __                          __
#   / /____ ___ ____  ___  ___ _/ /       This script is provided to you by https://github.com/tegonal/cohiva
#  / __/ -_) _ `/ _ \/ _ \/ _ `/ /        Copyright 2024 Tegonal Genossenschaft <info@tegonal.com>
#  \__/\__/\_, /\___/_//_/\_,_/_/         It is licensed under GNU Affero General Public License v3
#         /___/                           Please report bugs and contribute back your improvements
#
#                                         Version: v1.6.0-SNAPSHOT
###################################
set -euo pipefail
shopt -s inherit_errexit || { echo >&2 "please update to bash 5, see errors above" && exit 1; }
unset CDPATH

if ! [[ -v scriptsDir ]]; then
	scriptsDir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" >/dev/null && pwd 2>/dev/null)"
	readonly scriptsDir
fi
source "$scriptsDir/dirs.source.sh"
sourceOnce "$dir_of_tegonal_scripts/qa/check-help-callable.sh"

function customCheckHelpCallable() {

	# shellcheck disable=SC2034   # is passed by name to checkHelpCallable
	local -ra scripts=(
		"$scriptsDir/release.sh"
		"$scriptsDir/prepare-next-dev-cycle.sh"
	)
	checkHelpCallable scripts
}

${__SOURCED__:+return}
customCheckHelpCallable "$@"
