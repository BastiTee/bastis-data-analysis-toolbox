#!/bin/sh
set -e  # Always exit on non-zero return codes
cd "$( cd "$( dirname "$0" )"; pwd )"

# Check python and pipenv installation
[ -z "$( command -v python3 )" ] && { echo "python3 not available."; exit 1; }
[ -z "$( command -v pipenv )" ] && { echo "pipenv not available."; exit 1; }

# Suppress warning if pipenv is started inside .venv
export PIPENV_VERBOSITY=${PIPENV_VERBOSITY:--1}
# Use relative .venv folder instead of home-folder based
export PIPENV_VENV_IN_PROJECT=${PIPENV_VENV_IN_PROJECT:-1}
# Ignore existing venvs (required for travis)
export PIPENV_IGNORE_VIRTUALENVS=${PIPENV_IGNORE_VIRTUALENVS:-1}
# Setup python path
export PYTHONPATH=${PYTHONPATH:-.}
# Make sure we are running with an explicit encoding
export LC_ALL=${PYPE_ENCODING:-${LC_ALL}}
export LANG=${PYPE_ENCODING:--${LANG}}

venv() {
    # Create a pipenv virtual environment for IDE/coding support
    rm -rf .venv $PYPE_CONFIG_FOLDER
	pipenv install --dev --skip-lock
    pipenv run pip install --editable .
    nltk_install
}

nltk_install() {
    # Install nltk packages
    [ ! -d .venv ] && venv
    for module in averaged_perceptron_tagger stopwords punkt; do
        pipenv run python -c \
        "import nltk; nltk.download('$module', download_dir='nltk-data');"
    done
}

shell() {
    # Open virtual environment with forced bash shell (required for venv)
    [ ! -d .venv ] && venv
    bash -c "pipenv shell; $SHELL"
}

clean() {
    # Clean project base by deleting any non-VC files
    rm -rf .venv build dist .ropeproject nltk-data .pytest_cache \
    *.egg-info _test
}

test() {
    # Run all tests in default virtualenv
    workdir="_test"
    rm -rf $workdir && mkdir -p $workdir

    # setup files and folders
    feeds="${workdir}/00-feeds"
    html="${workdir}/01-html"
    rawtext="${workdir}/02-raw-text"
    tokens="${workdir}/03-tokens"
    tstats="${workdir}/04-text-stats"
    topics="${workdir}/05-topic-models"
    mkdir -p ${feeds} ${html} ${rawtext} ${tokens} ${tstats} ${topics}
    cat << EOF > "${workdir}/00-rss-feeds.txt"
    http://www.faz.net/rss/aktuell/
EOF

    # setup mongodb
    python -c "\
from robota import r_mongo; \
col = r_mongo.get_client_for_collection('robota-test', True); \
r_mongo.clear_collection(col); \
"

    echo "Working dir is: $workdir"
    run_pfx="python -m robota_scripts"

    ${run_pfx}.parse_rss_feed -i "${workdir}/00-rss-feeds.txt" -o ${feeds}
    ${run_pfx}.download_website -i ${feeds} -o ${html}
    ${run_pfx}.extract_pubdate_from_html -i ${html} -o ${workdir}/pubdates.txt
    ${run_pfx}.extract_raw_text_from_website -i ${html} -o ${rawtext}
    ${run_pfx}.detect_language -i ${rawtext} -o ${rawtext}/lang.txt
    ${run_pfx}.tokenize_raw_text -i ${rawtext} -o ${tokens} -n nltk-data
    ${run_pfx}.get_keywords -i ${rawtext} -n nltk-data
    ${run_pfx}.generate_topic_models -i ${tokens} -o ${topics}
}

lint() {
    # Run linter / code formatting checks against source code base
    pipenv run flake8 pype example_pypes tests
}

# -----------------------------------------------------------------------------
internal_print_commands() {
    echo "$1\n"
    {   # All functions except prefixed "internal_"  are considered targets
        cat make 2>/dev/null
    } | egrep -e "^[a-zA-Z_]+\(\)" | egrep -ve "^internal" |\
    tr "(" " " | awk '{print $1}' | sort
    echo
}
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    internal_print_commands "Available:"
    exit 0
fi
if [ $# = 0 ]; then
    internal_print_commands "No command selected. Available:"
    exit 1
fi
# Execute the provided command line
$@
