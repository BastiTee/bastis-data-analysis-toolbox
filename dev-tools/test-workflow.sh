#!/bin/bash

cd "$( dirname "$( dirname "$( readlink -f $0 )" )" )"
echo -e "@ $( pwd )\n"

rm -rf "_sanity" 2>&1 > /dev/null

tmpf=$( mktemp )

run_pfx="python3 -m bdatbx_scripts"
${run_pfx}.admin_test_library
${run_pfx}.parse_rss_feed -i "http://www.spiegel.de/index.rss" -l > ${tmpf}
${run_pfx}.download_raw_text -i ${tmpf} -f
${run_pfx}.raw_text_preprocessing -f
${run_pfx}.text_statistics -f
${run_pfx}.generate_topic_model -f

rm -f $tmpf
