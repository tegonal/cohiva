#!/usr/bin/env bash
#
#    __                          __
#   / /____ ___ ____  ___  ___ _/ /       This script is provided to you by https://github.com/tegonal/scripts
#  / __/ -_) _ `/ _ \/ _ \/ _ `/ /        Copyright 2022 Tegonal Genossenschaft <info@tegonal.com>
#  \__/\__/\_, /\___/_//_/\_,_/_/         It is licensed under European Union Public License v. 1.2
#         /___/                           Please report bugs and contribute back your improvements
#
#                                         Version: v1.2.1
###################################
set -euo pipefail
shopt -s inherit_errexit
unset CDPATH
COHIVA_VERSION="v1.2.1"

if ! [[ -v scriptsDir ]]; then
	scriptsDir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" >/dev/null && pwd 2>/dev/null)"
	readonly scriptsDir
fi

if ! [[ -v projectDir ]]; then
	projectDir="$(realpath "$scriptsDir/../")"
	readonly projectDir
fi

if ! [[ -v dir_of_github_commons ]]; then
	dir_of_github_commons="$scriptsDir/../lib/tegonal-gh-commons/src"
	readonly dir_of_github_commons
fi

if ! [[ -v dir_of_tegonal_scripts ]]; then
	dir_of_tegonal_scripts="$scriptsDir/../lib/tegonal-scripts/src"
	source "$dir_of_tegonal_scripts/setup.sh" "$dir_of_tegonal_scripts"
fi
sourceOnce "$dir_of_github_commons/gt/pull-hook-functions.sh"
sourceOnce "$dir_of_tegonal_scripts/releasing/release-template.sh"
sourceOnce "$scriptsDir/before-pr.sh"
sourceOnce "$scriptsDir/prepare-next-dev-cycle.sh"

function release() {
	local prepareOnlyParamPatternLong
	source "$dir_of_tegonal_scripts/releasing/common-constants.source.sh" || die "could not source common-constants.source.sh"

	# shellcheck disable=SC2034   # they seem unused but are necessary in order that parseArguments doesn't create global readonly vars
	local version prepareOnly
	# shellcheck disable=SC2034   # they seem unused but are necessary in order that parseArguments doesn't create global readonly vars
	local branch nextVersion
	# shellcheck disable=SC2034   # is passed by name to parseArguments
	local -ra params=(
		version "$versionParamPattern" "$versionParamDocu"
		branch "$branchParamPattern" "$branchParamDocu"
		nextVersion "$nextVersionParamPattern" "$nextVersionParamDocu"
		prepareOnly "$prepareOnlyParamPattern" "$prepareOnlyParamDocu"
	)
	parseArguments params "" "$COHIVA_VERSION" "$@"
	# we don't check if all args are set (and neither set default values) as we currently don't use
	# any param in here but just delegate to releaseTemplate.

	function release_afterVersionHook() {
		local version projectsRootDir additionalPattern
		parseArguments afterVersionHookParams "" "$COHIVA_VERSION" "$@"

		local -r githubUrl="https://github.com/tegonal/cohiva"
		replaceTagInPullRequestTemplate "$projectsRootDir/.github/PULL_REQUEST_TEMPLATE.md" "$githubUrl" "$version" || die "could not fill the placeholders in PULL_REQUEST_TEMPLATE.md"

		local -r versionWithoutLeadingV="${version:1}"

		find ./ -name "*.md" | xargs perl -0777 -i \
			-pe "s@(https://github.com/tegonal/cohiva/(?:tree|blob)/)$branch@\${1}$version@g;"

		perl -0777 -i \
			-pe "s@(__version__ = )\"[^\"]+\"@\${1}\"$versionWithoutLeadingV\"@g;" \
			"$projectsRootDir/django/cohiva/version.py"

		find "$projectsRootDir/pwa" -maxdepth 1 -name "package*.json" | xargs perl -0777 -i \
			-pe "s@(\"version\": )\"[^\"]+\"@\${1}\"$versionWithoutLeadingV\"@g;"
	}

	function release_releaseHook() {
		logInfo "releaseHook: nothing to do."
	}

	# similar as in prepare-next-dev-cycle.sh, you might need to update it there as well if you change something here
	local -r additionalPattern="(COHIVA_(?:LATEST_)?VERSION=['\"])[^'\"]+(['\"])"

	releaseTemplate \
		--project-dir "$projectDir" \
		--pattern "$additionalPattern" \
		"$@" \
		--after-version-update-hook release_afterVersionHook \
		--release-hook release_releaseHook
}

${__SOURCED__:+return}
release "$@"
