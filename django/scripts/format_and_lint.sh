#!/bin/bash
TARGETS=(
    #"credit_accounting/models.py"#
    "."
)

function prompt_yes_no() {
    local text=$1
    local default=$2
    local prompt

    case $default in
        "y"|"Y") answer=1; prompt="${text} [Y/n]" ;;
        "n"|"N") answer=0; prompt="${text} [y/N]" ;;
        *) answer=""; prompt="${text} [y/n]" ;;
    esac
    while :
    do
        echo -n $prompt
        read -n1 IN
        if [ "$IN" == "" -a "$answer" != "" ] ; then
            return
        fi
        case "$IN" in
            "y"|"Y") answer=1; echo ""; return ;;
            "n"|"N") answer=0; echo ""; return ;;
        esac
        echo ""
    done
}

for TARGET in "${TARGETS[@]}" ; do
    ## Formatting
    ruff format --diff $TARGET
    if [ $? != 0 ] ; then
        prompt_yes_no "Apply formatting?" "n"
        if [ "${answer}" == "1" ] ; then
            ruff format $TARGET
        fi
    fi

    ## Linting / checking
    ruff check $TARGET || exit
    ## TODO: Activate pylint checks
    #pylint $TARGET  || exit # more comprehensive checks

    ## Type checks
    #mypy $TARGET

    ## Security checks
    # bandit
    # Bearer -> security scan  github.com/bearer/bearer
done

