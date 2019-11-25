#!/bin/bash
cd "$( cd "$( dirname "$0" )"; pwd )"
set -e

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
