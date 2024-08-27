#!/usr/bin/env bash
#
#    __                          __
#   / /____ ___ ____  ___  ___ _/ /       This file is provided to you by https://github.com/tegonal/oss-template
#  / __/ -_) _ `/ _ \/ _ \/ _ `/ /        Copyright 2024 Tegonal Genossenschaft
#  \__/\__/\_, /\___/_//_/\_,_/_/         It is licensed under Creative Commons Zero v1.0 Universal
#         /___/                           Please report bugs and contribute back your improvements
#
#                                         Version: v0.1.0-SNAPSHOT
###################################
set -euo pipefail
shopt -s inherit_errexit
unset CDPATH

projectDir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" >/dev/null && pwd 2>/dev/null)"
readonly projectDir

if ! [[ -v dir_of_tegonal_scripts ]]; then
	dir_of_tegonal_scripts="$projectDir/lib/tegonal-scripts/src"
	source "$dir_of_tegonal_scripts/setup.sh" "$dir_of_tegonal_scripts"
fi
sourceOnce "$dir_of_tegonal_scripts/utility/log.sh"

defaultOrgNameGithub="tegonal"
printf "Please insert the github organisation name (default %s): " "$defaultOrgNameGithub"
read -r orgNameGithub
if [[ -z "$orgNameGithub" ]]; then
	orgNameGithub="$defaultOrgNameGithub"
fi

if [[ "$orgNameGithub" == "$defaultOrgNameGithub" ]]; then
	orgName="Tegonal Genossenschaft"
	orgEmail="info@tegonal.com"
