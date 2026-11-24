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
shopt -s inherit_errexit
unset CDPATH

if ! [[ -v scriptsDir ]]; then
	scriptsDir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" >/dev/null && pwd 2>/dev/null)"
	readonly scriptsDir
fi
source "$scriptsDir/dirs.source.sh"
sourceOnce "$scriptsDir/check-help-callable.sh"
sourceOnce "$scriptsDir/cleanup-on-push-to-main.sh"
sourceOnce "$scriptsDir/run-shellcheck.sh"

function checkPython() {
	(
		cd "$projectDir"
		ruff check --ignore D
	)
}

function checkPWA() {
	if [[ "$SKIP_PWA" != "false" && "$SKIP_PWA" != "0" ]]; then
		return
	fi
	(
		cd "$projectDir/pwa"
		yarn build || die "yarn build failed"
		yarn lint || die "yarn lint failed"
		yarn prettier || die "prettier failed"
	)
}

function beforePr() {
	# using && because this function might be used on the left side of an ||
	customRunShellcheck &&
		cleanupOnPushToMain &&
		checkPython &&
		checkPWA &&
		customCheckHelpCallable
}

${__SOURCED__:+return}
beforePr "$@"
