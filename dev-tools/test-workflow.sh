#!/bin/bash

# change to root of bdatbx
cd "$( dirname "$( dirname "$( readlink -f $0 )" )" )"
# extend python path with a local bptbx version
export PYTHONPATH=${PYTHONPATH}:../bastis-python-toolbox

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
EOF
# http://www.faz.net/rss/aktuell
# http://www.tagesschau.de/xml/rss2
# http://www.stern.de/feed/standard/all/
# http://rssfeed.sueddeutsche.de/c/795/f/449002/index.rss
# http://www.bild.de/rss-feeds/rss-16725492,feed=home.bild.html
# http://www.taz.de/rss.xml
# https://www.welt.de/feeds/latest.rss
# http://rss.focus.de/politik/
# http://www.n-tv.de/rss
# http://newsfeed.zeit.de/index
# http://www.handelsblatt.com/contentexport/feed/top-themen/

python3 -m bdatbx_test.admin_test_library
run_pfx="python3 -m bdatbx_scripts"
${run_pfx}.parse_rss_feed -i "${workdir}/00-rss-feeds.txt" -o ${feeds}
${run_pfx}.download_website -i ${feeds} -o ${html}
${run_pfx}.extract_raw_text_from_website -i ${html} -o ${rawtext}
${run_pfx}.tokenize_raw_text -i ${rawtext} -o ${tokens} -n nltk-data
${run_pfx}.gather_statistics -i ${tokens} -o ${tstats}
${run_pfx}.generate_topic_models -i ${tokens} -o ${topics}

[ $temp_only == 1 ] && {
  rm -rf $workdir
  echo "Deleted $workdir"
}