else
	printf "Please insert the organisation name: "
	read -r orgName
	if [[ -z ${orgName// /} ]]; then
		die "organisation name was empty or blank"
	fi

	printf "Please insert the organisation email: "
	read -r orgEmail
	if [[ -z ${orgEmail// /} ]]; then
		die "organisation email was empty or blank"
	fi
fi

printf "Please insert the project name: "
read -r projectName
if [[ -z ${projectName// /} ]]; then
	die "project name was empty or blank"
fi
tmpName="${projectName//-/_}"
projectNameUpper="${tmpName^^}"
tmpName="${projectName// /-}"
defaultProjectNameGithub="${tmpName,,}"

printf "Please insert the github project name (default %s): " "${defaultProjectNameGithub}"
read -r projectNameGithub
if [[ -z "$projectNameGithub" ]]; then
	projectNameGithub="${defaultProjectNameGithub}"
fi

printf "Please choose your license:\n(1) EUPL 1.2\n(2) AGPL 3\n(3) GPL 3\n(4) Apache 2.0\n(5) MIT\n(6) CC0 1.0 Universal\nYour selection (default (1) EUPL 1.2): "
read -r choice

if [[ -z "$choice" ]]; then
	choice=1
fi

if ! [[ "$choice" =~ ^[1-6]+$ ]]; then
	die "the selection %s is invalid, enter a number between 1 and 4" "$choice"
elif [[ choice -eq 1 ]]; then
	licenseUrl="https://joinup.ec.europa.eu/collection/eupl/eupl-text-11-12"
	licenseShortName="EUPL 1.2"
	licenseFullName="European Union Public Licence v. 1.2"
	cp "$projectDir/EUPL.LICENSE.txt" "$projectDir/LICENSE.txt"
elif [[ choice -eq 2 ]]; then
	licenseUrl="https://www.gnu.org/licenses/agpl-3.0.en.html"
	licenseShortName="AGPL 3"
	licenseFullName="GNU Affero General Public License v3"
	cp "$projectDir/AGPL.LICENSE.txt" "$projectDir/LICENSE.txt"
elif [[ choice -eq 3 ]]; then
	licenseUrl="https://www.gnu.org/licenses/gpl-3.0.html"
	licenseShortName="GPL 3.0"
	licenseFullName="GNU General Public License v3"
	cp "$projectDir/GPL.LICENSE.txt" "$projectDir/LICENSE.txt"
elif [[ choice -eq 4 ]]; then
	licenseUrl="https://www.apache.org/licenses/LICENSE-2.0"
	licenseShortName="Apache 2.0"
	licenseFullName="Apache License, Version 2.0"
	cp "$projectDir/Apache.LICENSE.txt" "$projectDir/LICENSE.txt"
elif [[ choice -eq 5 ]]; then
	licenseUrl="https://www.apache.org/licenses/LICENSE-2.0"
	licenseShortName="MIT"
	licenseFullName="MIT License"
	cp "$projectDir/MIT.LICENSE.txt" "$projectDir/LICENSE.txt"
elif [[ choice -eq 6 ]]; then
	licenseUrl="https://creativecommons.org/publicdomain/zero/1.0/"
	licenseShortName="CC0 1.0"
	licenseFullName="Creative Commons Zero v1.0 Universal"
	cp "$projectDir/CC0.LICENSE.txt" "$projectDir/LICENSE.txt"
fi

defaultInitialYear="$(date +%Y)"
printf "Please insert the year in which the project started (default %s):" "$defaultInitialYear"
read -r initialYear
if [[ -z "$initialYear" ]]; then
	initialYear="$defaultInitialYear"
fi

if [[ "$orgNameGithub" == "$defaultOrgNameGithub" ]]; then
	mv "$projectDir/.gt/remotes/tegonal-gh-commons/pull-hook_tegonal.sh" "$projectDir/.gt/remotes/tegonal-gh-commons/pull-hook.sh"
	rm "$projectDir/.gt/remotes/tegonal-gh-commons/pull-hook_other.sh"
	rm "$projectDir/.gt/remotes/gt/pull-hook_other.sh"
else
	mv "$projectDir/.gt/remotes/tegonal-gh-commons/pull-hook_other.sh" "$projectDir/.gt/remotes/tegonal-gh-commons/pull-hook.sh"
	rm "$projectDir/.gt/remotes/tegonal-gh-commons/pull-hook_tegonal.sh"

	rm "$projectDir/lib/tegonal-gh-commons/src/gt/tegonal.data.source.sh"
	head -n -1 <"$projectDir/.gt/remotes/tegonal-gh-commons/pulled.tsv" >"$projectDir/.gt/remotes/tegonal-gh-commons/pulled.tsv.tmp"
	mv "$projectDir/.gt/remotes/tegonal-gh-commons/pulled.tsv.tmp" "$projectDir/.gt/remotes/tegonal-gh-commons/pulled.tsv"

	mv "$projectDir/.gt/remotes/gt/pull-hook_other.sh" "$projectDir/.gt/remotes/gt/pull-hook.sh"
	perl -0777 -i -pe "s@(github.repository_owner\s*==\s*)'tegonal'@\${1}'$orgNameGithub'@" "$projectDir/.github/workflows/gt-update.yml"

	# remove the tegonal header
	find "$projectDir/scripts" "$projectDir/.gt/remotes/" -type f -name "*.sh" -print0 |
		while read -r -d $'\0' file; do
			perl -0777 -i \
				-pe "s@#    __                          __\n@#@;" \
				-pe "s@#.*(This script is provided to you by|Copyright YEAR ORG_NAME <ORG_EMAIL>|It is licensed under LICENSE_FULL_NAME|Please report bugs and contribute back your improvements)@#  \${1}@g;" \
				"$file"
		done
fi

licenseBadge="[![$licenseShortName](https://img.shields.io/badge/%E2%9A%96-${licenseShortName// /%220}-%230b45a6)]($licenseUrl \"License\")"
licenseLink="[$licenseFullName]($licenseUrl)"

find "$projectDir" -type f \
	-not -path "$projectDir/lib/**" \
	-not -name "init.sh" \
	-not -name "cleanup.yml" \
	-not -name "gt-update.yml" \
	-not -name "*LICENSE.txt" \
	\( -name "*.md" -o -name "*.txt" -o -name "*.yaml" -o -name "*.yml" -o -name "*.sh" \) \
	-print0 |
	while read -r -d $'\0' file; do
		PROJECT_NAME_GITHUB="$projectNameGithub" \
			PROJECT_NAME_UPPER="${projectNameUpper}" \
			PROJECT_NAME="$projectName" \
			ORG_NAME_GITHUB="$orgNameGithub" \
			ORG_NAME="$orgName" \
			ORG_EMAIL="$orgEmail" \
			LICENSE_BADGE="$licenseBadge" \
			LICENSE_LINK="$licenseLink" \
			LICENSE_FULL_NAME="$licenseFullName" \
			GITHUB_URL="https://github.com/$orgNameGithub/$projectNameGithub" \
			YEAR="$initialYear" \
			perl -0777 -i \
			-pe "s@<PROJECT_NAME_GITHUB>@\$ENV{PROJECT_NAME_GITHUB}@g;" \
			-pe "s@PROJECT_NAME_GITHUB@\$ENV{PROJECT_NAME_GITHUB}@g;" \
			-pe "s@PROJECT_NAME_UPPER@\$ENV{PROJECT_NAME_UPPER}@g;" \
			-pe "s@<PROJECT_NAME>@\$ENV{PROJECT_NAME}@g;" \
			-pe "s@PROJECT_NAME@\$ENV{PROJECT_NAME}@g;" \
			-pe "s@ORG_NAME_GITHUB@\$ENV{ORG_NAME_GITHUB}@g;" \
			-pe "s@ORG_NAME@\$ENV{ORG_NAME}@g;" \
			-pe "s@<OWNER>@\$ENV{ORG_NAME}@g;" \
			-pe "s@<OWNER_GITHUB>@\$ENV{ORG_NAME_GITHUB}@g;" \
			-pe "s@ORG_EMAIL@\$ENV{ORG_EMAIL}@g;" \
			-pe "s@<OWNER_EMAIL>@\$ENV{ORG_EMAIL}@g;" \
			-pe "s@LICENSE_BADGE@\$ENV{LICENSE_BADGE}@g;" \
			-pe "s@LICENSE_LINK@\$ENV{LICENSE_LINK}@g;" \
			-pe "s@LICENSE_FULL_NAME@\$ENV{LICENSE_FULL_NAME}@g;" \
			-pe "s@<GITHUB_URL>@\$ENV{GITHUB_URL}@g;" \
			-pe "s@YEAR@\$ENV{YEAR}@g;" \
			-pe "s@<TAG>@main@g;" \
			"$file"
	done

if [[ choice -eq 5 ]]; then
	untilYear="$defaultInitialYear"
	yearText="${initialYear}-${untilYear}"
	if [[ "$untilYear" == "$initialYear" ]]; then
		yearText="${initialYear}"
	fi
	YEAR="$yearText" \
		ORG_NAME="$orgName" \
		perl -0777 -i \
		-pe "s@\[year\]@\$ENV{YEAR}@g;" \
		-e "s@\[fullname\]@\$ENV{ORG_NAME}@g;" \
		"$projectDir/LICENSE.txt"
fi

find "$projectDir" -maxdepth 1 -name "*.LICENSE.txt" -print0 |
	while read -r -d $'\0' license; do
		rm "$license"
	done

logSuccess "initialised the repository, please follow the remaining steps in README.md"

rm "$projectDir/init.sh"
