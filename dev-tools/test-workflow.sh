#!/bin/bash

# change to root of bdatbx
cd "$( dirname "$( dirname "$( readlink -f $0 )" )" )"
echo -e "@ $( pwd )\n"

# create a temporary work directory
[ -z "$1" ] && {
    workdir=$( mktemp -d )
    temp_only=1
} || {
    workdir=$1
    temp_only=0
}
[ ! -d "$workdir" ] && {
    echo "Parameter must be a working directory."; exit 1;
}

html="${workdir}/01-html"
rawtext="${workdir}/02-raw-text"
tokens="${workdir}/03-tokens"
tstats="${workdir}/04-text-stats"
topics="${workdir}/05-topic-models"

mkdir -vp ${html}
mkdir -vp ${rawtext}
mkdir -vp ${tokens}
mkdir -vp ${tstats}
mkdir -vp ${topics}

run_pfx="python3 -m bdatbx_scripts"
${run_pfx}.admin_test_library
${run_pfx}.parse_rss_feed -i "http://www.spiegel.de/index.rss" \
-o ${workdir}/rss-links.txt -l
echo "Parsed $( cat ${workdir}/rss-links.txt | wc -l ) article links."
${run_pfx}.download_website -i ${workdir}/rss-links.txt -o ${html}
${run_pfx}.extract_raw_text -i ${html} -o ${rawtext}
${run_pfx}.raw_text_preprocessing -i ${rawtext} -o ${tokens} \
-n nltk-data
${run_pfx}.text_statistics -i ${tokens} -o ${tstats}
${run_pfx}.generate_topic_model -i ${tokens} -o ${topics}

[ $temp_only == 1 ] && {
    rm -rf $workdir
    echo "Deleted $workdir"
}
