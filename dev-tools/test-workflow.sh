#!/bin/bash

# prepare execution environment
cd "$( dirname "$( dirname "$( readlink -f $0 )" )" )"
source "dev-tools/base.sh"
PY=$( get_python_com )
[ -z $PY ] && { echo "Python not installed."; exit 1; }
echo "Running python: $( $PY --version )"
export PYTHONPATH=${PYTHONPATH}:bastis-python-toolbox

[ -z "$1" ] && {
    # create a temporary work directory
    workdir=$( mktemp -d )
    temp_only=1
    } || {
    workdir=$1
    temp_only=0
    rm -rf "$1"
    mkdir -p "$1"
}
[ ! -d "$workdir" ] && {
    echo "Parameter must be an existing working directory."; exit 1;
}

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
python3 -c "\
from robota import r_mongo; \
col = r_mongo.get_client_for_collection('robota-test', True); \
r_mongo.clear_collection(col); \
    "

echo "Working dir is: $workdir"
run_pfx="$PY -m robota_scripts"

$PY -m robota_test.test_suite
[ $? != 0 ] && exit 1

# set -x

${run_pfx}.parse_rss_feed -i "${workdir}/00-rss-feeds.txt" -o ${feeds}
[ $? != 0 ] && exit 1

${run_pfx}.download_website -i ${feeds} -o ${html}
[ $? != 0 ] && exit 1

${run_pfx}.extract_pubdate_from_html -i ${html} -o ${workdir}/pubdates.txt
[ $? != 0 ] && exit 1

${run_pfx}.extract_raw_text_from_website -i ${html} -o ${rawtext}
[ $? != 0 ] && exit 1

${run_pfx}.detect_language -i ${rawtext} -o ${rawtext}/lang.txt
[ $? != 0 ] && exit 1

${run_pfx}.tokenize_raw_text -i ${rawtext} -o ${tokens} -n nltk-data
[ $? != 0 ] && exit 1

${run_pfx}.get_keywords -i ${rawtext} -n nltk-data
[ $? != 0 ] && exit 1

${run_pfx}.generate_topic_models -i ${tokens} -o ${topics}
[ $? != 0 ] && exit 1

[ $temp_only == 1 ] && {
    rm -rf $workdir
    echo "Deleted $workdir"
}
