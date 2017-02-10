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

mkdir -vp ${workdir}/raw-text
mkdir -vp ${workdir}/tokens
mkdir -vp ${workdir}/text-stats
mkdir -vp ${workdir}/topic-model

run_pfx="python3 -m bdatbx_scripts"
# ${run_pfx}.admin_test_library
${run_pfx}.parse_rss_feed -i "http://www.spiegel.de/index.rss" \
-o ${workdir}/rss-links.txt -l
echo "Parsed $( cat ${workdir}/rss-links.txt | wc -l ) article links."
${run_pfx}.download_raw_text -i ${workdir}/rss-links.txt -o ${workdir}/raw-text
${run_pfx}.raw_text_preprocessing -i ${workdir}/raw-text -o ${workdir}/tokens \
-n nltk-data
${run_pfx}.text_statistics -i ${workdir}/tokens -o ${workdir}/text-stats
${run_pfx}.generate_topic_model -i ${workdir}/tokens -o ${workdir}/topic-model

[ $temp_only == 1 ] && {
    rm -rf $workdir
    echo "Deleted $workdir"
}
