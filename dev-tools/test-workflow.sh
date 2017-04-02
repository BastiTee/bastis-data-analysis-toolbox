#!/bin/bash

# prepare execution environment
cd "$( dirname "$( dirname "$( readlink -f $0 )" )" )"
source "dev-tools/base.sh"
PY=$( get_python_com )
[ -z $PY ] && { echo "Python not installed."; exit 1; }

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
http://www.spiegel.de/index.rss
http://www.tagesschau.de/xml/rss2
http://www.faz.net/rss/aktuell
EOF

$PY -m bdatbx_test.test_suite
run_pfx="$PY -m bdatbx_scripts"
${run_pfx}.parse_rss_feed -i "${workdir}/00-rss-feeds.txt" -o ${feeds}
${run_pfx}.download_website -i ${feeds} -o ${html}
${run_pfx}.extract_raw_text_from_website -i ${html} -o ${rawtext}
${run_pfx}.tokenize_raw_text -i ${rawtext} -o ${tokens} -n nltk-data
${run_pfx}.generate_topic_models -i ${tokens} -o ${topics}

[ $temp_only == 1 ] && {
  rm -rf $workdir
  echo "Deleted $workdir"
}
