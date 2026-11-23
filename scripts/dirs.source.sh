#!/usr/bin/env bash
# shellcheck disable=SC2034,SC2168,SC2154
#
#    __                          __
#   / /____ ___ ____  ___  ___ _/ /       This script is provided to you by https://github.com/tegonal/cohiva
#  / __/ -_) _ `/ _ \/ _ \/ _ `/ /        Copyright 2024 Tegonal Genossenschaft <info@tegonal.com>
#  \__/\__/\_, /\___/_//_/\_,_/_/         It is licensed under GNU Affero General Public License v3
#         /___/                           Please report bugs and contribute back your improvements
#
#                                         Version: v1.6.0-SNAPSHOT
###################################

if ! [[ -v projectDir ]]; then
	projectDir="$(realpath "$scriptsDir/../")"
	readonly projectDir
fi

if ! [[ -v dir_of_tegonal_scripts ]]; then
	dir_of_tegonal_scripts="$projectDir/lib/tegonal-scripts/src"
	source "$dir_of_tegonal_scripts/setup_tegonal_scripts.sh" "$dir_of_tegonal_scripts"
fi


if ! [[ -v dir_of_github_commons ]]; then
	dir_of_github_commons="$projectDir/lib/tegonal-gh-commons/src"
	readonly dir_of_github_commons
fi

if ! [[ -v SKIP_PWA ]]; then
	SKIP_PWA="false"
	readonly SKIP_PWA
fi
